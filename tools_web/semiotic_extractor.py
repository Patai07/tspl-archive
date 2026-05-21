import time
import json
import io
import docx
import re
import anthropic
from PyPDF2 import PdfReader
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
from datetime import datetime

# --- 1. CONFIGURATION ---
with open('config.json', 'r') as f: config = json.load(f)

# Anthropic API Key will be read from config.json
ANTHROPIC_API_KEY = config.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

SERVICE_ACCOUNT_FILE = 'service-account.json'
DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SPREADSHEET_ID = config['SPREADSHEET_ID']

CATEGORY_MAP = {
    "Nature & Botany": "01_Nature", "Fauna & Mythical": "02_Fauna",
    "Geometric & Synthetic": "03_Geometric", "Sacred & Belief": "04_Sacred"
}

def log_ignored(sh, filename, reason):
    try:
        try: ws_ig = sh.worksheet('Ignored_Docs')
        except:
            ws_ig = sh.add_worksheet(title='Ignored_Docs', rows=1000, cols=3)
            ws_ig.append_row(['Filename', 'Reason', 'Timestamp'])
        ws_ig.append_row([filename, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except Exception as e:
        print("Ignored_Docs append error:", e)

def get_next_symbol_id(all_rows, category):
    cat_code = "NAT"
    if "Fauna" in category: cat_code = "FAU"
    elif "Geometric" in category: cat_code = "GEO"
    elif "Sacred" in category: cat_code = "SAC"
    
    max_num = 0
    pattern = re.compile(rf'TSP-LST-{cat_code}-(\d+)', re.IGNORECASE)
    for r in all_rows:
        if r and len(r) > 0 and r[0]:
            clean_id = r[0].lstrip('#').strip()
            m = pattern.search(clean_id)
            if m:
                num = int(m.group(1))
                if num > max_num: max_num = num
                
    return f"TSP-LST-{cat_code}-{max_num + 1:03d}"

def clean_json(text):
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match: return match.group(1)
    return text

def get_normalized_title(filename):
    base = filename.rsplit('.', 1)[0]
    if re.match(r'^202\d_\d{4}_', base):
        title = base.split('_')[-1]
    else:
        title = base
    # ตัดคำว่า "ลาย" หรือสเปซออกเพื่อให้เช็คซ้ำได้แม่นยำสุดๆ
    clean = re.sub(r'^ลาย', '', title.strip()).strip().lower()
    return clean

def extract_for_template(content, filename):
    prompt = (
        f"คุณคือผู้เชี่ยวชาญด้านศิลปะไทย สถาปัตยกรรม และสัญศาสตร์วัฒนธรรม "
        f"วิเคราะห์เอกสารลายไทยจากไฟล์ชื่อ '{filename}' แล้วสกัดข้อมูลเป็น JSON object ดังนี้:\n\n"
        "- category: เลือกหนึ่งอย่างเท่านั้น [Nature & Botany, Fauna & Mythical, Geometric & Synthetic, Sacred & Belief]\n"
        "- title_th: ชื่อลายภาษาไทย (ตอบเป็นภาษาไทยเท่านั้น)\n"
        "- title_en: ชื่อลายภาษาอังกฤษ\n"
        "- location: ดูจากเนื้อหาเอกสารเท่านั้น ห้ามเดาหรือใช้ความรู้ทั่วไป: (1) ถ้าเอกสารระบุวัดหรือสถานที่ → ตอบเป็น ชื่อวัด, จังหวัด เช่น วัดพระธาตุลำปางหลวง, ลำปาง (2) ถ้าเอกสารระบุแค่จังหวัดหรือเมือง → ตอบแค่ชื่อจังหวัด/เมืองนั้น (3) ถ้าเอกสารไม่ระบุสถานที่เลย → ตอบว่า ไม่ปรากฏหลักฐานสถานที่ — ตอบเป็นภาษาไทยเท่านั้น\n"
        "- ethics: ระดับความอ่อนไหว — เลือกหนึ่ง [low, medium, high]\n"
        "- confidence: ความมั่นใจในการระบุ — เลือกหนึ่ง [Verified, Reconstructed, Fragment, Hypothetical]\n"
        "- connotation_th: อธิบายความหมายทางวัฒนธรรมและสัญลักษณ์ 2-3 ประโยค (ตอบเป็นภาษาไทยเท่านั้น)\n"
        "- connotation_en: Describe the cultural meaning and symbolism in 2-3 sentences in English\n"
        "- protocol_preserve: แนวทางการอนุรักษ์และใช้งานอย่างเหมาะสม 1-2 ประโยค (ตอบเป็นภาษาไทยเท่านั้น)\n"
        "- protocol_do_not: สิ่งที่ควรหลีกเลี่ยงเมื่อนำลายไปใช้ 1-2 ประโยค (ตอบเป็นภาษาไทยเท่านั้น)\n"
        "- morphemes_th: องค์ประกอบย่อยของลาย คั่นด้วย | เช่น กลีบบัว | เส้นโค้ง | ลายก้านขด (ตอบเป็นภาษาไทยเท่านั้น)\n"
        "- morphemes_en: Visual sub-elements separated by | e.g. Lotus petal | Curved line | Spiral tendril\n"
        "- tags: 5-8 คำคั่นด้วยเครื่องหมายจุลภาค (,) เช่น ลายไทย, สถาปัตยกรรม, วัด, พุทธศิลป์ (ตอบเป็นภาษาไทยเท่านั้น)\n\n"
        "🚨 สำคัญมาก: หากเนื้อหาในเอกสารไม่เกี่ยวข้องกับลวดลายไทย (เช่น เป็นเอกสารขออนุมัติงบประมาณ, ใบเสร็จ, หนังสือราชการ หรือประกาศทั่วไป) ให้กำหนดค่า title_th เป็น 'IRRELEVANT' เท่านั้น ไม่ต้องกรอกข้อมูลอื่น\n\n"
        "ตอบเป็น JSON object เท่านั้น ห้ามใส่คำอธิบายเพิ่มเติม เนื้อหา:\n" + content[:3000]
    )

    wait_seconds = 60
    for attempt in range(3):  # ลองซ้ำสูงสุด 3 ครั้ง
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            json_text = clean_json(message.content[0].text)
            return json.loads(json_text)
        except anthropic.RateLimitError:
            print(f"\n   ⚠️  Rate limit! พัก {wait_seconds} วินาที (ครั้งที่ {attempt+1}/3)...", flush=True)
            time.sleep(wait_seconds)
            wait_seconds *= 2  # exponential backoff
        except anthropic.AuthenticationError:
            print("\n   ❌ API Key ผิดพลาด! กรุณาตรวจสอบ ANTHROPIC_API_KEY ในสคริปต์", flush=True)
            return None
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)[:80]}", flush=True)
            return None
    print("\n   ❌ เกิน retry limit แล้ว ข้ามไฟล์นี้", flush=True)
    return None

