"""
line_finalize.py — Asset Map Generator
========================================
รันหลังจาก review เสร็จแล้ว
อ่าน APPROVED จาก LINE_Review + ชื่อลายจาก tspl_database (Master)
สร้าง 'Asset_Map' tab ใน Spreadsheet หลัก

Output columns:
  symbol_name | in_database | image_url | doc_url | status
"""

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from google.oauth2 import service_account
import gspread

# ─── CONFIG ───────────────────────────────────────────────────────────────────
with open('config.json', 'r') as f:
    config = json.load(f)

SERVICE_ACCOUNT_FILE   = 'service-account.json'
DEST_SPREADSHEET_ID    = config['SPREADSHEET_ID']           # งานหลัก (เขียน)
DB_SPREADSHEET_ID      = config['DB_SOURCE_SPREADSHEET_ID'] # tspl_database (อ่าน)
LINE_SYNC_TAB          = config.get('LINE_SYNC_SHEET_TAB', 'LINE_Sync')
REVIEW_TAB             = 'LINE_Review'
ASSET_MAP_TAB          = 'Asset_Map'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# ─── SIMILARITY ───────────────────────────────────────────────────────────────
def clean_thai_name(text: str) -> str:
    """ลบตัวเลขนำหน้า สัญลักษณ์ และคำว่า 'ลาย' ออกเพื่อให้การเทียบแม่นยำขึ้น"""
    # ลบตัวเลขและขีดนำหน้า เช่น "013-", "032 - "
    text = re.sub(r'^[\d\.\-\s]+', '', text)
    # ลบคำว่า "ลาย" ที่อยู่หน้าสุด
    if text.startswith('ลาย'):
        text = text[3:]
    return text.strip().lower()

def similarity(a: str, b: str) -> float:
    a_clean, b_clean = clean_thai_name(a), clean_thai_name(b)
    if not a_clean or not b_clean: return 0.0
    if a_clean == b_clean: return 1.0
    if a_clean in b_clean or b_clean in a_clean: return 0.85
    return SequenceMatcher(None, a_clean, b_clean).ratio()

