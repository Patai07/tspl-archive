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

# Read Sheet 1 (first tab)
ws1 = sh.get_worksheet(0)
rows1 = ws1.get_all_values()

# Read Haiku_Scan_Master
ws_haiku = sh.worksheet('Haiku_Scan_Master')
rows_haiku = ws_haiku.get_all_values()

# Make a map from Haiku_Scan_Master: Title TH -> Doc Name
haiku_map = {}
headers_haiku = rows_haiku[0]
title_idx = headers_haiku.index('Title TH')
doc_idx = headers_haiku.index('Doc Name')

for r in rows_haiku[1:]:
    if len(r) > max(title_idx, doc_idx):
        title = r[title_idx].strip()
        doc = r[doc_idx].strip()
        haiku_map[title] = doc

print("Matching Sheet 1 rows to Haiku_Scan_Master...")
for r in rows1[1:]:
    sid = r[0].strip()
    if not sid or sid.startswith('#'):
        continue
    title = r[1].strip()
    
    doc = haiku_map.get(title)
    if doc:
        p_name = doc.split('_')[0]
        print(f"ID: {sid} | Title TH: '{title}' | Match Doc: '{doc}' -> Drive Folder: '{p_name}'")
    else:
        # Try a fuzzy title match
        matched = False
        for h_title, h_doc in haiku_map.items():
            if title in h_title or h_title in title:
                p_name = h_doc.split('_')[0]
                print(f"ID: {sid} | Title TH: '{title}' (Fuzzy Match '{h_title}') | Match Doc: '{h_doc}' -> Drive Folder: '{p_name}'")
                matched = True
                break
        if not matched:
            print(f"ID: {sid} | Title TH: '{title}' -> ❌ No match in Haiku_Scan_Master")
