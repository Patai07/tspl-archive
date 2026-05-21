import json, os, re
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- CONFIG ---
with open('config.json', 'r') as f: config = json.load(f)
SERVICE_ACCOUNT_FILE = 'service-account.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']

def debug_names():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_svc = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    
    # 1. Get names from Sheet 1 (Column B - Title)
    sh = gc.open_by_key(config['SPREADSHEET_ID'])
    rows = sh.get_worksheet(0).get_all_values()
    sheet_titles = [r[1].strip() for r in rows[1:] if len(r) > 1 and r[1].strip()]
    
    # 2. Get names from Drive
    root_id = config['DRIVE_ASSET_ROOT']
    cats = drive_svc.files().list(q=f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false").execute().get('files', [])
    
    drive_names = []
    for c in cats:
        subs = drive_svc.files().list(q=f"'{c['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false", pageSize=20).execute().get('files', [])
        for s in subs:
            drive_names.append(s['name'].strip())
            if len(drive_names) >= 10: break
        if len(drive_names) >= 10: break
    
    print("\n--- DETAILED TITLES COMPARISON ---")
    print(f"Sheet 1 Titles (First 10): {sheet_titles[:10]}")
    print(f"Drive Folders (First 10): {drive_names}")
    
    # Check if any drive names exist in sheet titles
    match_count = 0
    for d in drive_names:
        d_clean = d.lower().replace(' ', '')
        matches = [s for s in sheet_titles if s.lower().replace(' ', '') == d_clean]
        if matches:
            match_count += 1
            print(f"✅ Match Found: '{d}' == '{matches[0]}'")
        else:
            print(f"❌ No Match for: '{d}'")

if __name__ == "__main__":
    debug_names()