def best_match(name: str, candidates: list, threshold=0.5) -> tuple:
    """หา match ที่ใกล้เคียงที่สุดจาก list ของ (key, value)"""
    best_k, best_v, best_s = '', '', 0.0
    for k, v in candidates:
        s = similarity(name, k)
        if s > best_s:
            best_s, best_k, best_v = s, k, v
    if best_s >= threshold:
        return best_k, best_v, best_s
    return '', '', 0.0

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Asset Map Generator — LINE × Database")
    print("=" * 55)

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    # ── 1. อ่าน tspl_database หน้าแรก (READ ONLY) ─────────────────────────────
    print(f"\n📖 อ่าน หน้าแรก จาก tspl_database...")
    db_sh  = gc.open_by_key(DB_SPREADSHEET_ID)
    db_ws  = db_sh.sheet1  # ใช้หน้าแรกสุดของไฟล์แทนหน้า Master
    db_rows = db_ws.get_all_values()

    if len(db_rows) < 2:
        print("⚠️  หน้าแรก ว่าง")
        db_data = []
    else:
        db_headers = db_rows[0]
        # หา column ชื่อลาย (เช่น 'Title (TH)' หรือ 'ชื่อลาย')
        name_col = 0
        for i, h in enumerate(db_headers):
            h_low = h.lower()
            # ป้องกันการไปจับผิดคอลัมน์ Symbol ID
            if 'title (th)' in h_low or 'title_th' in h_low or h_low in ['ชื่อ', 'ชื่อลาย']:
                name_col = i
                break
        
        db_data = []
        for row in db_rows[1:]:
            if len(row) > name_col and row[name_col].strip():
                # ข้ามลายที่ Symbol ID ขึ้นต้นด้วย # (พี่กบไม่เลือกลายพวกนี้)
                if row[0].startswith('#'):
                    continue
                # pad row ให้เท่ากับ headers
                padded_row = row + [''] * (len(db_headers) - len(row))
                db_data.append((row[name_col].strip(), padded_row))

    db_symbols = [item[0] for item in db_data]
    print(f"   พบ {len(db_data)} รายการใน database")

    # ── 2. อ่าน LINE_Review APPROVED ─────────────────────────────────────────
    print(f"\n📋 อ่าน APPROVED จาก LINE_Review...")
    dest_sh  = gc.open_by_key(DEST_SPREADSHEET_ID)
    rev_ws   = dest_sh.worksheet(REVIEW_TAB)
    rev_rows = rev_ws.get_all_values()

    if len(rev_rows) < 2:
        print("⚠️  LINE_Review ว่าง — รัน line_classify.py ก่อน")
        return

    rev_headers = rev_rows[0]
    rcol = {h: i for i, h in enumerate(rev_headers)}
    STATUS   = rcol.get('STATUS', 0)
    SYMBOL   = rcol.get('haiku_symbol', 1)
    OVERRIDE = rcol.get('override_name', 3)
    VIEW     = rcol.get('img_view_link', 7)
    FILE_ID  = rcol.get('file_id', 9)

    approved_imgs = []  # list of (symbol_name, image_url, file_id)
    for row in rev_rows[1:]:
        if len(row) <= STATUS: continue
        if row[STATUS] != 'APPROVED': continue
        sym = (row[OVERRIDE] if len(row) > OVERRIDE and row[OVERRIDE].strip()
               else (row[SYMBOL] if len(row) > SYMBOL else ''))
        url = row[VIEW] if len(row) > VIEW else ''
        fid = row[FILE_ID] if len(row) > FILE_ID else ''
        if sym and sym not in ('ไม่ใช่ลวดลาย', 'ERROR', 'ไม่ทราบ'):
            approved_imgs.append((sym, url, fid))

    print(f"   APPROVED: {len(approved_imgs)} รูป")

    # ── 3. อ่าน LINE_Sync DOC และ Timestamps ──────────────────────────────────
    print(f"\n📄 อ่าน doc links และวิเคราะห์บริบทเวลาจาก LINE_Sync...")
    sync_ws   = dest_sh.worksheet(LINE_SYNC_TAB)
    sync_rows = sync_ws.get_all_values()
    sync_headers = sync_rows[0] if sync_rows else []
    scol = {h: i for i, h in enumerate(sync_headers)}
    SFOLDER = scol.get('folder_type', 0)
    SREAL   = scol.get('real_name', 2)
    SCREATE = scol.get('drive_created', 9)
    SFILEID = scol.get('file_id', 11)
    SVIEW   = scol.get('web_view_link', 12)

    def parse_dt(s):
        try: return datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
        except: return datetime.min

    doc_candidates = []  # list of (name, url, dt)
    sync_map = {}        # file_id -> dt
    for row in sync_rows[1:]:
        if len(row) <= max(SFOLDER, SFILEID, SCREATE): continue
        dt = parse_dt(row[SCREATE]) if len(row) > SCREATE else datetime.min
        sync_map[row[SFILEID]] = dt
        if row[SFOLDER] == 'DOC':
            name = row[SREAL] if len(row) > SREAL else ''
            url  = row[SVIEW] if len(row) > SVIEW else ''
            if name:
                doc_candidates.append((name, url, dt))
    print(f"   พบเอกสาร: {len(doc_candidates)} ไฟล์")

    # ── 4. Build Asset_Map ────────────────────────────────────────────────────
    print(f"\n🔗 สร้าง Asset_Map ด้วย Context-Aware Matching...")

    img_map = {}  # final_db_key → [url1, url2, ...]
    doc_map = {}  # final_db_key → doc_url

    for haiku_sym, url, fid in approved_imgs:
        img_dt = sync_map.get(fid, datetime.min)
        
        # หาเอกสารที่อัปโหลดเวลาใกล้เคียงที่สุด (Context)
        closest_doc_name = ''
        closest_doc_url = ''
        min_diff = float('inf')
        for d_name, d_url, d_dt in doc_candidates:
            diff = abs((img_dt - d_dt).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_doc_name = d_name
                closest_doc_url = d_url
                
        # เทียบชื่อจาก Haiku กับ Database
        db_key_h, _, score_h = best_match(haiku_sym, [(s, s) for s in db_symbols])
        # เทียบชื่อจากไฟล์เอกสารใกล้เคียง กับ Database
        db_key_d, _, score_d = best_match(closest_doc_name, [(s, s) for s in db_symbols])
        
        # ตัดสินใจเลือกอันที่แมตช์เข้า Database ได้คะแนนสูงกว่า
        if score_h >= score_d and score_h >= 0.5:
            final_key = db_key_h
            used_doc = closest_doc_url if min_diff < 3600 else '' # ภายใน 1 ชม.
        elif score_d > score_h and score_d >= 0.5:
            final_key = db_key_d
            used_doc = closest_doc_url
        else:
            final_key = haiku_sym # หาไม่เจอทั้งคู่ ปล่อยเป็น NEW
            used_doc = closest_doc_url if min_diff < 3600 else ''
            
        img_map.setdefault(final_key, []).append(url)
        if used_doc and final_key not in doc_map:
            doc_map[final_key] = used_doc

    # สร้าง rows
    asset_rows = []
    covered_symbols = set()

    # A) ลายที่อยู่ใน database (จากหน้าแรก)
    for db_sym, full_db_row in db_data:
        imgs = img_map.get(db_sym, [])
        doc_url = doc_map.get(db_sym, '')

        img1 = imgs[0] if len(imgs) > 0 else ''
        img2 = imgs[1] if len(imgs) > 1 else ''
        img3 = imgs[2] if len(imgs) > 2 else ''

        has_img  = bool(imgs)
        has_doc  = bool(doc_url)

        if has_img and has_doc:   status = 'COMPLETE'
        elif has_img:             status = 'NO_DOC'
        elif has_doc:             status = 'NO_IMAGE'
        else:                     status = 'MISSING'

        # เอา row เดิมจาก DB มาต่อท้ายด้วยข้อมูลใหม่
        new_cols = ['✅', img1, img2, img3, doc_url, status, len(imgs)]
        asset_rows.append(full_db_row + new_cols)
        covered_symbols.add(db_sym)

    # B) ลายใหม่จาก LINE ที่ยังไม่อยู่ใน database
    for sym, urls in img_map.items():
        if sym in covered_symbols:
            continue
        doc_url = doc_map.get(sym, '')
        img1 = urls[0] if len(urls) > 0 else ''
        img2 = urls[1] if len(urls) > 1 else ''
        img3 = urls[2] if len(urls) > 2 else ''
        
        # สร้าง row ว่างๆ ให้ความยาวเท่ากับ DB headers
        empty_db_row = [''] * len(db_headers)
        if len(empty_db_row) > name_col:
            empty_db_row[name_col] = sym  # ใส่ชื่อลายลงไปในช่อง name
            
        new_cols = ['❌ ยังไม่อยู่ใน DB', img1, img2, img3, doc_url, 'NEW', len(urls)]
        asset_rows.append(empty_db_row + new_cols)

    # ── 5. เขียน Asset_Map sheet ──────────────────────────────────────────────
    NEW_HEADERS = [
        'in_database',   # ✅ / ❌ ยังไม่อยู่ใน DB
        'image_url_1',   # รูปที่ 1
        'image_url_2',   # รูปที่ 2
        'image_url_3',   # รูปที่ 3
        'doc_url',       # Drive link เอกสาร
        'status',        # COMPLETE / NO_IMAGE / NO_DOC / MISSING / NEW
        'image_count',   # จำนวนรูป
        'updated_at',    # เวลาที่ generate
    ]
    
    FINAL_HEADERS = db_headers + NEW_HEADERS

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_rows = [FINAL_HEADERS] + [[*r, now] for r in asset_rows]

    try:
        am_ws = dest_sh.worksheet(ASSET_MAP_TAB)
        am_ws.clear()
        print(f"   ♻️  clear '{ASSET_MAP_TAB}' แล้ว overwrite ใหม่")
    except gspread.WorksheetNotFound:
        am_ws = dest_sh.add_worksheet(
            title=ASSET_MAP_TAB,
            rows=max(len(final_rows) + 10, 200),
            cols=len(FINAL_HEADERS)
        )
        print(f"   ✨ สร้าง tab '{ASSET_MAP_TAB}' ใหม่")

    am_ws.update(final_rows, value_input_option='RAW')

    # format header
    try:
        am_ws.format("1:1", {
            "backgroundColor": {"red": 0.06, "green": 0.06, "blue": 0.15},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}},
        })
    except Exception:
        pass

    # ── สรุป ──────────────────────────────────────────────────────────────────
    # ตำแหน่งของ status จะอยู่ที่ -2 ก่อน updated_at (เพราะ -1 คือ updated_at ที่เพิ่งเติมตอนสร้าง final_rows)
    # ใน asset_rows ตอนนี้ status คือ index -2 ของแถว
    complete  = sum(1 for r in asset_rows if len(r) >= 2 and r[-2] == 'COMPLETE')
    no_image  = sum(1 for r in asset_rows if len(r) >= 2 and r[-2] == 'NO_IMAGE')
    no_doc    = sum(1 for r in asset_rows if len(r) >= 2 and r[-2] == 'NO_DOC')
    missing   = sum(1 for r in asset_rows if len(r) >= 2 and r[-2] == 'MISSING')
    new_sym   = sum(1 for r in asset_rows if len(r) >= 2 and r[-2] == 'NEW')

    print(f"\n✅ Asset_Map เสร็จแล้ว!\n")
    print(f"📊 สรุป ({len(asset_rows)} รายการ):")
    print(f"   ✅ COMPLETE   : {complete:3} ลาย  (มีทั้งรูปและเอกสาร)")
    print(f"   🖼️  NO_IMAGE   : {no_image:3} ลาย  (ไม่มีรูปใน LINE)")
    print(f"   📄 NO_DOC     : {no_doc:3} ลาย  (ไม่มีเอกสารใน LINE)")
    print(f"   ❓ MISSING    : {missing:3} ลาย  (ไม่มีทั้งคู่)")
    print(f"   🆕 NEW        : {new_sym:3} ลาย  (จาก LINE ยังไม่อยู่ใน DB)")
    print(f"\n   🔗 https://docs.google.com/spreadsheets/d/{DEST_SPREADSHEET_ID}")
    print(f"       → tab '{ASSET_MAP_TAB}'")

if __name__ == "__main__":
    main()
