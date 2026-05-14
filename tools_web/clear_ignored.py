import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f: config = json.load(f)
creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(creds)
sh = gc.open_by_key(config['SPREADSHEET_ID'])

try:
    ws = sh.worksheet('Ignored_Docs')
    ws.clear()
    ws.append_row(['Filename', 'Reason', 'Timestamp'])
    print("Cleared Ignored_Docs successfully")
except Exception as e:
    print(f"Error: {e}")
