#!/bin/zsh

# สคริปต์ Reset Google Sheets — ล้างข้อมูลทั้งหมดและใส่ Header กลับ
# สร้างโดย Antigravity AI

cd "$(dirname "$0")"

echo "================================================"
echo "🗑️  TSPL Archive — Reset Sheet"
echo "================================================"
echo ""
echo "⚠️  คำเตือน: คุณกำลังจะล้างข้อมูลทั้งหมดใน Google Sheets"
echo "    ข้อมูลทั้งหมดจะถูกลบ และ Header จะถูกสร้างใหม่"
echo "    สคริปต์หลักจะเริ่มประมวลผลใหม่ตั้งแต่ต้น"
echo ""
echo -n "ยืนยันการ Reset หรือไม่? (y/n): "
read confirmation

if [ "$confirmation" = "y" ]; then
    echo ""
    echo "🧹 กำลังล้างข้อมูล..."
    python3 -c "
import gspread
from google.oauth2 import service_account
import json

with open('config.json', 'r') as f:
    config = json.load(f)

creds = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['SPREADSHEET_ID'])
worksheet = sh.get_worksheet(0)

# ล้างข้อมูลทั้งหมด
worksheet.clear()
print('  ✅ ล้างข้อมูลเรียบร้อย')

# ใส่ Header กลับ (20 คอลัมน์)
headers = [
    'symbol_id', 'title_th', 'title_en',
    'category', 'location', 'confidence', 'ethics',
    'connotation_th', 'connotation_en',
    'protocol_preserve', 'protocol_do_not',
    'morphemes_th', 'morphemes_en',
    'tags',
    'img_main', 'img_vector', 'img_context',
    'source_filename', 'col_19',
    'source_link'
]
worksheet.append_row(headers)
print('  ✅ สร้าง Header ใหม่เรียบร้อย')
print(f'  📋 พร้อมรับข้อมูลใหม่ ({len(headers)} คอลัมน์)')
"
    echo ""
    echo "================================================"
    echo "✨ Sheet พร้อม Reset แล้ว! รัน run_extractor.command ได้เลย"
    echo "================================================"
else
    echo ""
    echo "❌ ยกเลิกการ Reset"
fi

echo ""
read -k 1 -s "กดปุ่มใดก็ได้เพื่อปิดหน้าต่างนี้..."
