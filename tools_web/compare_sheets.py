import csv
import urllib.request
import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv"
PROD_SPREADSHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)

# Fetch published CSV
response = urllib.request.urlopen(csv_url)
csv_content = response.read().decode('utf-8')
pub_reader = csv.DictReader(csv_content.splitlines())
pub_rows = list(pub_reader)

# Read tspl_database
sh = gc.open_by_key(PROD_SPREADSHEET_ID)
ws = sh.worksheet('tspl_database')
sheet_rows = ws.get_all_values()
sheet_headers = sheet_rows[0]
sheet_data = [dict(zip(sheet_headers, r)) for r in sheet_rows[1:]]

print(f"Published CSV has {len(pub_rows)} rows.")
print(f"Sheet tspl_database (1iJIr2v...) has {len(sheet_data)} rows.")

# Compare Symbol IDs
pub_ids = set(r.get('Symbol ID', '').strip() for r in pub_rows)
sheet_ids = set(r.get('Symbol ID', '').strip() for r in sheet_data)

only_in_pub = pub_ids - sheet_ids
only_in_sheet = sheet_ids - pub_ids

print(f"Only in Published CSV: {len(only_in_pub)} IDs: {sorted(list(only_in_pub))[:10]}")
print(f"Only in Sheet 1iJIr2v...: {len(only_in_sheet)} IDs: {sorted(list(only_in_sheet))[:10]}")
