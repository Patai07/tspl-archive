#!/bin/bash
# run_pipeline.command — ปุ่มหลัก: Sync + Classify ในครั้งเดียว
cd "$(dirname "$0")/.."   # cd ขึ้นไปที่ Web/ เพื่อหา config.json
clear

echo "╔══════════════════════════════════════════════╗"
echo "║   LINE Archive Pipeline                      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

echo "▶ Step 1/2 — Sync Drive folders → LINE_Sync sheet"
echo "────────────────────────────────────────────────"
python3 pipeline_line/line_sync.py
echo ""

if [ $? -ne 0 ]; then
  echo "❌ line_sync.py ล้มเหลว กรุณาตรวจ config.json"
  echo "กด Enter เพื่อปิด..."
  read; exit 1
fi

echo ""
echo "▶ Step 2/2 — Haiku Vision classify images"
echo "────────────────────────────────────────────────"
echo "   (ใช้เวลาประมาณ 10-20 นาที ขึ้นกับจำนวนรูปใหม่)"
echo "   ปิดหน้าต่างนี้ไม่ได้นะ — ปล่อยทิ้งไว้ได้เลย"
echo ""
python3 pipeline_line/line_classify.py

if [ $? -ne 0 ]; then
  echo "❌ line_classify.py ล้มเหลว"
  echo "กด Enter เพื่อปิด..."
  read; exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   ✅ Pipeline เสร็จแล้ว!                    ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  ขั้นตอนถัดไป:                              ║"
echo "║  1. double-click  line_review.command        ║"
echo "║     → review รูปที่เป็น PENDING              ║"
echo "║  2. double-click  line_finalize.command      ║"
echo "║     → สร้าง Asset_Map sheet                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "กด Enter เพื่อปิดหน้าต่างนี้..."
read
