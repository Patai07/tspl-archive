"""
line_sync.py — LINE Auto-Upload Drive Sync
==========================================
อ่าน 2 โฟลเดอร์ใน Google Drive (ภาพ + เอกสาร) ที่ LINE auto-upload
จับคู่ไฟล์ตาม timestamp prefix ที่ LINE ใส่มา
แล้ว sync directory listing เข้า Google Sheet

ชื่อไฟล์ที่ LINE ใส่มาจะเป็นแบบ:
  YYYY_MMDD_HHMMSS_mmm_XXXXXXX_ชื่อไฟล์จริง.ext

Config ใน config.json:
  LINE_IMAGE_FOLDER_ID   - Folder ID ของโฟลเดอร์ภาพจาก LINE
  LINE_DOC_FOLDER_ID     - Folder ID ของโฟลเดอร์เอกสารจาก LINE
  LINE_SYNC_SHEET_ID     - Spreadsheet ID สำหรับ sync (ใช้ SPREADSHEET_ID ตัวเดิมได้)
  LINE_SYNC_SHEET_TAB    - ชื่อ tab ใน Sheet (default: "LINE_Sync")
"""

import json
import re
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
import anthropic

# ─── 1. CONFIG ────────────────────────────────────────────────────────────────
with open('config.json', 'r') as f:
    config = json.load(f)

SERVICE_ACCOUNT_FILE = 'service-account.json'
ANTHROPIC_API_KEY    = config.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL         = "claude-haiku-4-5-20251001"

# โฟลเดอร์ทั้งสองจาก LINE (ต้อง set ใน config.json)
IMAGE_FOLDER_ID = config.get('LINE_IMAGE_FOLDER_ID', '')
DOC_FOLDER_ID   = config.get('LINE_DOC_FOLDER_ID', '')

SPREADSHEET_ID  = config.get('SPREADSHEET_ID')
SHEET_TAB       = config.get('LINE_SYNC_SHEET_TAB', 'LINE_Sync')

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
]

# ─── 2. TIMESTAMP PARSER ──────────────────────────────────────────────────────
# LINE ใส่ชื่อไฟล์ในรูปแบบ: YYYY_MMDD_HHMMSS_mmm_RANDOM_ชื่อ.ext
LINE_TS_PATTERN = re.compile(
    r'^(\d{4})_(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_(\d{3})_(\d+)_(.+)$'
)

def parse_line_filename(name: str) -> dict:
    """แยก timestamp และชื่อจริงออกจากชื่อไฟล์ที่ LINE ตั้ง"""
    stem = name.rsplit('.', 1)[0]  # ตัด extension
    ext  = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    m    = LINE_TS_PATTERN.match(stem)
    if m:
        year, mon, day, hh, mm, ss, ms, rand, real_name = m.groups()
        ts_str = f"{year}-{mon}-{day} {hh}:{mm}:{ss}.{ms}"
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            ts = None
        return {
            'timestamp': ts,
            'ts_str': ts_str,
            'ts_key': f"{year}{mon}{day}{hh}{mm}{ss}{ms}",  # key สำหรับจับคู่
            'random_id': rand,
            'real_name': real_name,
            'extension': ext,
            'original_name': name,
            'parsed': True,
        }
    return {
        'timestamp': None,
        'ts_str': '',
        'ts_key': '',
        'random_id': '',
        'real_name': stem,
        'extension': ext,
        'original_name': name,
        'parsed': False,
    }

# ─── 3. DRIVE HELPERS ─────────────────────────────────────────────────────────
def list_folder(drive_service, folder_id: str, label: str) -> list:
    """ดึง list ไฟล์ทั้งหมดในโฟลเดอร์ (รองรับ pagination)"""
    if not folder_id:
        print(f"⚠️  ยังไม่ได้ตั้งค่า folder ID สำหรับ {label} — ข้ามโฟลเดอร์นี้")
        return []
    results = []
    page_token = None
    query = f"'{folder_id}' in parents and trashed = false"
    fields = "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)"
    while True:
        resp = drive_service.files().list(
            q=query, fields=fields, pageSize=1000,
            pageToken=page_token
        ).execute()
        results.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    print(f"📂 {label}: พบ {len(results)} ไฟล์")
    return results

