#!/bin/bash
# batch_sync.command — double-click เพื่อ sync Asset Drive → Google Sheet
cd "$(dirname "$0")/.."   # cd ขึ้นไปที่ Web/
echo "🔄 กำลัง sync Asset Drive files → Google Sheet..."
echo ""
python3 pipeline_batch/batch_sync.py
echo ""
echo "กด Enter เพื่อปิดหน้าต่างนี้..."
read
