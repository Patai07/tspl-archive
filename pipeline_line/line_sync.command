#!/bin/bash
# line_sync.command — double-click เพื่อ sync LINE Drive → Google Sheet
cd "$(dirname "$0")/.."   # cd ขึ้นไปที่ Web/
echo "🔄 กำลัง sync LINE Drive files → Google Sheet..."
echo ""
python3 pipeline_line/line_sync.py
echo ""
echo "กด Enter เพื่อปิดหน้าต่างนี้..."
read
