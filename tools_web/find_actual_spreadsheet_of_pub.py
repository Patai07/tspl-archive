import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

with open('config.json') as f:
    config = json.load(f)

SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)
gc = gspread.authorize(creds)

print("Listing all Spreadsheets in Google Drive...")
q = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
resp = drive_svc.files().list(q=q, fields="files(id,name)").execute()
files = resp.get('files', [])

for f in files:
    print(f"\nSpreadsheet Name: '{f['name']}' | ID: {f['id']}")
    try:
        sh = gc.open_by_key(f['id'])
        for ws in sh.worksheets():
            # Count rows
            rows = ws.get_all_values()
            print(f"  - Worksheet: '{ws.title}' | GID: {ws.id} | Rows: {len(rows)}")
    except Exception as e:
        print(f"  Error: {e}")