def get_file_content(drive_service, file_id, mime_type):
    try:
        if mime_type == 'application/vnd.google-apps.document':
            return drive_service.files().export(fileId=file_id, mimeType='text/plain').execute().decode('utf-8')
        request = drive_service.files().get_media(fileId=file_id)
        raw_data = request.execute()
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(io.BytesIO(raw_data))
            return "\n".join([p.text for p in doc.paragraphs])
        elif mime_type == 'application/pdf':
            reader = PdfReader(io.BytesIO(raw_data))
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return raw_data.decode('utf-8')
    except Exception as e: 
        print(f"Error reading file content: {e}")
        return None

def should_skip_file(file_name, mime_type):
    """ตรวจสอบว่าไฟล์นี้ควร skip หรือไม่"""
    # ไฟล์ระบบ / ไฟล์ temp
    SKIP_NAMES = {'.ds_store', 'thumbs.db', 'desktop.ini'}
    SKIP_PREFIXES = ('~$', '.~', '._')
    ALLOWED_MIMES = {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.google-apps.document',  # Google Docs
        'application/pdf',
        'text/plain',
        'text/markdown',
    }
    name_lower = file_name.lower().strip()
    if name_lower in SKIP_NAMES:
        return True
    if any(name_lower.startswith(p) for p in SKIP_PREFIXES):
        return True
    if mime_type not in ALLOWED_MIMES:
        return True
    return False

