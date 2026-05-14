#!/bin/bash
# line_finalize.command — Step 3: สร้าง Asset_Map หลัง review เสร็จ
cd "$(dirname "$0")/.."   # cd ขึ้นไปที่ Web/
echo "📊 สร้าง Asset_Map sheet..."
echo ""
python3 pipeline_line/line_finalize.py
echo ""
echo "กด Enter เพื่อปิด..."
read
