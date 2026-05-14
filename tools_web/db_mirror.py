"""
db_mirror.py — TSPL Database Mirror Sync
=========================================
อ่านข้อมูลจาก tspl_database spreadsheet (read-only, ไม่แตะต้นฉบับเลย)
แล้ว copy ทั้งหมดเข้า tab 'DB_Mirror' ใน Spreadsheet หลัก

เรียกใช้:  python3 db_mirror.py
หรือ double-click:  db_mirror.command
"""

import json
from datetime import datetime
from google.oauth2 import service_account
import gspread

# ─── CONFIG ───────────────────────────────────────────────────────────────────
with open('config.json', 'r') as f:
    config = json.load(f)

SERVICE_ACCOUNT_FILE = 'service-account.json'

# ต้นทาง (database ที่ curate manual — READ ONLY)
SRC_SPREADSHEET_ID = config['DB_SOURCE_SPREADSHEET_ID']
SRC_TAB            = config.get('DB_SOURCE_TAB', 'tspl_database')

# ปลายทาง (Spreadsheet หลักของโปรเจกต์)
DEST_SPREADSHEET_ID = config['SPREADSHEET_ID']
DEST_TAB            = config.get('DB_DEST_TAB', 'DB_Mirror')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  TSPL Database Mirror Sync")
    print("=" * 55)

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    # ── อ่านต้นทาง (ไม่แก้ไขเลย) ───────────────────────────────────────────
    print(f"\n📖 อ่านจาก: '{SRC_TAB}' ({SRC_SPREADSHEET_ID[:20]}...)")
    src_sh = gc.open_by_key(SRC_SPREADSHEET_ID)
    src_ws = src_sh.worksheet(SRC_TAB)
    all_data = src_ws.get_all_values()

    if not all_data:
        print("⚠️  ไม่พบข้อมูลใน source sheet")
        return

    headers  = all_data[0]
    data_rows = all_data[1:]
    print(f"   พบ {len(data_rows)} แถว, {len(headers)} คอลัมน์")

    # ── เปิด/สร้างปลายทาง ───────────────────────────────────────────────────
    dest_sh = gc.open_by_key(DEST_SPREADSHEET_ID)
    try:
        dest_ws = dest_sh.worksheet(DEST_TAB)
        print(f"\n♻️  พบ tab '{DEST_TAB}' แล้ว → จะ clear แล้ว overwrite ใหม่")
        dest_ws.clear()
    except gspread.WorksheetNotFound:
        dest_ws = dest_sh.add_worksheet(
            title=DEST_TAB,
            rows=max(len(all_data) + 10, 200),
            cols=max(len(headers) + 2, 26)
        )
        print(f"\n✨ สร้าง tab '{DEST_TAB}' ใหม่")

    # ── เพิ่ม meta column ──────────────────────────────────────────────────
    synced_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_headers = headers + ["_synced_at", "_source_tab"]

    # build rows
    final_rows = [final_headers]
    for row in data_rows:
        # padding ถ้า row สั้นกว่า header
        padded = row + [''] * (len(headers) - len(row))
        padded += [synced_at, SRC_TAB]
        final_rows.append(padded)

    # ── batch write ──────────────────────────────────────────────────────────
    print(f"\n💾 กำลัง write {len(final_rows)-1} แถว → '{DEST_TAB}'...")
    dest_ws.update(final_rows, value_input_option='RAW')

    # ── format header row ────────────────────────────────────────────────────
    try:
        dest_ws.format("1:1", {
            "backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.18},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        })
    except Exception:
        pass  # format เป็น optional

    print(f"✅ mirror สำเร็จ!\n")
    print(f"📊 สรุป:")
    print(f"   ต้นทาง  : '{SRC_TAB}' @ {SRC_SPREADSHEET_ID[:30]}...")
    print(f"   ปลายทาง : '{DEST_TAB}' @ Spreadsheet หลัก")
    print(f"   แถวข้อมูล: {len(data_rows)} แถว")
    print(f"   sync เมื่อ: {synced_at}")
    print(f"\n   🔗 https://docs.google.com/spreadsheets/d/{DEST_SPREADSHEET_ID}")

if __name__ == "__main__":
    main()