def get_all_docs_in_asset_root(drive_service, root_id):
    items = []
    cats = drive_service.files().list(
        q=f"'{root_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)", pageSize=50
    ).execute().get('files', [])

    for cat in cats:
        token = None
        while True:
            resp = drive_service.files().list(
                q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
                fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token
            ).execute()
            
            for p in resp.get('files', []):
                file_token = None
                while True:
                    files_resp = drive_service.files().list(
                        q=f"'{p['id']}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'",
                        fields="nextPageToken,files(id, name, mimeType, webViewLink)", pageSize=100, pageToken=file_token
                    ).execute()
                    
                    for f in files_resp.get('files', []):
                        if should_skip_file(f['name'], f.get('mimeType', '')):
                            print(f"   ⏭️  ข้ามไฟล์ระบบ/temp: {f['name']}", flush=True)
                            continue
                        f['parent_name'] = p['name']
                        f['category_folder'] = cat['name']
                        items.append(f)
                    
                    file_token = files_resp.get('nextPageToken')
                    if not file_token:
                        break
                        
            token = resp.get('nextPageToken')
            if not token:
                break
    return items

def main():
    if not ANTHROPIC_API_KEY:
        print("❌ ไม่พบ ANTHROPIC_API_KEY ใน config.json! กรุณาเพิ่มค่า ANTHROPIC_API_KEY ก่อนรัน")
        print("   สมัครได้ที่: https://console.anthropic.com")
        return
    print(f"ระบบเริ่มทำงาน (Claude {CLAUDE_MODEL} | Delay 2s/file)...", flush=True)
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets'])
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    
    # Try to open Master, create if missing
    MASTER_NAME = "Haiku_Scan_Master"
    try:
        worksheet = sh.worksheet(MASTER_NAME)
    except gspread.exceptions.WorksheetNotFound:
        print(f"⚡ ไม่พบ Tab '{MASTER_NAME}' — กำลังสร้างให้ใหม่...", flush=True)
        worksheet = sh.add_worksheet(title=MASTER_NAME, rows="1000", cols="20")
        headers = [
            "Symbol ID", "Title TH", "Title EN", "Category", "Location", "Confidence", "Ethics",
            "Connotation TH", "Connotation EN", "Preservation", "Restriction",
            "Morphemes TH", "Morphemes EN", "Tags", "Main Img", "Vector Path", "Context Img",
            "Doc Name", "Timestamp", "Drive Link"
        ]
        worksheet.append_row(headers)
        time.sleep(1)

    # Try to open Ignored, create if missing
    try:
        ws_ignored = sh.worksheet("Ignored_Docs")
    except gspread.exceptions.WorksheetNotFound:
        ws_ignored = sh.add_worksheet(title="Ignored_Docs", rows="1000", cols="5")
        ws_ignored.append_row(["Filename", "Reason", "Timestamp"])
        time.sleep(1)
    
    # ── โหลด Sheet 1 (ข้อมูลเก่าที่ Approve แล้ว) เพื่อ fallback ──
    master_ws = sh.get_worksheet(0)
    master_headers = master_ws.row_values(1)
    old_data_rows = master_ws.get_all_values()
    
    # ── ระบบล้างชื่อและ Manual Mapping เพื่อป้องกันการแสกนซ้ำ ──
    def _norm(s):
        if not s: return ""
        import unicodedata
        s = unicodedata.normalize('NFC', str(s))
        s = re.sub(r'\(.*?\)', '', s)
        s = re.sub(r'^\d+[-\s.]+', '', s.strip())
        s = re.sub(r'^(ลวดลาย|ลาย)', '', s)
        s = re.sub(r'\.(jpg|jpeg|png|webp|tiff|tif|heic|heif)$', '', s, flags=re.I)
        return re.sub(r'[^a-zA-Z0-9\u0E00-\u0E7F]', '', s).lower().strip()

    manual_map = {
        "ลวดลายดอกไม้ประดับอัญมณี": "สังวาลพระพุทธชินราช",
        "010หน้าบันลูกฟักหน้าพรหม": "จั่วภัควัมหน้าพรหม",
        "1-กระหนกสามตัว": "กนกสามตัว",
        "ธรรมาสน์ วัดราชบูรณะ จังหวัดพิษณุโลก.jpg": "ลายก้านขดธรรมาสน์ไม้จำหลัก",
        "ธรรมาสน์ วัดราชบูรณะ จังหวัดพิษณุโลก": "ลายก้านขดธรรมาสน์ไม้จำหลัก",
        "มกร": "องค์มกรคายนาค",
        "ครุฑ": "ครุฑไม้จำหลัก",
        "ปลา": "ลายปลา"
    }

    old_data_map = {}
    for r in old_data_rows[1:]:
        if len(r) > 1 and r[1].strip():
            clean_name = _norm(r[1])
            old_data_map[clean_name] = r
            
    # เพิ่มรายการจาก Manual Map เข้าไปในฐานข้อมูลตรวจซ้ำด้วย
    for drive_name, sheet_name in manual_map.items():
        clean_drive = _norm(drive_name)
        if _norm(sheet_name) in old_data_map:
            old_data_map[clean_drive] = old_data_map[_norm(sheet_name)]
            
    print(f"📚 โหลดข้อมูลเก่าจาก Sheet 1 แล้ว ({len(old_data_map)} รายการ) เพื่อป้องกันการแสกนซ้ำ", flush=True)

    # กรอง Header ที่ไม่ควรเอาไปใส่ Scan Sheet ใหม่
    SKIP_HEADERS = {'drive_confirmed', 'drive confirmed', 'confirmed', 'note', 'remark', 'หมายเหตุ'}
    clean_headers = [h for h in master_headers if h.strip().lower() not in SKIP_HEADERS]
    
    # ── สร้าง / เปิด Scan Sheet ใหม่ โดยอิงโครงสร้างจาก Sheet 1 ──
    sheet_name = "Haiku_Scan_Master"
    try:
        worksheet = sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows=1000, cols=max(20, len(clean_headers)))
        worksheet.append_row(clean_headers)

        
    # all_rows สำหรับ Haiku_Scan Sheet (ใช้ตรวจซ้ำและ append)
    all_rows = worksheet.get_all_values()

    # เพื่อให้สอดคล้องกับโฟลเดอร์ Drive แบบ 1:1 ให้เริ่มนับ ID สดใหม่ในชีตสแกนเสมอ
    all_rows_for_id = list(all_rows)
    
    # ── 3. ไล่เช็คไฟล์ที่เคยแสกนไปแล้ว "จากทุก Tab" เพื่อประหยัด API และป้องกัน ID ซ้ำ ──
    print("🔍 กำลังตรวจสอบประวัติการแสกนและรหัส ID จากทุก Tab...", flush=True)
    processed_filenames = set()
    processed_titles = set()
    all_rows_for_id_global = [] # เก็บทุกแถวจากทุก Tab เพื่อเช็คเลข ID สูงสุด
    
    for ws in sh.worksheets():
        if ws.title.startswith("Haiku_Scan") or ws.index == 0:
            rows = ws.get_all_values()
            if len(rows) > 1:
                all_rows_for_id_global.extend(rows[1:])
                for r in rows[1:]:
                    if len(r) > 17 and r[17].strip():
                        fn = r[17].strip()
                        processed_filenames.add(fn)
                        if '_' in fn:
                            p_folder = fn.split('_')[0].strip().lower()
                            processed_titles.add(p_folder)
    
    print(f"🎯 พบประวัติการแสกนแล้วทั้งหมด {len(processed_filenames)} ไฟล์", flush=True)
    print(f"📊 รวบรวมข้อมูล ID เดิมเพื่อป้องกันการออกเลขซ้ำแล้ว", flush=True)

    
    # โหลดรายชื่อไฟล์ที่ข้ามแล้ว (Ignored) เพื่อจะได้ไม่สแกนซ้ำ
    try:
        ws_ignored = sh.worksheet('Ignored_Docs')
        ignored_rows = ws_ignored.get_all_values()
        for r in ignored_rows[1:]:
            if r and r[0]: 
                processed_filenames.add(r[0])
                processed_titles.add(_norm(r[0]))
    except:
        pass

    print(f"พบไฟล์ที่ประมวลผลไปแล้ว {len(processed_filenames)} ไฟล์ — จะข้ามทั้งหมด (ไม่กิน token)", flush=True)
    
    print(f"กำลังดึงรายการไฟล์จาก Drive (โครงสร้างใหม่ที่พี่กบจัดหมวดไว้)...", flush=True)
    items = get_all_docs_in_asset_root(drive_service, DRIVE_ASSET_ROOT)
    print(f"พบไฟล์ทั้งหมดในโฟลเดอร์ {len(items)} ไฟล์...", flush=True)

    for file in items:
        f_name = file['name']
        p_name = file.get('parent_name', 'Unknown')
        mime = file.get('mimeType', '')
        
        # ใช้ชื่อโฟลเดอร์แม่มาร่วมสร้างความแตกต่าง เพราะไฟล์อาจชื่อ "การวิเคราะห์เจาะลึก.docx" ซ้ำกัน
        context_name = f"{p_name}_{f_name}"

        # ข้ามไฟล์ที่ไม่ใช่เอกสาร หรือเป็น PDF (ปิดการอ่าน PDF ชั่วคราวตามคำสั่ง) หรือไฟล์รูปภาพต่างๆ
        if 'image' in mime or mime == 'application/pdf' or f_name.lower().endswith('.pdf') or '.ai' in f_name.lower() or '.bin' in f_name.lower() or f_name.lower().endswith('.csv'):
            continue
            
        if context_name in processed_filenames:
            print(f"⏩ ข้าม (ประมวลผลไฟล์นี้แล้ว): {context_name}", flush=True)
            continue
            
        # ใช้ชื่อโฟลเดอร์แบบเป๊ะๆ เป็นตัวระบุเอกลักษณ์ของลาย เพื่อไม่ให้โฟลเดอร์ชื่อคล้ายกันถูกตัดทิ้ง
        folder_key = p_name.strip().lower()
        if folder_key in processed_titles:
            print(f"⏩ ข้าม (ประมวลผลเอกสารในโฟลเดอร์นี้ไปแล้ว): {p_name} ({f_name})", flush=True)
            continue
            
        print(f"ประมวลผล: {p_name} / {f_name}...", end=" ", flush=True)
        content = get_file_content(drive_service, file['id'], mime)
        if not content:
            print("❌ อ่านเนื้อหาไฟล์ไม่ได้ - ย้ายไปเก็บที่ Ignored_Docs", flush=True)
            log_ignored(sh, context_name, "Failed to read file content (Corrupt/Unsupported)")
            processed_filenames.add(context_name)
            continue
            
        data = extract_for_template(content, f"{p_name} - {f_name}")
        if not data:
            print("❌ AI สกัดข้อมูลล้มเหลวเกิน 3 ครั้ง - ย้ายไปเก็บที่ Ignored_Docs", flush=True)
            log_ignored(sh, context_name, "Failed extraction >3 times (API/Format Error)")
            processed_filenames.add(context_name)
            continue
        
        if data.get('title_th', '').strip().upper() == 'IRRELEVANT':
            print("🚫 ไม่เกี่ยวกับลวดลาย (IRRELEVANT) - ข้ามการลง Sheet หลัก", flush=True)
            log_ignored(sh, context_name, 'Not related to patterns (IRRELEVANT)')
            processed_filenames.add(context_name)
            continue

        try:
            cat_folder = file.get('category_folder', '')
            cat_folder_lower = cat_folder.lower()
            if 'nature' in cat_folder_lower or 'พฤกษา' in cat_folder or '01' in cat_folder:
                cat = 'Nature & Botany'
            elif 'fauna' in cat_folder_lower or 'สัตว์' in cat_folder or '02' in cat_folder:
                cat = 'Fauna & Mythical'
            elif 'geometric' in cat_folder_lower or 'เรขา' in cat_folder or '03' in cat_folder:
                cat = 'Geometric & Synthetic'
            elif 'sacred' in cat_folder_lower or 'ความเชื่อ' in cat_folder or '04' in cat_folder:
                cat = 'Sacred & Belief'
            else:
                cat = data.get('category', 'Nature & Botany')
            
            data['category'] = cat  # บังคับเขียนทับ JSON category ให้ตรงกับโฟลเดอร์จริงเสมอ
            sid = get_next_symbol_id(all_rows_for_id_global, cat)
            folder = CATEGORY_MAP.get(cat, '01_Nature')
            base_path = f"assets/images/database/{folder}/{sid}"
            # ── Fallback จาก Sheet 1 เมื่อ AI ไม่พบข้อมูล ──
            empty_vals = {'n/a', 'ไม่ปรากฏ', 'ไม่ระบุ', '-', '', 'unknown'}
            def ai_or_old(ai_val, old_row, col_idx):
                """ใช้ค่า AI ก่อน ถ้าว่าง/ไม่ปรากฏ ดึงจาก old_row แทน"""
                v = str(ai_val or '').strip()
                if v.lower() in empty_vals or 'ไม่ปรากฏ' in v:
                    old_v = old_row[col_idx].strip() if old_row and len(old_row) > col_idx else ''
                    if old_v and old_v.lower() not in empty_vals:
                        return old_v  # ได้ข้อมูลเก่า!
                return v if v else 'N/A'

            title_th = data.get('title_th', p_name)
            old_row  = old_data_map.get(_norm(title_th), old_data_map.get(_norm(p_name), []))
            if old_row:
                print(f"   🔗 พบข้อมูลเก่าตรงกันใน Sheet 1: ดึง fallback มาเติม", flush=True)

            row = [
                sid,
                title_th,
                ai_or_old(data.get('title_en'),      old_row, 2),
                cat,
                ai_or_old(data.get('location'),      old_row, 4),   # Location
                data.get('confidence', 'Verified'),
                data.get('ethics', 'low'),
                ai_or_old(data.get('connotation_th'), old_row, 7),
                ai_or_old(data.get('connotation_en'), old_row, 8),
                ai_or_old(data.get('protocol_preserve'), old_row, 9),
                ai_or_old(data.get('protocol_do_not'),   old_row, 10),
                ai_or_old(data.get('morphemes_th'),  old_row, 11),
                ai_or_old(data.get('morphemes_en'),  old_row, 12),
                ai_or_old(data.get('tags'),          old_row, 13),
                f"{base_path}/main.jpg", f"{base_path}/vectors/vector.svg", f"{base_path}/context.jpg",
                context_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                file.get('webViewLink', 'N/A')
            ]
            worksheet.append_row(row)
            all_rows.append(row)  # อัปเดตข้อมูลในเมมโมรี่เพื่อรันเลขถัดไปไม่ให้ซ้ำ
            processed_filenames.add(context_name)
            processed_titles.add(folder_key)
            all_rows_for_id_global.append(row)  # อัปเดต ID pool รวมด้วย เพื่อให้เลขถัดไปไม่ซ้ำ
            print(f"✅ สำเร็จ: {sid}", flush=True)
        except Exception as e:
            print(f"❌ บันทึกผิดพลาด: {str(e)[:60]}", flush=True)
        time.sleep(2)  # Claude paid tier — 2s ก็เพียงพอ

if __name__ == "__main__":
    main()
