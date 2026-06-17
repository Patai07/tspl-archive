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

def deep_normalize_single(name):
    """Extra-aggressive normalize for a single string segment."""
    n = normalize(name)                          # existing normalize
    n = re.sub(r'[:/\-\(\)\[\].,;?]', '', n)    # strip punctuation
    n = re.sub(r'บน.*', '', n)                  # drop "บน..." suffix  
    n = re.sub(r'ใน.*', '', n)                  # drop "ใน..." suffix
    return n

def deep_normalize(name):
    """Extract and normalize all possible naming candidates from a folder/title name."""
    candidates = [name]
    
    # 1. Split by colon
    if ':' in name:
        candidates.extend(name.split(':'))
        
    # 2. Split by .jpg- or similar
    for ext in ['.jpg-', '.png-', '.jpeg-', ' - ']:
        for cand in list(candidates):
            if ext in cand:
                candidates.extend(cand.split(ext))
                
    # 3. Clean and normalize each candidate
    normalized_cands = []
    for cand in candidates:
        cand_dn = deep_normalize_single(cand)
        if cand_dn and cand_dn not in normalized_cands:
            normalized_cands.append(cand_dn)
    return normalized_cands

def fuzzy_score(title_dn_list, folder_dn_list):
    """Compare candidates of title to candidates of folder name, returning max score."""
    if not title_dn_list or not folder_dn_list: return 0.0
    
    max_score = 0.0
    for title_dn in title_dn_list:
        for folder_dn in folder_dn_list:
            score = _fuzzy_score_single(title_dn, folder_dn)
            if score > max_score:
                max_score = score
    return max_score

def _fuzzy_score_single(title_dn, folder_dn):
    # Check substring containment
    if title_dn in folder_dn or folder_dn in title_dn:
        shorter = min(len(title_dn), len(folder_dn))
        longer  = max(len(title_dn), len(folder_dn))
        return shorter / longer
    # LCS length using DP
    s1, s2 = title_dn, folder_dn
    dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    lcs_len = dp[len(s1)][len(s2)]
    return lcs_len / max(len(s1), len(s2))