def enrich_file(f: dict, folder_label: str) -> dict:
    """เพิ่มข้อมูล parsed จากชื่อไฟล์"""
    parsed = parse_line_filename(f['name'])
    return {**f, **parsed, 'folder_type': folder_label}

# ─── 4. CLAUDE MATCHER (optional) ────────────────────────────────────────────
def haiku_describe_file(name: str, mime: str) -> str:
    """ให้ Claude Haiku สรุปประเภทไฟล์อย่างสั้น (ใช้เมื่อ parse ชื่อไม่ได้)"""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=80,
            messages=[{
                "role": "user",
                "content": (
                    f"ไฟล์ชื่อ '{name}' (mime: {mime}) "
                    "คืออะไร? ตอบสั้นๆ เป็นภาษาไทย ไม่เกิน 10 คำ"
                )
            }]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        return f"ไม่ทราบ ({str(e)[:30]})"

# ─── 5. SHEET HELPERS ─────────────────────────────────────────────────────────
SHEET_HEADERS = [
    "folder_type",       # A: IMAGE / DOC
    "original_name",     # B: ชื่อไฟล์เต็มจาก LINE
    "real_name",         # C: ชื่อจริง (ตัด timestamp prefix ออก)
    "extension",         # D: นามสกุล
    "ts_str",            # E: timestamp (YYYY-MM-DD HH:MM:SS.mmm)
    "ts_key",            # F: key 17 หลัก สำหรับจับคู่
    "random_id",         # G: random ID จาก LINE
    "mime_type",         # H: MIME type
    "size_bytes",        # I: ขนาดไฟล์
    "drive_created",     # J: createdTime ใน Drive
    "drive_modified",    # K: modifiedTime ใน Drive
    "file_id",           # L: Drive file ID
    "web_view_link",     # M: ลิงก์ดู
    "download_link",     # N: ลิงก์โหลด
    "haiku_note",        # O: Claude Haiku อธิบาย (เฉพาะไฟล์ที่ parse ไม่ได้)
    "synced_at",         # P: เวลาที่ sync
    "matched_partner",   # Q: ts_key ของไฟล์คู่ (ถ้า match ได้ระหว่างภาพ-เอกสาร)
]

def get_sheet(gc, spreadsheet_id: str, tab_name: str):
    """เปิด/สร้าง worksheet"""
    sh = gc.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(tab_name)
        print(f"📋 เปิด sheet '{tab_name}' ที่มีอยู่แล้ว")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab_name, rows=2000, cols=len(SHEET_HEADERS))
        ws.append_row(SHEET_HEADERS)
        print(f"✨ สร้าง sheet '{tab_name}' ใหม่")
    return ws

def get_processed_ids(ws) -> set:
    """ดึง file_id ที่อยู่ใน Sheet แล้ว (col L = index 11)"""
    all_rows = ws.get_all_values()
    if not all_rows:
        return set()
    return set(row[11] for row in all_rows[1:] if len(row) > 11 and row[11])

# ─── 6. MATCH ─────────────────────────────────────────────────────────────────
def build_ts_map(files: list) -> dict:
    """สร้าง dict ที่ key = ts_key → file"""
    m = {}
    for f in files:
        key = f.get('ts_key', '')
        if key:
            m[key] = f
    return m

