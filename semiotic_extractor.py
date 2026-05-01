import time
import json
import io
import docx
import re
import anthropic
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

# --- 1. CONFIGURATION ---
with open('config.json', 'r') as f: config = json.load(f)

# Anthropic API Key will be read from config.json
ANTHROPIC_API_KEY = config.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL = "claude-3-5-haiku-latest"

SERVICE_ACCOUNT_FILE = 'service-account.json'
DRIVE_FOLDER_ID = config['DRIVE_FOLDER_ID']
SPREADSHEET_ID = config['SPREADSHEET_ID']

CATEGORY_MAP = {
    "Nature & Botany": "01_Nature", "Fauna & Mythical": "02_Fauna",
    "Geometric & Synthetic": "03_Geometric", "Sacred & Belief": "04_Sacred"
}

def clean_json(text):
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match: return match.group(1)
    return text

def extract_for_template(content, filename):
    prompt = (
        f"คุณคือผู้เชี่ยวชาญด้านศิลปะไทย สถาปัตยกรรม และสัญศาสตร์วัฒนธรรม "
        f"วิเคราะห์เอกสารลายไทยจากไฟล์ชื่อ '{filename}' แล้วสกัดข้อมูลเป็น JSON object ดังนี้:\n\n"
        "- symbol_id: รหัสในรูปแบบ TSP-LST-(NAT/FAU/GEO/SAC)-NNN\n"
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
        return raw_data.decode('utf-8')
    except: return None

def main():
    if ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY_HERE":
        print("❌ กรุณาใส่ ANTHROPIC_API_KEY ในไฟล์ semiotic_extractor.py ก่อนรัน!")
        print("   สมัครได้ที่: https://console.anthropic.com")
        return
    print(f"ระบบเริ่มทำงาน (Claude {CLAUDE_MODEL} | Delay 2s/file)...", flush=True)
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets'])
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.get_worksheet(0)
    all_rows = worksheet.get_all_values()
    # col_18 (index 17) = source_filename — ใช้ check ว่าไฟล์ไหนถูกประมวลผลไปแล้ว
    processed_filenames = set(row[17] for row in all_rows if len(row) > 17 and row[17])
    print(f"พบไฟล์ที่ประมวลผลไปแล้ว {len(processed_filenames)} ไฟล์ — จะข้ามทั้งหมด (ไม่กิน token)", flush=True)
    items = drive_service.files().list(q=f"'{DRIVE_FOLDER_ID}' in parents and trashed = false", fields="files(id, name, mimeType, webViewLink)").execute().get('files', [])
    print(f"พบไฟล์ {len(items)} ไฟล์...", flush=True)

    for file in items:
        f_name = file['name']
        if f_name in processed_filenames:
            print(f"⏩ ข้าม: {f_name}", flush=True)
            continue
        print(f"ประมวลผล: {f_name}...", end=" ", flush=True)
        content = get_file_content(drive_service, file['id'], file.get('mimeType'))
        if not content: continue
        data = extract_for_template(content, f_name)
        if not data: continue
        try:
            sid = data.get('symbol_id', 'N/A').upper()
            cat = data.get('category', 'Nature & Botany')
            folder = CATEGORY_MAP.get(cat, '01_Nature')
            base_path = f"assets/images/database/{folder}/{sid}"
            row = [
                sid, data.get('title_th', f_name), data.get('title_en', 'N/A'),
                cat, data.get('location', 'N/A'), data.get('confidence', 'Verified'), data.get('ethics', 'low'),
                data.get('connotation_th', 'N/A'), data.get('connotation_en', 'N/A'),
                data.get('protocol_preserve', 'N/A'), data.get('protocol_do_not', 'N/A'),
                data.get('morphemes_th', 'N/A'), data.get('morphemes_en', 'N/A'),
                data.get('tags', 'N/A'),
                f"{base_path}/main.jpg", f"{base_path}/vectors/vector.svg", f"{base_path}/context.jpg",
                f_name,  # col_18 = source_filename (ใช้ตรวจ dedup)
                "",      # col_19 = สำรองไว้ใช้ภายหลัง
                file.get('webViewLink', 'N/A')
            ]
            worksheet.append_row(row)
            print(f"✅ สำเร็จ: {sid}", flush=True)
        except Exception as e:
            print(f"❌ บันทึกผิดพลาด: {str(e)[:60]}", flush=True)
        time.sleep(2)  # Claude paid tier — 2s ก็เพียงพอ

if __name__ == "__main__":
    main()
