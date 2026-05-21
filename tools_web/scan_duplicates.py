import json, os, re
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
with open('config.json', 'r') as f: config = json.load(f)
SPREADSHEET_ID = config['SPREADSHEET_ID'] # Sheet 1
SERVICE_ACCOUNT_FILE = 'service-account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def scan():
    print("🔍 เริ่มต้นการตรวจสอบรายชื่อลายที่ซ้ำใน Sheet 1 (Staging)...", flush=True)
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.get_worksheet(0)
        rows = ws.get_all_values()
        
        if len(rows) < 2:
            print("✅ ไม่พบข้อมูลใน Sheet", flush=True)
            return

        groups = {}
        for idx, r in enumerate(rows[1:], start=2):
            if not r or not r[0].strip() or r[0].strip().startswith('#'): continue
            title = r[1] if len(r) > 1 else ''
            # Normalize title
            ct = re.sub(r'^ลาย', '', title.strip()).lower()
            ct = re.sub(r'\s+', '', ct)
            if not ct: continue
            
            if ct not in groups: groups[ct] = []
            groups[ct].append(f"แถว {idx} (ID: {r[0]})")

        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        
        if not duplicates:
            print("✅ ยินดีด้วย! ไม่พบรายชื่อลายที่ซ้ำกันในระบบ", flush=True)
        else:
            print(f"⚠️  พบข้อมูลซ้ำทั้งหมด {len(duplicates)} กลุ่ม:", flush=True)
            for title, info in duplicates.items():
                print(f"   • ลาย '{title}': {', '.join(info)}", flush=True)
                
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}", flush=True)

if __name__ == "__main__":
    scan()