TITLE_TO_FOLDER_MAP = {
    normalize('ใบไม้สามแฉกก้านคดกับกากบาทรูปใบกลาง'): normalize('ลายกระเบื้องวัดใหญ่ 3'),
    normalize('ใบไม้สามแฉกบนกระเบื้องโบราณ'): normalize('ลายกระเบื้องวัดใหญ่ 1'),
    normalize('ดอกจันกากบาทกลีบพัด'): normalize('ดาวสี่แฉกหลักไขว้ซ้อน'),
    normalize('ดอกจันกังหันเวียนสลับสี'): normalize('ลายกังหันดอกจันหมุนสลับสี'),
    normalize('ขิดดอกพิกุล'): normalize('ลายดอกแก้วแปดกลีบ'),
    normalize('แตงโม'): normalize('ลายแตงโม-ผ้า'),
    normalize('ครุฑปูนปั้น'): normalize('ครุฑ'),
    normalize('องค์มกรคายนาค'): normalize('มกร'),
    normalize('มังกรนูนต่ำ'): normalize('มังกร'),
    normalize('ขิดนาคและโคมเรขาคณิต'): normalize('ลายขิดนาค'),
    normalize('ม้า'): normalize('ม้า-ลายผ้า'),
    normalize('ขิดมกรและโคมเรขาคณิต'): normalize('ลายขิดมกร'),
    normalize('ขิดคชลักษณ์และโคมเรขาคณิต'): normalize('ลายขิดช้าง'),
    normalize('นกคุ้ม'): normalize('ลายผ้านกคุ้ม'),
    normalize('ขิดกนกสัตวลักษณ์เรขาคณิต'): normalize('ผ้าทอมือลายขิดนกยูง'),
    normalize('ขิดก้างปลาและโคมเรขาคณิต'): normalize('ลายขิดก้างปลา'),
    normalize('ช้าง'): normalize('ช้าง-ลายผ้า'),
    normalize('คลื่นและลายก้านขดบนเครื่องปั้นดินเผา'): normalize('เครื่องปั้นดินเผา'),
    normalize('แถบสามเหลี่ยมปะสลับสี'): normalize('ลายฟันปลาขอบหมอนไทดำ'),
    normalize('หน้าหมอนขิดไทพวน'): normalize('หมอนไทพวน'),
    normalize('สามเหลี่ยมฟันปลา'): normalize('ลายสามเหลี่ยม:ฟันปลา'),
    normalize('หน้าหมอนดอกแก้วไทพวน'): normalize('ลายดอกแก้ว'),
    normalize('ขิดสร้อยสา'): normalize('ลายสร้อยสา'),
    normalize('ขิดดอกในตารางสี่เหลี่ยม'): normalize('ผ้าทอขิดตารางสี่เหลี่ยมสลับลายขิดดอก'),
    normalize('ดาวเพดานไม้แกะสลักประดับกระจก'): normalize('ดาวเพดาน วัดใหญ่'),
    normalize('จั่วภควัมหน้าพรหม'): normalize('010หน้าบันลูกฟักหน้าพรหม '),
    normalize('เม็ดสร้อยสังวาลพระพุทธชินราช'): normalize('สังวาลพระพุทธชินราช'),
    # GEO-026: sheet title longer than Drive folder name
    normalize('ลายขูดขีดและลายกดประทับบนภาชนะดินเผา'): normalize('ลายขูดขีดและลายกดประทับ'),
    # SAC-030: sheet uses / but Drive uses :
    normalize('ลายจักร/พระอาทิตย์'): normalize('ลายจักร:พระอาทิตย์ '),
    # FAU-034: sheet has extra words
    normalize('ลายหงส์ในวงกลมคั่นเถาดอกไม้บนเครื่องถ้วยลายคราม'): normalize('ลายหงส์ในวงกลมบนเครื่องถ้วยลายคราม'),
    # FAU-043: Drive folder name has stray trailing )
    normalize('ลายลวดลายนกเกาะกิ่งไม้บนภาชนะแปดเหลี่ยม'): normalize('ลายลวดลายนกเกาะกิ่งไม้บนภาชนะแปดเหลี่ยม)'),
    # FAU-031: Drive uses different wording
    normalize('มังกรประดับสถาปัตยกรรมศาลเจ้า'): normalize('มังกรประดับวัดจีน ศาลเจ้าจีน'),
    # FAU-041: Drive has shorter name
    normalize('ไก่โต้งบนบานประตูไม้'): normalize('ไก่'),
    # FAU-032: Drive has shorter name
    normalize('เสือกำลังกัดกวาง'): normalize('เสือ'),
    # NAT-056: word order differs between Sheet and Drive
    normalize('ลายกลีบบัวบนภาชนะดินเผาสุโขทัย'): normalize('ภาชนะลายกลีบบัว'),
    # NAT-051: Sheet has กลางกระเบื้อง, Drive has prefix ลายกระเบื้องวัดใหญ่ 2:
    normalize('ลายดอกแปดกลีบกลางกระเบื้อง'): normalize('ลายกระเบื้องวัดใหญ่ 2: ลายกระเบื้องดอกแปดกลีบ'),
    # FAU-039: Drive has typo 'ปลาย' instead of 'ปลา'
    normalize('ลายกุ้ง ปู และปลา'): normalize('ปู กุ้ง ปลาย'),
    # Mappings from Haiku for missing 6 patterns
    normalize('ลายใบไม้ปลายแหลมบนกระปุกเขียนสี'): normalize('กระปุกวัดช้างรอบ'),
    normalize('ลายเถากระหนกช่องสี่เหลี่ยมบนฐานสถาปัตยกรรม'): normalize('ลายกรุยเชิงซุ้มเรือนธาตุ'),
    normalize('ภาพเล่าเรื่องวิถีชีวิตและสถาปัตยกรรมพื้นถิ่นในจิตรกรรมฝาผนังไทย'): normalize('เรือนพื้นถิ่น'),
    normalize('ลายพันธุ์พฤกษาก้านขดบนเครื่องถ้วยสุโขทัย'): normalize('วัดสระไข่น้ำ'),
    normalize('ลายกลีบบัวและก้านขดบนโถสุโขทัยมีฝาปิด'): normalize('กระปุกวัดช้างรอบ2'),
    normalize('ลายพรรณไม้เลื้อยในแปดเหลี่ยมบนเครื่องสังคโลก'): normalize('กระปุก วัดช้างรอบ2'),
}

def thumb_url(file_id, size='w1200'):
    return f"https://drive.google.com/thumbnail?id={file_id}&sz={size}"

