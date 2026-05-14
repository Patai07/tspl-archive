"""
asset_manager.py — Drive Asset Manager
เชื่อมโยง Google Drive Folders กับ Sheet 2 (Production)
Commands: link | download | check | rollback
"""
import json, os, re, time, io, sys
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread

with open('config.json') as f:
    config = json.load(f)

PROD_SHEET_ID    = config['DB_SOURCE_SPREADSHEET_ID']
STAGING_SHEET_ID = config['SPREADSHEET_ID']   # Sheet 1 — staging
DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
BACKUP_DIR       = 'tools_web/backups'
ASSETS_BASE      = 'assets/images/database'
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_services():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds), gspread.authorize(creds)

def normalize(name):
    """Normalize pattern folder/title name for fuzzy matching."""
    n = re.sub(r'^\d+', '', name.strip())            # Remove ANY leading digits unconditionally
    n = re.sub(r'^[-.\s]+', '', n)                   # Remove dangling punctuation/spaces
    n = re.sub(r'^ลาย', '', n)                       # Remove leading ลาย
    n = re.sub(r'กระหนก', 'กนก', n)                    # Normalize spelling variations
    n = re.sub(r'\s*\(.*?\)', '', n)                 # Remove (English subtitle)
    return re.sub(r'\s+', '', n).lower()

def thumb_url(file_id, size='w1200'):
    return f"https://drive.google.com/thumbnail?id={file_id}&sz={size}"

# ─── Drive: build pattern map ────────────────────────────────────────────────

def list_pattern_folders(drive_svc):
    """Returns dict: normalized_name → {folder_name, folder_id, images:[...]}"""
    result = {}
    cats = drive_svc.files().list(
        q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)", pageSize=10
    ).execute().get('files', [])

    for cat in cats:
        token = None
        while True:
            resp = drive_svc.files().list(
                q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
                fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token
            ).execute()
            for p in resp.get('files', []):
                imgs = drive_svc.files().list(
                    q=f"'{p['id']}' in parents and trashed=false and mimeType contains 'image/'",
                    fields="files(id,name,mimeType,webViewLink)",
                    orderBy="name", pageSize=20
                ).execute().get('files', [])
                norm = normalize(p['name'])
                result[norm] = {'folder_name': p['name'], 'folder_id': p['id'], 'images': imgs}
            token = resp.get('nextPageToken')
            if not token: break
    return result

# ─── Backup / Rollback ───────────────────────────────────────────────────────

def save_backup(ws):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rows = ws.get_all_values()
    path = f"{BACKUP_DIR}/asset_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'rows': rows}, f, ensure_ascii=False, indent=2)
    return path

def cmd_rollback():
    if not os.path.exists(BACKUP_DIR):
        print("❌ ไม่พบโฟลเดอร์ Backup", flush=True); return
    backups = sorted([x for x in os.listdir(BACKUP_DIR) if x.startswith('asset_backup_')], reverse=True)
    if not backups:
        print("❌ ไม่พบไฟล์ Backup", flush=True); return

    latest = backups[0]
    print(f"↩️  กำลัง Rollback จาก: {latest}", flush=True)
    with open(os.path.join(BACKUP_DIR, latest), encoding='utf-8') as f:
        backup = json.load(f)

    _, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')
    rows = backup['rows']

    # Batch restore col O:S (15-19)
    batch_data = []
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 19:
            batch_data.append({
                'range': f'O{i}:S{i}',
                'values': [[row[14], row[15], row[16], row[17], row[18]]]
            })
    if batch_data:
        ws.batch_update(batch_data)
    print(f"✅ Rollback สำเร็จ ({len(batch_data)} แถว) จาก Backup: {latest}", flush=True)
    print(f"🕐 Backup นี้บันทึกเมื่อ: {backup.get('timestamp','?')}", flush=True)

# ─── CMD: link ───────────────────────────────────────────────────────────────

