import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f: config = json.load(f)
creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['DB_SOURCE_SPREADSHEET_ID'])

print("Worksheets in Sheet 2 (PROD):")
for ws in sh.worksheets():
    print(f"- {ws.title}")
