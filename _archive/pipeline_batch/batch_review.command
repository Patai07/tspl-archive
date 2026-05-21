#!/bin/bash
# batch_review.command — Step 2: เปิด review UI
cd "$(dirname "$0")/.."   # cd ขึ้นไปที่ Web/
echo "🖥️  Step 2: เปิด Review Server..."
echo ""
open http://localhost:5555
python3 pipeline_batch/batch_review.py