def cmd_link():
    print("🔗 เริ่มซิงค์และอัปเดตเส้นทางรูปภาพทั้งหมด (O:S) → Sheet 2 (tspl_database)...", flush=True)
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')

    backup_path = save_backup(ws)
    print(f"💾 Backup บันทึกแล้ว: {backup_path}", flush=True)

    print("📂 กำลังตรวจสอบไฟล์รูปภาพในเครื่อง (assets/images/database)...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)
    
    rows = ws.get_all_values()
    matched = 0; no_match = 0
    batch_data = []

    for i, row in enumerate(rows[1:], start=2):
        if not row or not row[0].strip() or row[0].strip().startswith('#'):
            continue
        sid = row[0].strip()
        title_th = row[1] if len(row) > 1 else ''
        cat = row[3] if len(row) > 3 else ''
        norm = normalize(title_th)

        local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)
        
        def find_slot(prefix, subfolder=''):
            tdir = os.path.join(local_dir, subfolder) if subfolder else local_dir
            if not os.path.exists(tdir): return ''
            for f in os.listdir(tdir):
                if f.lower().startswith(prefix.lower() + '.') and re.search(r'\.(jpg|jpeg|png|svg)$', f, re.I):
                    rel = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid, subfolder, f) if subfolder else os.path.join(ASSETS_BASE, cat_folder_name(cat), sid, f)
                    return rel.replace('\\', '/')
            return ''

        # หาพาธจริงที่อยู่ในเครื่อง
        img_main = find_slot('main')
        img_vec  = find_slot('vector', 'vectors')
        img_ctx  = find_slot('context')
        img_mid  = find_slot('img_mid')
        img_det  = find_slot('img_detail')

        # Fallback กรณีที่ยังไม่ได้ดาวน์โหลด แต่มีข้อมูลใน row เดิมอยู่แล้ว
        old_main = row[14].strip() if len(row) > 14 else ''
        old_vec  = row[15].strip() if len(row) > 15 else ''
        old_ctx  = row[16].strip() if len(row) > 16 else ''
        old_mid  = row[17].strip() if len(row) > 17 else ''
        old_det  = row[18].strip() if len(row) > 18 else ''

        if not img_main: img_main = old_main or (f"{ASSETS_BASE}/{cat_folder_name(cat)}/{sid}/main.jpg" if norm in pattern_map else '')
        if not img_vec:  img_vec  = old_vec
        if not img_ctx:  img_ctx  = old_ctx
        if not img_mid:  img_mid  = old_mid
        if not img_det:  img_det  = old_det

        # ถ้าพบใน Drive หรือมีโฟลเดอร์ในเครื่อง ให้นับว่า match เพื่อรายงานผล
        if norm in pattern_map or os.path.exists(local_dir):
            matched += 1
            print(f"✅ {sid} — {title_th} (Main: {img_main.rsplit('/',1)[-1].upper() if img_main else 'NONE'})", flush=True)
        else:
            no_match += 1
            print(f"⚠️  ไม่พบข้อมูล: {sid} — {title_th}", flush=True)

        batch_data.append({
            'range': f'O{i}:S{i}',
            'values': [[img_main, img_vec, img_ctx, img_mid, img_det]]
        })

    print(f"\n📊 เตรียมอัปเดตข้อมูล {len(batch_data)} แถว...", flush=True)
    if batch_data:
        ws.batch_update(batch_data)
    print(f"🎉 อัปเดตเส้นทางรูปภาพสำเร็จ! (พบไฟล์/โฟลเดอร์ {matched} ลาย | ไม่พบ {no_match} ลาย)", flush=True)
    print("✅ เสร็จสิ้น! สามารถกด Deploy ขึ้น Vercel ได้เลยครับ", flush=True)

# ─── CMD: download ───────────────────────────────────────────────────────────

def cat_folder_name(cat):
    if 'Fauna' in cat:     return '02_Fauna'
    if 'Geometric' in cat: return '03_Geometric'
    if 'Sacred' in cat:    return '04_Sacred'
    return '01_Nature'

def cmd_download():
    print("📥 เริ่มดาวน์โหลดรูปภาพจาก Drive → assets/images/database/...", flush=True)
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')

    print("📂 กำลังสแกนโครงสร้าง Drive...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)

    rows = ws.get_all_values()
    downloaded = 0; skipped = 0; errors = 0

    IMG_SLOTS = ['main', 'img_mid', 'img_detail', 'img_extra1', 'img_extra2']

    for row in rows[1:]:
        if not row or not row[0].strip() or row[0].strip().startswith('#'):
            continue
        sid      = row[0].lstrip('#').strip()
        title_th = row[1] if len(row) > 1 else ''
        cat      = row[3] if len(row) > 3 else 'Nature & Botany'
        norm     = normalize(title_th)
        local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)

        if norm not in pattern_map:
            print(f"⚠️  ข้าม (ไม่พบโฟลเดอร์): {sid} — {title_th}", flush=True)
            continue

        imgs = pattern_map[norm]['images']
        if not imgs:
            print(f"⚠️  ข้าม (โฟลเดอร์ว่าง): {sid}", flush=True)
            continue

        os.makedirs(local_dir, exist_ok=True)

        for j, img in enumerate(imgs[:5]):
            ext = img['name'].rsplit('.', 1)[-1].lower() if '.' in img['name'] else 'jpg'
            local_path = os.path.join(local_dir, f"{IMG_SLOTS[j]}.{ext}")
            if os.path.exists(local_path):
                skipped += 1; continue
            try:
                req = drive_svc.files().get_media(fileId=img['id'])
                buf = io.BytesIO()
                dl  = MediaIoBaseDownload(buf, req)
                done = False
                while not done: _, done = dl.next_chunk()
                with open(local_path, 'wb') as f: f.write(buf.getvalue())
                print(f"✅ {local_path}", flush=True)
                downloaded += 1
                time.sleep(0.15)
            except Exception as e:
                print(f"❌ {img['name']}: {e}", flush=True)
                errors += 1

    print(f"\n📊 ดาวน์โหลด {downloaded} | ข้าม {skipped} | Error {errors}", flush=True)
    print("✅ เสร็จสิ้น!", flush=True)

