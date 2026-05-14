"""
line_classify.py — Haiku Vision Image Classifier
==================================================
Download ภาพทุกรูปจาก LINE_Sync → Haiku Vision วิเคราะห์
เขียนผลลัพธ์พร้อม status PENDING ลง 'LINE_Review' tab
รัน line_review.py หลังจากนี้เพื่อ review ผล
"""

import json
import time
import re
import io
import base64
from datetime import datetime
from difflib import SequenceMatcher
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
import anthropic

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ─── CONFIG ───────────────────────────────────────────────────────────────────
with open('config.json', 'r') as f:
    config = json.load(f)

SERVICE_ACCOUNT_FILE = 'service-account.json'
ANTHROPIC_API_KEY    = config.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL         = "claude-haiku-4-5-20251001"
SPREADSHEET_ID       = config['SPREADSHEET_ID']
SOURCE_TAB           = config.get('LINE_SYNC_SHEET_TAB', 'LINE_Sync')
REVIEW_TAB           = 'LINE_Review'

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
]

MAX_IMAGE_PX   = 800   # resize ก่อนส่ง Haiku ประหยัด token
DELAY_SEC      = 0.8   # delay ระหว่างรูป
AUTO_THRESHOLD = 0.55  # similarity score สำหรับ auto-approve

# ─── IMAGE HELPERS ────────────────────────────────────────────────────────────
def resize_image_bytes(data: bytes, max_px=MAX_IMAGE_PX) -> bytes:
    """Resize ภาพให้ไม่เกิน max_px บน longest side"""
    if not HAS_PIL:
        return data
    try:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((max_px, max_px), Image.LANCZOS)
        buf = io.BytesIO()
        fmt = img.format or 'JPEG'
        if fmt not in ('JPEG', 'PNG', 'GIF', 'WEBP'):
            fmt = 'JPEG'
        img.save(buf, format=fmt)
        return buf.getvalue()
    except Exception:
        return data

def get_media_type(filename: str) -> str:
    ext = filename.lower().rsplit('.', 1)[-1]
    return {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif',
        'webp': 'image/webp', 'heic': 'image/jpeg',
    }.get(ext, 'image/jpeg')

# ─── HAIKU VISION ─────────────────────────────────────────────────────────────
def best_doc_match(symbol: str, doc_map: dict) -> tuple:
    """หาเอกสารที่ชื่อใกล้เคียงสัญลักษณ์มากที่สุด
    Returns (matched_symbol, score)"""
    if not symbol or symbol in ('ไม่ใช่ลวดลาย', 'ERROR', 'ไม่ทราบ'):
        return '', 0.0
    best_sym, best_score = '', 0.0
    sym_lower = symbol.strip().lower()
    for cand in doc_map:
        cand_lower = cand.strip().lower()
        if not cand_lower:
            continue
        # exact
        if sym_lower == cand_lower:
            return cand, 1.0
        # substring
        if sym_lower in cand_lower or cand_lower in sym_lower:
            score = 0.85
        else:
            score = SequenceMatcher(None, sym_lower, cand_lower).ratio()
        if score > best_score:
            best_score = score
            best_sym = cand
    return best_sym, best_score

def auto_status(symbol: str, confidence: str, match_score: float) -> str:
    """ตัดสินใจ status อัตโนมัติ"""
    if confidence != 'high':
        return 'PENDING'           # ไม่มั่นใจ → รอ review
    if symbol in ('ไม่ใช่ลวดลาย', 'ERROR', 'ไม่ทราบ'):
        return 'REJECTED'          # high confidence ว่าไม่ใช่ลวดลาย
    if match_score >= AUTO_THRESHOLD:
        return 'APPROVED'          # high confidence + ชื่อตรงกับเอกสาร
    return 'PENDING'               # high confidence แต่ match ไม่ได้ → review