def select_main_image(imgs):
    """
    เลือกรูป Main จาก list ของไฟล์ใน Drive folder
    Priority:
      1. ไฟล์ที่ชื่อ base name ว่า 'main' พอดี เช่น main.jpg, Main.PNG
      2. ไฟล์ที่ชื่อขึ้นต้นด้วย 'main' เช่น main_photo.jpg
      3. ไฟล์ที่ชื่อขึ้นต้นด้วยตัวเลขน้อยสุด เช่น 01_xxx.jpg, 1.jpg
      4. Fallback: ไฟล์แรกตาม alphabet (แจ้งเตือนว่าใช้ fallback)
    Returns (img_dict, confidence) where confidence = 'exact'|'prefix'|'numbered'|'fallback'
    """
    if not imgs:
        return None, None
    if len(imgs) == 1:
        return imgs[0], 'exact'

    img_exts = re.compile(r'\.(jpg|jpeg|png|webp|heic|heif|tif|tiff|svg)$', re.I)

    # Priority 1: base name == 'main'
    for img in imgs:
        base = img['name'].rsplit('.', 1)[0].lower() if '.' in img['name'] else img['name'].lower()
        if base == 'main':
            return img, 'exact'

    # Priority 2: ชื่อขึ้นต้นด้วย 'main'
    for img in imgs:
        if img['name'].lower().startswith('main'):
            return img, 'prefix'

    # Priority 3: ชื่อขึ้นต้นด้วยตัวเลข → เลือกที่มีเลขน้อยสุด
    numbered = []
    for img in imgs:
        m = re.match(r'^(\d+)', img['name'])
        if m:
            numbered.append((int(m.group(1)), img))
    if numbered:
        numbered.sort(key=lambda x: x[0])
        return numbered[0][1], 'numbered'

    # Priority 4: fallback — ตัวแรก alphabet
    return imgs[0], 'fallback'

# ─── Drive folder ID helpers ─────────────────────────────────────────────────

def build_id_map(pattern_map):
    """Build reverse lookup: folder_id → folder_info (same dict as pattern_map values)"""
    return {info['folder_id']: info for info in pattern_map.values()}

def resolve_folder(row, headers, pattern_map, id_map):
    """
    หา folder info สำหรับแถวนี้ ตาม 3-tier priority:
      1. Drive_Folder_ID (col W) — ID โดยตรง 100% แม่นยำ
      2. Drive Folder (col V)    — match ชื่อ normalized
      3. Title TH (col B)        — normalize + TITLE_TO_FOLDER_MAP
    Returns folder_info dict {'folder_name', 'folder_id', 'images'} or None
    """
    drive_id_col_idx = headers.index('Drive_Folder_ID') if 'Drive_Folder_ID' in headers else -1
    drive_col_idx    = headers.index('Drive Folder')    if 'Drive Folder'    in headers else -1

    # Priority 1: Direct ID lookup (column W)
    if drive_id_col_idx != -1 and len(row) > drive_id_col_idx:
        folder_id = row[drive_id_col_idx].strip()
        if folder_id and folder_id in id_map:
            return id_map[folder_id]

    # Priority 2: Drive Folder name (column V)
    drive_folder_val = row[drive_col_idx].strip() if drive_col_idx != -1 and len(row) > drive_col_idx else ''
    if drive_folder_val:
        norm = normalize(drive_folder_val)
        if norm in pattern_map:
            return pattern_map[norm]

    # Priority 3: Title TH with alias map (column B)
    title_th = row[1] if len(row) > 1 else ''
    norm = normalize(title_th)
    if norm in TITLE_TO_FOLDER_MAP:
        norm = TITLE_TO_FOLDER_MAP[norm]
    if norm in pattern_map:
        return pattern_map[norm]

    return None

# ─── Drive: build pattern map ────────────────────────────────────────────────

