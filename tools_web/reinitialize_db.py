#!/usr/bin/env python3
"""
reinitialize_db.py — TSPL Big Cleaning & Sequential Re-indexing
=================================================================
1. สแกนโฟลเดอร์จริงจาก Google Drive ทั้ง 4 หมวด (28, 15, 8, 17 รวม 68 ลาย)
2. ดึงข้อมูลเนื้อหา (semiotic text metadata) จากฐานข้อมูลเดิมมาจับคู่เพื่อไม่ให้สูญหาย
3. รัน Symbol ID ใหม่แบบเรียงลำดับตั้งแต่ 001 ของแต่ละหมวด
4. ลบโฟลเดอร์รูปภาพเก่าในเซิร์ฟเวอร์ทิ้งทั้งหมด เพื่อล้างรหัสเก่า
5. เขียนทับ Sheet 2 (tspl_database) ด้วยข้อมูล 68 แถวใหม่ที่ถูกต้องสมบูรณ์
"""

import os
import json
import re
import shutil
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

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

def clean_title(name):
    t = re.sub(r'^\d+', '', name.strip())
    t = re.sub(r'^[-.\s]+', '', t)
    t = re.sub(r'\.(jpg|png|svg)$', '', t, flags=re.I)
    return t.strip()

def main():
    print("=" * 60)
    print("🚀 เริ่มกระบวนการ BIG CLEANING & RE-INITIALIZE ฐานข้อมูล")
    print("=" * 60)

    config = load_config()
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT, 
        scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    )
    drive_svc = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(config['DB_SOURCE_SPREADSHEET_ID'])
    ws = sh.worksheet('tspl_database')

    # 1. Backup ของเก่าก่อน
    rows = ws.get_all_values()
    headers = rows[0] if rows else []
    
    os.makedirs('tools_web/backups', exist_ok=True)
    backup_path = f"tools_web/backups/tspl_db_pre_cleaning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'rows': rows}, f, ensure_ascii=False, indent=2)
    print(f"💾 บันทึก Backup ข้อมูลเดิมเรียบร้อย: {backup_path}", flush=True)

    # 2. Map ข้อมูลเก่าเตรียมสวมเนื้อหา
    old_map = {}
    for r in rows[1:]:
        if not r or not r[0].strip() or r[0].strip().startswith('#'): continue
        if len(r) > 1:
            norm_t = normalize(r[1])
            old_map[norm_t] = r

    # 3. ดึงโฟลเดอร์จาก Drive
    print("📂 กำลังสแกนโครงสร้างโฟลเดอร์หลักใน Google Drive...", flush=True)
    root_id = config['DRIVE_ASSET_ROOT']
    cats = drive_svc.files().list(
        q=f"'{root_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)"
    ).execute().get('files', [])

    # กำหนดนิยามหมวดหมู่เป้าหมาย
    cat_definitions = {
        '01': {'title': 'Nature & Botany',       'prefix': 'TSP-LST-NAT-', 'local': '01_Nature'},
        '02': {'title': 'Fauna & Mythical',      'prefix': 'TSP-LST-FAU-', 'local': '02_Fauna'},
        '03': {'title': 'Geometric & Synthetic', 'prefix': 'TSP-LST-GEO-', 'local': '03_Geometric'},
        '04': {'title': 'Sacred & Belief',       'prefix': 'TSP-LST-SAC-', 'local': '04_Sacred'}
    }

    new_rows = []
    total_folders = 0

    for cat_obj in sorted(cats, key=lambda x: x['name']):
        cat_name = cat_obj['name']
        code = cat_name[:2]
        if code not in cat_definitions: continue
        cdef = cat_definitions[code]

        # ดึง subfolders ทั้งหมด
        subfolders = drive_svc.files().list(
            q=f"'{cat_obj['id']}' in parents and trashed=false and (mimeType='application/vnd.google-apps.folder' or name contains '.jpg')",
            fields="files(id,name)", pageSize=200
        ).execute().get('files', [])
        
        # กรองให้แน่ใจว่าเอาเฉพาะไฟล์ที่ทำหน้าที่เป็นโฟลเดอร์ลาย
        valid_subs = [f for f in subfolders if not f['name'].startswith('.')]
        valid_subs.sort(key=lambda x: x['name'])

        print(f"\n📁 หมวด {cat_name} (พบ {len(valid_subs)} ลาย)")
        total_folders += len(valid_subs)

        counter = 1
        for sub in valid_subs:
            title = clean_title(sub['name'])
            sid = f"{cdef['prefix']}{counter:03d}"
            norm_sub = normalize(sub['name'])

            # สร้างโครงสร้างแถวใหม่ความยาวเท่า header
            new_r = [''] * len(headers)
            new_r[0] = sid
            new_r[1] = title
            new_r[3] = cdef['title']

            if norm_sub in old_map:
                old_r = old_map[norm_sub]
                # สวมข้อมูลเนื้อหาเดิม (คอลัมน์ 2, และ 4 ถึง 13)
                if len(old_r) > 2:  new_r[2] = old_r[2]  # Title (EN)
                for c_idx in range(4, min(14, len(old_r))):
                    new_r[c_idx] = old_r[c_idx]
                print(f"   🔄 [สวมเนื้อหาเดิม] {sid} : {title}")
            else:
                print(f"   ✨ [สร้างลายใหม่]   {sid} : {title}")

            new_rows.append(new_r)
            counter += 1

    print(f"\n📊 สรุปจัดระเบียบข้อมูลใหม่ทั้งหมด: {len(new_rows)} ลาย (ตรงกับโฟลเดอร์ Drive เป๊ะ)", flush=True)

    # 4. ลบโฟลเดอร์รูปภาพเก่าในเซิร์ฟเวอร์
    print("\n🗑️  กำลังล้างโฟลเดอร์รูปภาพเก่าในเครื่องเซิร์ฟเวอร์ (assets/images/database)...", flush=True)
    base_dir = 'assets/images/database'
    for loc_folder in ['01_Nature', '02_Fauna', '03_Geometric', '04_Sacred']:
        target_path = os.path.join(base_dir, loc_folder)
        if os.path.exists(target_path):
            for item in os.listdir(target_path):
                if item.startswith('.'): continue
                ipath = os.path.join(target_path, item)
                if os.path.isdir(ipath):
                    shutil.rmtree(ipath)
                else:
                    os.remove(ipath)
    print("✅ ล้างรูปภาพรหัสเก่าออกหมดจดเรียบร้อย", flush=True)

    # 5. เขียนทับ Sheet 2
    print("\n📝 กำลังเขียนทับ Sheet 2 (tspl_database) ด้วยชุดข้อมูลใหม่...", flush=True)
    ws.clear()
    ws.update([headers] + new_rows, value_input_option='RAW')
    
    # ตกแต่ง Header สีสีกนิดหน่อย
    try:
        ws.format("1:1", {
            "backgroundColor": {"red": 0.06, "green": 0.06, "blue": 0.15},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
        })
    except Exception:
        pass
    print("✅ เขียนทับฐานข้อมูลเสร็จสมบูรณ์!", flush=True)

if __name__ == '__main__':
    main()
