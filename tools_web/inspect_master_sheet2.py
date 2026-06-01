import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

PROD_SPREADSHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(PROD_SPREADSHEET_ID)
ws = sh.worksheet('Master')
rows = ws.get_all_values()

print(f"Worksheet 'Master' in Sheet 2 has {len(rows)} rows.")
print("Headers:", rows[0])
print("First 3 records:")
for i, r in enumerate(rows[1:4], start=2):
    print(f"Row {i} | {r[:4]} | Main Img: {r[14] if len(r)>14 else ''}")
