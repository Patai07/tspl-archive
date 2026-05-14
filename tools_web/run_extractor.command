#!/bin/zsh
set -e  # หยุดทันทีถ้า command ใดล้มเหลว

# สคริปต์รันระบบ Archive Extractor อัตโนมัติ (เวอร์ชันรองรับ Environment)
# สร้างโดย Antigravity AI

# นำทางไปยังโฟลเดอร์ปัจจุบัน
cd "$(dirname "$0")/.."  # ขึ้นไป Web/ เพื่อหา config.json

echo "------------------------------------------------"
echo "🛠️  ตรวจสอบความพร้อมของระบบ..."
echo "------------------------------------------------"

# ติดตั้ง Libraries ที่จำเป็น (บังคับผ่านระบบป้องกันของ Mac)
python3 -m pip install anthropic google-auth google-api-python-client gspread python-docx --break-system-packages

echo "🚀 เริ่มรันระบบ Thai Symbol Pattern Extractor..."
echo "------------------------------------------------"

# รันสคริปต์ Python
python3 semiotic_extractor.py

echo "------------------------------------------------"
echo "✅ ภารกิจเสร็จสมบูรณ์! (หรือคุณได้กดหยุดสคริปต์แล้ว)"
echo "หน้าจอนี้จะค้างไว้เพื่อให้คุณตรวจสอบผลลัพธ์..."
echo "------------------------------------------------"
read -k 1 -s "กดปุ่มใดก็ได้เพื่อปิดหน้าต่างนี้..."
