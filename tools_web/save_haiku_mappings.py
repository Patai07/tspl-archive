import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

SPREADSHEET_ID = config.get('SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)

sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.worksheet('Haiku_Scan_Master')
rows = ws.get_all_values()

out_path = "/Users/phu/Desktop/งานพี่กบ/Web/tools_web/haiku_mappings.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"Total rows in Haiku_Scan_Master: {len(rows)}\n")
    headers = rows[0]
    try:
        title_idx = headers.index('Title TH')
        sid_idx = headers.index('Symbol ID')
        doc_idx = headers.index('Doc Name')
        link_idx = headers.index('Drive Link')
        
        for r in rows[1:]:
            if len(r) > max(title_idx, sid_idx, doc_idx):
                sid = r[sid_idx]
                title = r[title_idx]
                doc = r[doc_idx]
                p_name = doc.split('_')[0] if doc else ''
                f.write(f"ID: {sid} | Title TH: '{title}' | Folder in Drive: '{p_name}' | Doc: '{doc}'\n")
    except Exception as e:
        f.write(f"Error mapping: {e}\n")

print(f"Saved mappings to {out_path}")
