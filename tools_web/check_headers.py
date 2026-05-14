import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f: config = json.load(f)
creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['DB_SOURCE_SPREADSHEET_ID'])
ws = sh.worksheet('tspl_database')

headers = ws.row_values(1)
for i, h in enumerate(headers):
    col_letter = chr(65 + i) if i < 26 else chr(64 + i//26) + chr(65 + i%26)
    print(f"Col {col_letter} ({i+1}): {h}")
