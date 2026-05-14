#!/bin/bash
# line_dashboard.command — เปิด Control Panel ทั้งหมดในที่เดียว
cd "$(dirname "$0")/.."   # ขึ้นไป Web/
echo "🏛  เปิด LINE Archive Dashboard..."
echo ""
open http://localhost:5556
python3 pipeline_line/line_dashboard.py