# ─── CMD: check ──────────────────────────────────────────────────────────────

def cmd_check():
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')
    pattern_map = list_pattern_folders(drive_svc)
    rows = ws.get_all_values()
    results = []
    for row in rows[1:]:
        if not row or not row[0].strip() or row[0].strip().startswith('#'): continue
        sid      = row[0].strip()
        title_th = row[1] if len(row) > 1 else ''
        cat      = row[3] if len(row) > 3 else ''
        norm     = normalize(title_th)
        local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)
        local_imgs = [f for f in os.listdir(local_dir) if re.search(r'\.(jpg|jpeg|png)$', f, re.I)] if os.path.exists(local_dir) else []
        results.append({
            'symbol_id':        sid,
            'title_th':         title_th,
            'in_drive':         norm in pattern_map,
            'drive_images':     len(pattern_map[norm]['images']) if norm in pattern_map else 0,
            'local_downloaded': len(local_imgs),
        })
    print(json.dumps(results, ensure_ascii=False), flush=True)

# ─── CMD: confirm_sheet1 ─────────────────────────────────────────────────────

def cmd_confirm_sheet1():
    """
    ใช้โฟลเดอร์ Drive เป็น 'ฐานข้อมูลจริง'
    จับคู่กับแต่ละแถวใน Sheet 1 แล้วเติมคอลัมน์ Drive_Confirmed (Col 21)
    """
    print("🔎 เริ่มจับคู่ Drive Folders กับ Sheet 1...", flush=True)
    drive_svc, gc = get_services()

    # 1. สร้างแผนที่จาก Drive (master)
    print("📂 กำลังสแกนโครงสร้างโฟล์เดอร์ Drive...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)
    print(f"   พบ {len(pattern_map)} โฟล์เดอร์ลายใน Drive", flush=True)

    # 2. อ่าน Sheet 1
    sh1 = gc.open_by_key(STAGING_SHEET_ID)
    ws1 = sh1.get_worksheet(0)   # 'Sheet1' tab
    rows = ws1.get_all_values()

    if not rows:
        print("❌ ไม่พบข้อมูลใน Sheet 1", flush=True); return

    # 3. ตรวจว่ามีคอลัมน์ Drive_Confirmed หรือยัง
    header = rows[0]
    if 'Drive_Confirmed' not in header:
        # เพิ่ม header ในคอลัมน์ที่ 21
        ws1.update_cell(1, 21, 'Drive_Confirmed')
        print("➕ เพิ่มคอลัมน์ 'Drive_Confirmed' แล้ว", flush=True)
    col_idx = 21  # col U

    # 4. จับคู่และเก็บ batch
    confirmed = 0; not_found = 0
    batch_data = []

    for i, row in enumerate(rows[1:], start=2):
        if not row or not row[0].strip():
            continue

        sid      = row[0].strip()
        title_th = row[1] if len(row) > 1 else ''
        norm     = normalize(title_th)

        if norm in pattern_map:
            folder   = pattern_map[norm]
            img_cnt  = len(folder['images'])
            status   = f"✅ Drive Match ({img_cnt} รูป) [{folder['folder_name']}]"
            confirmed += 1
        else:
            status   = f"⚠️ ไม่พบโฟล์เดอร์ใน Drive"
            not_found += 1

        batch_data.append({'range': f'U{i}', 'values': [[status]]})
        print(f"  {status[:50]} — {sid} {title_th[:20]}", flush=True)

    # 5. เขียนลง Sheet 1 ทีเดียว
    if batch_data:
        print(f"⏳ เขียน {len(batch_data)} แถวลง Sheet 1...", flush=True)
        ws1.batch_update(batch_data)

    print(f"\n📊 สรุป: Drive Match {confirmed} ลาย | ไม่พบโฟล์เดอร์ {not_found} ลาย", flush=True)
    print("✅ เสร็จสิ้น! เช็คคอลัมน์ 'Drive_Confirmed' ใน Sheet 1 ได้เลยครับ", flush=True)

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if   cmd == 'link':     cmd_link()
    elif cmd == 'download': cmd_download()
    elif cmd == 'check':    cmd_check()
    elif cmd == 'rollback': cmd_rollback()
    elif cmd == 'confirm':  cmd_confirm_sheet1()
    else: print(f"Unknown command: {cmd}. Use: link | download | check | rollback | confirm")
