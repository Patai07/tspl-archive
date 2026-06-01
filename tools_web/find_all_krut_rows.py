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

print("Rows containing 'ครุฑ' in Sheet 1:")
for r in rows:
    if any('ครุฑ' in str(val) for val in r):
        print(f"ID: {r[0]} | Title: '{r[1]}' | Category: '{r[3]}' | Main Img: '{r[14]}' | Vector: '{r[15]}' | Mid: '{r[17]}' | Detail: '{r[18]}'")
