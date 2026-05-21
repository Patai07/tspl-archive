import json
from google.oauth2 import service_account
import gspread

with open('config.json', 'r') as f: config = json.load(f)
creds = service_account.Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['SPREADSHEET_ID'])

for i, ws in enumerate(sh.worksheets()):
    print(f"Sheet {i}: {ws.title}")

ws0 = sh.get_worksheet(0)
rows = ws0.get_all_values()
if rows:
    print("\nHeaders of Sheet 0:")
    print(rows[0])
    print(f"Total Rows in Sheet 0: {len(rows)}")

ws1 = sh.worksheet('tspl_database') if 'tspl_database' in [w.title for w in sh.worksheets()] else None
if ws1:
    rows1 = ws1.get_all_values()
    print("\nHeaders of tspl_database:")
    print(rows1[0])
    print(f"Total Rows in tspl_database: {len(rows1)}")

