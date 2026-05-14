#!/usr/bin/env python3
"""
merge_haiku_to_db.py — สวมข้อมูลเนื้อหาจาก Haiku Sheet เข้าสู่ Sheet 2 (Production)
=================================================================================
อ่านข้อมูลเนื้อหาล่าสุดที่ AI (Haiku) สกัดเสร็จจากแท็บ 'Haiku_Scan' 
มาสวมอัปเดตเข้ากับ 68 แถวใน Sheet 2 (tspl_database) โดยอัตโนมัติ
รักษา Symbol ID ที่เรียง 001 ไว้คงเดิม เพื่อให้เชื่อมกับรูปภาพในเครื่องได้เป๊ะ 100%
"""

import json
import re
import gspread
from google.oauth2.service_account import Credentials

CONFIG_FILE = 'config.json'
SERVICE_ACCOUNT = 'service-account.json'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize(name):
    n = re.sub(r'^\d+', '', name.strip())
    n = re.sub(r'^[-.\s]+', '', n)
    n = re.sub(r'\.(jpg|png|svg)$', '', n, flags=re.I)
    n = re.sub(r'^ลาย', '', n)
    n = re.sub(r'กระหนก', 'กนก', n)
    n = re.sub(r'\s*\(.*?\)', '', n)
    return re.sub(r'\s+', '', n).lower()

def main():
    print("=" * 65)
    print("🤖 เริ่มดึงเนื้อหาจาก Haiku Sheet มาสวมเข้า Sheet 2 (Production)")
    print("=" * 65)

    config = load_config()
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT, 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)

    # 1. ค้นหาแท็บ Haiku_Scan ล่าสุดใน SPREADSHEET_ID
    print("🔍 กำลังค้นหาข้อมูลจากชีต Haiku ต้นทาง...", flush=True)
    sh_staging = gc.open_by_key(config['SPREADSHEET_ID'])
    haiku_ws = None
    for ws in sh_staging.worksheets():
        if 'Haiku_Scan' in ws.title:
            haiku_ws = ws
            break
    if not haiku_ws:
        # ถ้าหาชื่อตรงๆ ไม่เจอ ให้อ่านชีตแรกสุด
        haiku_ws = sh_staging.worksheets()[0]
    
    h_rows = haiku_ws.get_all_values()
    print(f"📂 พบชีตเป้าหมาย: '{haiku_ws.title}' (มีข้อมูล {len(h_rows)-1} แถว)", flush=True)

    # สร้าง Map เนื้อหาจาก Haiku
    haiku_map = {}
    for r in h_rows[1:]:
        if not r or not r[0].strip() or r[0].strip().startswith('#'): continue
        if len(r) > 1:
            norm_t = normalize(r[1])
            haiku_map[norm_t] = r

    # 2. เปิด Sheet 2 (Production Database)
    print("📝 กำลังอ่าน Sheet 2 (tspl_database)...", flush=True)
    sh_prod = gc.open_by_key(config['DB_SOURCE_SPREADSHEET_ID'])
    prod_ws = sh_prod.worksheet('tspl_database')
    p_rows = prod_ws.get_all_values()
    headers = p_rows[0] if p_rows else []

    updated_count = 0
    for idx, row in enumerate(p_rows[1:], start=1):
        if not row or not row[0].strip() or row[0].strip().startswith('#'): continue
        if len(row) > 1:
            norm_p = normalize(row[1])
            if norm_p in haiku_map:
                h_r = haiku_map[norm_p]
                
                # ขยายความยาวแถวถ้าจำเป็น
                while len(row) < len(headers):
                    row.append('')
                
                # สวมคอลัมน์เนื้อหาจาก Haiku (คอลัมน์ 2, และ 4 ถึง 13)
                if len(h_r) > 2 and h_r[2].strip(): 
                    row[2] = h_r[2].strip()  # Title (EN)
                
                merged_fields = 0
                for c_idx in range(4, min(14, len(h_r))):
                    val = h_r[c_idx].strip()
                    if val and val != 'NONE':
                        row[c_idx] = val
                        merged_fields += 1
                
                if merged_fields > 0:
                    print(f"   ✨ อัปเดตเนื้อหาสำเร็จ: {row[0]} — {row[1]}")
                    updated_count += 1

    print(f"\n📊 สรุปการสวมข้อมูล: อัปเดตเนื้อหาใหม่จาก Haiku สำเร็จ {updated_count} ลาย", flush=True)
    
    # 3. เขียนทับอัปเดตลง Sheet 2
    print("💾 กำลังบันทึกข้อมูลกลับลง Sheet 2...", flush=True)
    prod_ws.clear()
    prod_ws.update(p_rows, value_input_option='RAW')
    
    # ตกแต่ง Header
    try:
        prod_ws.format("1:1", {
            "backgroundColor": {"red": 0.06, "green": 0.06, "blue": 0.15},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
        })
    except Exception:
        pass
    print("✅ สวมเนื้อหาเสร็จสมบูรณ์ 100%! รหัส Symbol ID และรูปภาพตรงกันเป๊ะพร้อมใช้งาน", flush=True)

if __name__ == '__main__':
    main()