# ─── 7. MAIN ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  LINE Drive Sync — by Claude Haiku + Google Drive API")
    print("=" * 60)

    # ตรวจ config
    missing = []
    if not IMAGE_FOLDER_ID: missing.append('LINE_IMAGE_FOLDER_ID')
    if not DOC_FOLDER_ID:   missing.append('LINE_DOC_FOLDER_ID')
    if missing:
        print(f"\n⚠️  ยังไม่ได้ตั้งค่า config: {', '.join(missing)}")
        print("   กรุณาเพิ่มใน config.json แล้วรันใหม่")
        print("   (script จะ sync เฉพาะโฟลเดอร์ที่ตั้งค่าแล้ว)\n")

    # Auth
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)

    # เปิด Sheet
    ws = get_sheet(gc, SPREADSHEET_ID, SHEET_TAB)
    processed_ids = get_processed_ids(ws)
    print(f"🔍 ไฟล์ที่ sync แล้ว: {len(processed_ids)} รายการ\n")

    # ดึงไฟล์จาก 2 โฟลเดอร์
    raw_images = list_folder(drive_service, IMAGE_FOLDER_ID, 'IMAGE')
    raw_docs   = list_folder(drive_service, DOC_FOLDER_ID, 'DOC')

    images = [enrich_file(f, 'IMAGE') for f in raw_images]
    docs   = [enrich_file(f, 'DOC')   for f in raw_docs]

    all_files = images + docs
    new_files = [f for f in all_files if f['id'] not in processed_ids]
    print(f"\n📥 ไฟล์ใหม่ที่ต้อง sync: {len(new_files)} รายการ\n")

    if not new_files:
        print("✅ ทุกอย่าง sync แล้ว! ไม่มีไฟล์ใหม่")
        return

    # สร้าง ts_key map สำหรับจับคู่
    img_ts_map = build_ts_map(images)
    doc_ts_map = build_ts_map(docs)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows_to_add = []

    for f in new_files:
        ts_key = f.get('ts_key', '')
        folder_type = f['folder_type']

        # หาคู่ข้ามโฟลเดอร์
        if folder_type == 'IMAGE' and ts_key in doc_ts_map:
            partner_key = ts_key
        elif folder_type == 'DOC' and ts_key in img_ts_map:
            partner_key = ts_key
        else:
            partner_key = ''

        # ให้ Haiku อธิบายไฟล์ที่ parse ชื่อไม่ได้
        haiku_note = ''
        if not f.get('parsed') and ANTHROPIC_API_KEY:
            print(f"🤖 Haiku วิเคราะห์: {f['name'][:60]}...", end=' ')
            haiku_note = haiku_describe_file(f['name'], f.get('mimeType', ''))
            print(f"→ {haiku_note}")
            time.sleep(0.5)

        row = [
            folder_type,
            f.get('original_name', f['name']),
            f.get('real_name', ''),
            f.get('extension', ''),
            f.get('ts_str', ''),
            ts_key,
            f.get('random_id', ''),
            f.get('mimeType', ''),
            f.get('size', ''),
            f.get('createdTime', ''),
            f.get('modifiedTime', ''),
            f['id'],
            f.get('webViewLink', ''),
            f.get('webContentLink', ''),
            haiku_note,
            now,
            partner_key,
        ]
        rows_to_add.append(row)
        print(f"  {'🖼️' if folder_type == 'IMAGE' else '📄'} {f.get('real_name', f['name'])[:55]}"
              f"  {'↔️ match' if partner_key else ''}")

    # Batch write ทีเดียว (เร็วกว่า append_row ทีละแถว)
    if rows_to_add:
        print(f"\n💾 กำลัง batch write {len(rows_to_add)} แถวเข้า Sheet...")
        ws.append_rows(rows_to_add, value_input_option='RAW')
        print(f"✅ sync สำเร็จ {len(rows_to_add)} รายการ")

    # สรุป stats
    matched = sum(1 for r in rows_to_add if r[16])  # col Q = matched_partner
    print(f"\n📊 สรุป:")
    print(f"   ภาพใหม่     : {sum(1 for f in new_files if f['folder_type']=='IMAGE')}")
    print(f"   เอกสารใหม่  : {sum(1 for f in new_files if f['folder_type']=='DOC')}")
    print(f"   จับคู่ได้    : {matched} คู่")
    print(f"   Sheet tab   : '{SHEET_TAB}'")
    print(f"   Spreadsheet : https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

if __name__ == "__main__":
    main()