def classify_image(client, image_bytes: bytes, filename: str,
                   symbol_candidates: list) -> dict:
    """ส่งภาพให้ Haiku วิเคราะห์ว่าเป็นลายอะไร"""
    data_b64 = base64.standard_b64encode(image_bytes).decode('utf-8')
    media_type = get_media_type(filename)

    cands = "\n".join(f"- {s}" for s in symbol_candidates[:60])
    prompt = (
        "รูปนี้แสดงลวดลายหรือสัญลักษณ์ไทยอะไร?\n\n"
        f"รายชื่อลวดลายในฐานข้อมูล:\n{cands}\n\n"
        "คำแนะนำ:\n"
        "- ถ้าเห็นลวดลายที่ตรงกับในรายการ → ตอบชื่อนั้น\n"
        "- ถ้าไม่มีในรายการ → อธิบายสั้นๆ ว่าเห็นอะไร\n"
        "- ถ้าไม่ใช่ลวดลายไทย (รูปทั่วไป เอกสาร ฯลฯ) → symbol = 'ไม่ใช่ลวดลาย'\n\n"
        "ตอบ JSON เท่านั้น:\n"
        '{"symbol": "ชื่อ", "confidence": "high/medium/low", "note": "สั้นๆ"}'
    )

    for attempt in range(3):
        try:
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data_b64,
                        }},
                        {"type": "text", "text": prompt},
                    ]
                }]
            )
            text = msg.content[0].text.strip()
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json.loads(m.group(0))
                return {
                    'symbol':     result.get('symbol', 'ไม่ทราบ'),
                    'confidence': result.get('confidence', 'low'),
                    'note':       result.get('note', ''),
                }
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"   ⚠️  Rate limit — พัก {wait}s", flush=True)
            time.sleep(wait)
        except Exception as e:
            print(f"   ❌ {str(e)[:60]}", flush=True)
            break
    return {'symbol': 'ERROR', 'confidence': 'low', 'note': 'vision failed'}

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 58)
    print("  LINE Image Classifier — Claude Haiku Vision")
    print("=" * 58)
    if not HAS_PIL:
        print("  ⚠️  PIL ไม่ได้ติดตั้ง (pip install Pillow) — ส่งรูปขนาดเต็ม")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)

    # ── อ่าน LINE_Sync ───────────────────────────────────────────────────────
    print(f"\n📖 อ่านจาก '{SOURCE_TAB}'...")
    src_ws   = sh.worksheet(SOURCE_TAB)
    all_rows = src_ws.get_all_values()
    headers  = all_rows[0]
    col      = {h: i for i, h in enumerate(headers)}

    FOLDER  = col.get('folder_type', 0)
    ORIG    = col.get('original_name', 1)
    REAL    = col.get('real_name', 2)
    EXT     = col.get('extension', 3)
    FILE_ID = col.get('file_id', 11)
    VIEW    = col.get('web_view_link', 12)
    DL      = col.get('download_link', 13)

    images = [r for r in all_rows[1:] if len(r) > FOLDER and r[FOLDER] == 'IMAGE']
    docs   = [r for r in all_rows[1:] if len(r) > FOLDER and r[FOLDER] == 'DOC']
    print(f"   ภาพ: {len(images)}, เอกสาร: {len(docs)}")

    # ── สกัดชื่อสัญลักษณ์จากเอกสาร (candidates) ─────────────────────────────
    DOC_PATTERN = re.compile(
        r'9\.\d+[\s_]*(TSPL_Field_Notes|แบบฟอร์มแฟกต์ชีตสัญลักษณ์|'
        r'TSPL_Visual_Reading|แบบฟอร์มสรุปคะแนน)[\s_\-]*(.*)',
        re.IGNORECASE
    )
    symbol_candidates = []
    for row in docs:
        real = row[REAL] if len(row) > REAL else ''
        m = DOC_PATTERN.search(real)
        if m:
            s = m.group(2).strip().lstrip('-_').strip()
            s = re.sub(r'\.(docx?|pdf|txt)$', '', s, flags=re.IGNORECASE).strip()
            if s and s not in symbol_candidates:
                symbol_candidates.append(s)
    # ถ้า extract ไม่ได้ ให้ใช้ชื่อไฟล์โดยตรง
    for row in docs:
        real = row[REAL] if len(row) > REAL else row[ORIG]
        clean = re.sub(r'\.(docx?|pdf|txt)$', '', real, flags=re.IGNORECASE).strip()
        if clean and clean not in symbol_candidates:
            symbol_candidates.append(clean)
    # dict สำหรับ fast matching
    doc_symbol_set = {s: s for s in symbol_candidates}
    print(f"   Symbol candidates: {len(symbol_candidates)} รายการ")

    # ── เปิด/สร้าง LINE_Review tab ───────────────────────────────────────────
    REVIEW_HEADERS = [
        'STATUS',           # A: PENDING / APPROVED / REJECTED
        'haiku_symbol',     # B: Haiku's guess
        'confidence',       # C: high/medium/low
        'override_name',    # D: user กรอกชื่อแก้ไข (ถ้าต้องการ)
        'haiku_note',       # E: Haiku's note
        'img_real_name',    # F: ชื่อไฟล์ original
        'img_extension',    # G: นามสกุล
        'img_view_link',    # H: Drive view link
        'img_download_link',# I: Drive download link
        'file_id',          # J: Drive file ID (ใช้ใน review UI)
        'classified_at',    # K: เวลาที่ classify
    ]

    try:
        rev_ws = sh.worksheet(REVIEW_TAB)
        existing = rev_ws.get_all_values()
        done_ids = set(r[9] for r in existing[1:] if len(r) > 9 and r[9])
        print(f"\n📋 '{REVIEW_TAB}' มีอยู่แล้ว — ข้ามไฟล์ที่ classify แล้ว {len(done_ids)} รูป")
    except gspread.WorksheetNotFound:
        rev_ws = sh.add_worksheet(title=REVIEW_TAB, rows=2000, cols=len(REVIEW_HEADERS))
        rev_ws.append_row(REVIEW_HEADERS)
        done_ids = set()
        print(f"\n✨ สร้าง tab '{REVIEW_TAB}' ใหม่")

    # ── classify loop ─────────────────────────────────────────────────────────
    client     = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    new_images = [r for r in images if (r[FILE_ID] if len(r) > FILE_ID else '') not in done_ids]
    print(f"\n🔍 ต้อง classify {len(new_images)} รูป (ข้าม {len(images)-len(new_images)} ที่ทำแล้ว)\n")

    batch_rows = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, row in enumerate(new_images, 1):
        fid      = row[FILE_ID] if len(row) > FILE_ID else ''
        real     = row[REAL]    if len(row) > REAL    else row[ORIG]
        ext      = row[EXT]     if len(row) > EXT     else ''
        view     = row[VIEW]    if len(row) > VIEW     else ''
        dl       = row[DL]      if len(row) > DL       else ''
        filename = row[ORIG]    if len(row) > ORIG     else 'image.jpg'

        print(f"[{i:3}/{len(new_images)}] 🖼️  {real[:45] or filename[:45]}...", end=' ', flush=True)

        try:
            raw  = drive_service.files().get_media(fileId=fid).execute()
            data = resize_image_bytes(raw)
            result = classify_image(client, data, filename, symbol_candidates)
            sym  = result['symbol']
            conf = result['confidence']
            note = result['note']
            # auto-match กับเอกสาร
            matched_sym, match_score = best_doc_match(sym, doc_symbol_set)
            status = auto_status(sym, conf, match_score)
            conf_icon  = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(conf, '⚪')
            status_icon = {'APPROVED': '✅', 'REJECTED': '❌', 'PENDING': '⏳'}[status]
            print(f"{conf_icon} {sym[:28]}  {status_icon}", flush=True)
        except Exception as e:
            print(f"❌ {str(e)[:50]}", flush=True)
            sym, conf, note, status, matched_sym, match_score = 'ERROR', 'low', str(e)[:80], 'PENDING', '', 0.0

        batch_rows.append([
            status, sym, conf, '', note,
            real, ext, view, dl, fid, now,
        ])

        # batch write ทุก 50 รูป
        if len(batch_rows) >= 50:
            rev_ws.append_rows(batch_rows, value_input_option='RAW')
            batch_rows = []
            print(f"   💾 บันทึก batch แล้ว...", flush=True)

        time.sleep(DELAY_SEC)

    if batch_rows:
        rev_ws.append_rows(batch_rows, value_input_option='RAW')

    # ── สรุป ──────────────────────────────────────────────────────────────────
    # นับจาก sheet จริง
    all_rev = rev_ws.get_all_values()
    approved = sum(1 for r in all_rev[1:] if r and r[0] == 'APPROVED')
    rejected = sum(1 for r in all_rev[1:] if r and r[0] == 'REJECTED')
    pending  = sum(1 for r in all_rev[1:] if r and r[0] == 'PENDING')

    print(f"\n✅ classify เสร็จแล้ว!")
    print(f"\n📊 สรุป Auto-classification:")
    print(f"   ✅ APPROVED (auto): {approved} รูป")
    print(f"   ❌ REJECTED (auto): {rejected} รูป  (ไม่ใช่ลวดลาย)")
    print(f"   ⏳ PENDING (review): {pending} รูป  ← ต้องดูเพิ่มเติม")
    if pending > 0:
        print(f"\n   → รัน: python3 line_review.py เพื่อ review {pending} รูปที่เหลือ")
    else:
        print(f"\n   ✨ ไม่มีรูปที่ต้อง review เพิ่มเติม!")

if __name__ == "__main__":
    main()