def list_pattern_folders(drive_svc):
    """Returns dict: normalized_name → {folder_name, folder_id, images:[...]}"""
    result = {}
    # รองรับ Shared Drive ด้วย supportsAllDrives + includeItemsFromAllDrives
    shared_opts = dict(supportsAllDrives=True, includeItemsFromAllDrives=True)

    cats = drive_svc.files().list(
        q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)", pageSize=100, **shared_opts
    ).execute().get('files', [])

    for cat in cats:
        token = None
        while True:
            resp = drive_svc.files().list(
                q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
                fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token, **shared_opts
            ).execute()
            for p in resp.get('files', []):
                # ── ดึงรูปทุกใบด้วย pagination (แก้บั๊ก pageSize=20 ไม่ครบ) ──
                all_imgs = []
                img_token = None
                while True:
                    img_resp = drive_svc.files().list(
                        q=f"'{p['id']}' in parents and trashed=false and mimeType contains 'image/'",
                        fields="nextPageToken,files(id,name,mimeType,webViewLink,webContentLink)",
                        orderBy="name", pageSize=100, pageToken=img_token, **shared_opts
                    ).execute()
                    all_imgs.extend(img_resp.get('files', []))
                    img_token = img_resp.get('nextPageToken')
                    if not img_token:
                        break
                norm = normalize(p['name'])
                result[norm] = {'folder_name': p['name'], 'folder_id': p['id'], 'images': all_imgs}
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

    # Batch restore col O:U (15-21)
    batch_data = []
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 19:
            ex1 = row[19] if len(row) > 19 else ''
            ex2 = row[20] if len(row) > 20 else ''
            batch_data.append({
                'range': f'O{i}:U{i}',
                'values': [[row[14], row[15], row[16], row[17], row[18], ex1, ex2]]
            })
    if batch_data:
        ws.batch_update(batch_data)
    print(f"✅ Rollback สำเร็จ ({len(batch_data)} แถว) จาก Backup: {latest}", flush=True)
    print(f"🕐 Backup นี้บันทึกเมื่อ: {backup.get('timestamp','?')}", flush=True)

# ─── CMD: link ───────────────────────────────────────────────────────────────

