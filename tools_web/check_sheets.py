import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f: config = json.load(f)
creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['SPREADSHEET_ID'])

for ws in sh.worksheets():
    if ws.title.startswith('Haiku_Scan') or ws.title == 'Ignored_Docs':
        rows = ws.get_all_values()
        print(f"Sheet '{ws.title}': {len(rows)} rows")
        if len(rows) > 1:
            print(f"  Sample row 2: {rows[1][:3]}... Source File: {rows[1][17] if len(rows[1])>17 else 'N/A'}")
