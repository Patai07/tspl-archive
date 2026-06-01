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
ws = sh.get_worksheet(0)
rows = ws.get_all_values()

print("Analyzing Sheet 1 (first tab) data columns 17 (img_mid) & 19 (img_extra1)...")
print("-" * 100)

count_docs = 0
for i, r in enumerate(rows[1:], start=2):
    sid = r[0].strip()
    title = r[1].strip()
    img_mid_val = r[17].strip() if len(r) > 17 else ''
    
    # Check if this column contains doc file format
    if '.docx' in img_mid_val or '.pdf' in img_mid_val:
        p_name = img_mid_val.split('_')[0]
        print(f"Row {i} | ID: {sid} | Title: '{title}' | img_mid stores Doc Name: '{img_mid_val}' -> Folder in Drive: '{p_name}'")
        count_docs += 1

print("-" * 100)
print(f"Total rows where img_mid contains document names: {count_docs}")
