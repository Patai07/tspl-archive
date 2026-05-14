#!/bin/bash
# line_classify.command — Step 1: ให้ Haiku Vision อ่านรูปทุกรูป
cd "$(dirname "$0")"
echo "🤖 Step 1: Haiku Vision กำลังอ่านรูป..."
echo "   (ใช้เวลาประมาณ 10-15 นาทีสำหรับ 581 รูป)"
echo ""
pip3 install Pillow flask --quiet
python3 line_classify.py
echo ""
echo "✅ เสร็จแล้ว! รัน line_review.command เพื่อ review ต่อ"
echo "กด Enter เพื่อปิด..."
read