def cmd_link():
    print("🔗 เริ่มซิงค์และอัปเดตเส้นทางรูปภาพทั้งหมด (O:U) → Sheet 2 (tspl_database)...", flush=True)
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')

    backup_path = save_backup(ws)
    print(f"💾 Backup บันทึกแล้ว: {backup_path}", flush=True)

    print("📂 กำลังตรวจสอบไฟล์รูปภาพในเครื่อง (assets/images/database)...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)
    id_map = build_id_map(pattern_map)

    rows = ws.get_all_values()
    headers = rows[0]
    data_rows = []
    for i, row in enumerate(rows[1:], start=2):
        if not row or not row[0].strip() or row[0].strip().startswith('#'):
            continue
        data_rows.append({'row_idx': i, 'data': row})

    # Group by category folder name
    categories = ['01_Nature', '02_Fauna', '03_Geometric', '04_Sacred']
    grouped = {cat: [] for cat in categories}
    for item in data_rows:
        cat_val = item['data'][3] if len(item['data']) > 3 else ''
        folder = cat_folder_name(cat_val)
        if folder in grouped: grouped[folder].append(item)
        else: grouped['01_Nature'].append(item) # Default

    matched = 0; no_match = 0
    batch_data = []

    for cat_folder in categories:
        items = grouped[cat_folder]
        if not items: continue
        
        cat_display = cat_folder.split('_')[-1]
        print(f"\n📁 หมวด {cat_display}: กำลังตรวจสอบ {len(items)} รายการ...", flush=True)
        
        for item in items:
            i = item['row_idx']
            row = item['data']
            sid = row[0].strip()
            title_th = row[1] if len(row) > 1 else ''
            cat = row[3] if len(row) > 3 else ''
            folder_info = resolve_folder(row, headers, pattern_map, id_map)
            local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)
            
            def find_slot(prefix, subfolder=''):
                tdir = os.path.join(local_dir, subfolder) if subfolder else local_dir
                if not os.path.exists(tdir): return ''
                for f in os.listdir(tdir):
                    # รองรับไฟล์หลากหลายนามสกุล: jpg, jpeg, png, svg, webp, heic, heif, tif, tiff
                    if f.lower().startswith(prefix.lower() + '.') and re.search(r'\.(jpg|jpeg|png|svg|webp|heic|heif|tif|tiff)$', f, re.I):
                        rel = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid, subfolder, f) if subfolder else os.path.join(ASSETS_BASE, cat_folder_name(cat), sid, f)
                        return rel.replace('\\', '/')
                return ''

            # หาพาธจริงที่อยู่ในเครื่อง
            img_main   = find_slot('main')
            img_vec    = find_slot('vector', 'vectors')
            img_ctx    = find_slot('context')
            img_mid    = find_slot('img_mid')
            img_det    = find_slot('img_detail')
            img_extra1 = find_slot('img_extra1')
            img_extra2 = find_slot('img_extra2')

            # Fallback
            old_main = row[14].strip() if len(row) > 14 else ''
            old_vec  = row[15].strip() if len(row) > 15 else ''
            old_ctx  = row[16].strip() if len(row) > 16 else ''
            old_mid  = row[17].strip() if len(row) > 17 else ''
            old_det  = row[18].strip() if len(row) > 18 else ''
            old_ex1  = row[19].strip() if len(row) > 19 else ''
            old_ex2  = row[20].strip() if len(row) > 20 else ''

            if not img_main:   img_main   = old_main or (f"{ASSETS_BASE}/{cat_folder_name(cat)}/{sid}/main.jpg" if folder_info else '')
            if not img_vec:    img_vec    = old_vec
            if not img_ctx:    img_ctx    = old_ctx
            if not img_mid:    img_mid    = old_mid
            if not img_det:    img_det    = old_det
            if not img_extra1: img_extra1 = old_ex1
            if not img_extra2: img_extra2 = old_ex2

            if folder_info or os.path.exists(local_dir):
                matched += 1
            else:
                no_match += 1

            batch_data.append({
                'range': f'O{i}:U{i}',
                'values': [[img_main, img_vec, img_ctx, img_mid, img_det, img_extra1, img_extra2]]
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
    print("📥 เริ่มดาวน์โหลดรูปภาพ Main จาก Drive → assets/images/database/...", flush=True)
    print("   (โหลดแค่รูปหลัก 1 ใบต่อลวดลาย — ใช้ Smart Selection)", flush=True)
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')

    print("📂 กำลังสแกนโครงสร้าง Drive...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)
    id_map = build_id_map(pattern_map)

    rows = ws.get_all_values()
    headers = rows[0]
    downloaded = 0; skipped = 0; errors = 0; fallbacks = 0

    for row in rows[1:]:
        if not row or not row[0].strip() or row[0].strip().startswith('#'):
            continue
        sid      = row[0].lstrip('#').strip()
        title_th = row[1] if len(row) > 1 else ''
        cat      = row[3] if len(row) > 3 else 'Nature & Botany'
        local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)

        folder_info = resolve_folder(row, headers, pattern_map, id_map)
        if not folder_info:
            print(f"⚠️  ข้าม (ไม่พบโฟลเดอร์): {sid} — {title_th}", flush=True)
            continue

        imgs = folder_info['images']
        if not imgs:
            print(f"⚠️  ข้าม (โฟลเดอร์ว่าง): {sid}", flush=True)
            continue

        # ── Smart Main Selection ──────────────────────────────────────────────
        main_img, confidence = select_main_image(imgs)
        if not main_img:
            continue

        os.makedirs(local_dir, exist_ok=True)

        ext = main_img['name'].rsplit('.', 1)[-1].lower() if '.' in main_img['name'] else 'jpg'
        local_path = os.path.join(local_dir, f"main.{ext}")

        # ข้ามถ้ามี main.* อยู่แล้ว
        existing_main = [f for f in os.listdir(local_dir) if f.lower().startswith('main.')]
        if existing_main:
            skipped += 1
            continue

        # แจ้งเตือนถ้าใช้ fallback (ไม่มีไฟล์ชื่อ main)
        if confidence == 'fallback':
            fallbacks += 1
            print(f"⚠️  [{confidence}] {sid}: ไม่พบไฟล์ชื่อ 'main' — ใช้ '{main_img['name']}' แทน ({len(imgs)} ไฟล์ใน folder)", flush=True)
        elif confidence == 'numbered':
            print(f"🔢 [{confidence}] {sid}: เลือก '{main_img['name']}' (ตัวเลขน้อยสุดใน {len(imgs)} ไฟล์)", flush=True)

        try:
            req = drive_svc.files().get_media(fileId=main_img['id'], supportsAllDrives=True)
            buf = io.BytesIO()
            dl  = MediaIoBaseDownload(buf, req)
            done = False
            while not done: _, done = dl.next_chunk()
            data = buf.getvalue()
            if not data:
                raise ValueError("ได้รับไฟล์ว่าง (0 bytes)")
            with open(local_path, 'wb') as f: f.write(data)
            print(f"✅ {local_path} [{confidence}] ({len(data):,} bytes)", flush=True)
            downloaded += 1
            time.sleep(0.1)
        except Exception as e:
            err_str = str(e)
            if '403' in err_str:
                print(f"❌ {main_img['name']}: Permission Denied (403) — ตรวจสอบสิทธิ์ Service Account", flush=True)
            elif '404' in err_str:
                print(f"❌ {main_img['name']}: ไม่พบไฟล์ (404)", flush=True)
            else:
                print(f"❌ {main_img['name']}: {err_str[:200]}", flush=True)
            errors += 1

    print(f"\n📊 ดาวน์โหลด {downloaded} | ข้าม {skipped} | Error {errors} | Fallback {fallbacks}", flush=True)
    if fallbacks > 0:
        print(f"💡 แนะนำ: ให้ทีมตั้งชื่อรูปหลักว่า 'main.jpg' ใน Drive folder เพื่อให้ระบบเลือกถูกต้อง 100%", flush=True)
    print("✅ เสร็จสิ้น!", flush=True)

# ─── CMD: check ──────────────────────────────────────────────────────────────


def cmd_check():
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')
    pattern_map = list_pattern_folders(drive_svc)
    id_map = build_id_map(pattern_map)
    rows = ws.get_all_values()
    headers = rows[0]
    results = []
    for row in rows[1:]:
        if not row or not row[0].strip() or row[0].strip().startswith('#'): continue
        sid      = row[0].strip()
        title_th = row[1] if len(row) > 1 else ''
        cat      = row[3] if len(row) > 3 else ''
        local_dir = os.path.join(ASSETS_BASE, cat_folder_name(cat), sid)
        local_imgs = [f for f in os.listdir(local_dir) if re.search(r'\.(jpg|jpeg|png|webp|heic|heif|tif|tiff)$', f, re.I)] if os.path.exists(local_dir) else []
        folder_info = resolve_folder(row, headers, pattern_map, id_map)
        results.append({
            'symbol_id':        sid,
            'title_th':         title_th,
            'in_drive':         folder_info is not None,
            'drive_images':     len(folder_info['images']) if folder_info else 0,
            'local_downloaded': len(local_imgs),
        })
    print(json.dumps(results, ensure_ascii=False), flush=True)

# ─── CMD: map_ids ───────────────────────────────────────────────────────────

def cmd_map_ids():
    """
    One-time setup: สแกน Drive → เขียน Folder ID ลงคอลัมน์ W (Drive_Folder_ID)
    - Row ที่ match ได้ด้วยชื่อ: เขียน ID อัตโนมัติ
    - Row ที่ไม่ match: แสดง fuzzy suggestions + Drive URL สำหรับ paste เอง
    """
    print("\U0001f5fa\ufe0f  เริ่ม Map Drive Folder IDs ลง Sheet (tspl_database)...", flush=True)
    drive_svc, gc = get_services()
    sh = gc.open_by_key(PROD_SHEET_ID)
    ws = sh.worksheet('tspl_database')

    print("\U0001f4c2 กำลังสแกนโครงสร้าง Drive...", flush=True)
    pattern_map = list_pattern_folders(drive_svc)
    id_map      = build_id_map(pattern_map)
    print(f"   พบ {len(pattern_map)} โฟลเดอร์ใน Drive", flush=True)

    rows    = ws.get_all_values()
    headers = rows[0]

    # สร้างคอลัมน์ Drive_Folder_ID (W) ถ้ายังไม่มี
    drive_id_col_idx = headers.index('Drive_Folder_ID') if 'Drive_Folder_ID' in headers else -1
    if drive_id_col_idx == -1:
        ws.update_cell(1, 23, 'Drive_Folder_ID')
        drive_id_col_idx = 22
        print("➕ เพิ่มคอลัมน์ 'Drive_Folder_ID' ที่ Column W (col 23) แล้ว", flush=True)
        rows    = ws.get_all_values()
        headers = rows[0]

    # Build all folder list for fuzzy suggestion
    all_folders = [(info['folder_name'], info['folder_id'], len(info['images']))
                   for info in pattern_map.values()]

    auto_mapped = 0; already_mapped = 0; not_found_rows = []
    batch_data  = []

    for i, row in enumerate(rows[1:], start=2):
        if not row or not row[0].strip() or row[0].strip().startswith('#'):
            continue
        sid      = row[0].strip()
        title_th = row[1] if len(row) > 1 else ''

        # ถ้ามี ID อยู่แล้ว ข้าม
        existing_id = row[drive_id_col_idx].strip() if len(row) > drive_id_col_idx else ''
        if existing_id:
            already_mapped += 1
            continue

        folder_info = resolve_folder(row, headers, pattern_map, id_map)
        if folder_info:
            batch_data.append({'range': f'W{i}', 'values': [[folder_info['folder_id']]]})
            auto_mapped += 1
            print(f"✅ {sid}: '{folder_info['folder_name']}' (Exact/Map Match) ({len(folder_info['images'])} รูป)", flush=True)
        else:
            # Fuzzy match scoring
            title_dn = deep_normalize(title_th)
            best_score = 0.0
            best_info = None
            for info in pattern_map.values():
                folder_dn = deep_normalize(info['folder_name'])
                score = fuzzy_score(title_dn, folder_dn)
                if score > best_score:
                    best_score = score
                    best_info = info
            
            AUTO_THRESHOLD = 0.65
            if best_score >= AUTO_THRESHOLD and best_info:
                batch_data.append({'range': f'W{i}', 'values': [[best_info['folder_id']]]})
                auto_mapped += 1
                marker = "✅ AUTO" if best_score >= 0.85 else "⚠️ AUTO"
                print(f"{marker} [{best_score:.0%}] {sid}: '{best_info['folder_name']}' ({len(best_info['images'])} รูป)", flush=True)
            else:
                # If there's a best suggestion even if low confidence, offer it
                suggestions = []
                if best_info:
                    suggestions.append((best_info['folder_name'], best_info['folder_id'], len(best_info['images']), best_score))
                
                # Also fallback to basic substring checks to provide other suggestions if any
                title_norm = normalize(title_th)
                for fname, fid, fcount in all_folders:
                    if best_info and fid == best_info['folder_id']:
                        continue
                    fname_norm = normalize(fname)
                    if title_norm and (title_norm in fname_norm or fname_norm in title_norm):
                        suggestions.append((fname, fid, fcount, 0.5)) # default score for simple overlap
                
                not_found_rows.append((i, sid, title_th, suggestions, best_score))

    if batch_data:
        print(f"\n⏳ เขียน {len(batch_data)} Folder IDs ลง Sheet...", flush=True)
        ws.batch_update(batch_data)

    print(f"\n📊 Auto-mapped: {auto_mapped} | Already mapped: {already_mapped} | ยังไม่ match: {len(not_found_rows)}", flush=True)

    if not_found_rows:
        print("\n⚠️  รายการที่ต้อง paste Folder ID เอง (ความมั่นใจต่ำกว่า 65%):", flush=True)
        print("   เปิด Drive → เข้า folder → copy ID จาก URL → paste ลงคอลัมน์ W ใน Sheet", flush=True)
        print("-" * 70, flush=True)
        for _, sid, title, suggestions, best_score in not_found_rows:
            print(f"\n  📌 {sid}: {title} (ความเข้ากันได้สูงสุด: {best_score:.0%})", flush=True)
            if suggestions:
                print(f"     💡 Folder ที่น่าจะใช่:", flush=True)
                for item in suggestions[:3]:
                    fname, fid, fcount = item[0], item[1], item[2]
                    score_str = f" [Score: {item[3]:.0%}]" if len(item) > 3 else ""
                    print(f"     → '{fname}'{score_str} ({fcount} รูป)", flush=True)
                    print(f"       ID : {fid}", flush=True)
                    print(f"       URL: https://drive.google.com/drive/folders/{fid}", flush=True)
            else:
                print(f"     ❓ ไม่พบ folder ที่มีชื่อใกล้เคียงใน Drive", flush=True)
        print("-" * 70, flush=True)
        print(f"💡 paste Folder ID ลงคอลัมน์ W ใน Sheet สำหรับ {len(not_found_rows)} รายการด้านบน", flush=True)

    print("✅ เสร็จสิ้น!", flush=True)

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
    headers = rows[0]
    drive_col_idx = headers.index('Drive Folder') if 'Drive Folder' in headers else -1

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
        drive_folder_val = row[drive_col_idx].strip() if drive_col_idx != -1 and len(row) > drive_col_idx else ''
        if drive_folder_val:
            norm = normalize(drive_folder_val)
        else:
            norm = normalize(title_th)
            if norm in TITLE_TO_FOLDER_MAP:
                norm = TITLE_TO_FOLDER_MAP[norm]

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
    elif cmd == 'map_ids':  cmd_map_ids()
    else: print(f"Unknown command: {cmd}. Use: link | download | check | rollback | confirm | map_ids")
