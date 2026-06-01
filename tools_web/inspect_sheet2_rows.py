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
ws = sh.worksheet('tspl_database')
rows = ws.get_all_values()

print("Analyzing tspl_database (Sheet 2) columns 14-21...")
print("-" * 100)
for idx, r in enumerate(rows[1:10], start=2):
    print(f"Row {idx} | ID: {r[0]} | Title: '{r[1]}' | Img Main (14): '{r[14]}' | Img Vec (15): '{r[15]}' | Non-use (16): '{r[16]}' | Img Mid (17): '{r[17]}' | Img Detail (18): '{r[18]}'")
