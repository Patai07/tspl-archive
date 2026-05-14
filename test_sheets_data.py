import json
from google.oauth2 import service_account
import gspread

with open('config.json', 'r') as f: config = json.load(f)
creds = service_account.Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['SPREADSHEET_ID'])
ws = sh.get_worksheet(0)
rows = ws.get_all_values()
for i, r in enumerate(rows[1:10]):
    print(f"Row {i+1}: {r[0]} | {r[1]} | {r[3]}")
