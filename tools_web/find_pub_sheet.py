import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

SPREADSHEET_ID = config.get('SPREADSHEET_ID')
PROD_SPREADSHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)

def print_gids(sheet_id, name):
    print(f"\nSpreadsheet: {name} ({sheet_id})")
    try:
        sh = gc.open_by_key(sheet_id)
        for ws in sh.worksheets():
            print(f"  - Worksheet: '{ws.title}' | ID: {ws.id}")
    except Exception as e:
        print(f"  Error: {e}")

print_gids(SPREADSHEET_ID, "Staging Sheet (Sheet 1)")
print_gids(PROD_SPREADSHEET_ID, "Production Sheet (Sheet 2)")
