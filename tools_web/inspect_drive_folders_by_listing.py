import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

with open('config.json') as f:
    config = json.load(f)

DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)

cats = drive_svc.files().list(
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
    fields="files(id,name)"
).execute().get('files', [])

target_folders = ['ครุฑ', 'ครุฑแบก', 'ครุฑไม้จำหลัก', '010หน้าบันลูกฟักหน้าพรหม ', '010หน้าบันลูกฟักหน้าพรหม']

for cat in cats:
    resp = drive_svc.files().list(
        q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)"
    ).execute()
    for p in resp.get('files', []):
        if p['name'].strip() in target_folders or any(t in p['name'] for t in target_folders):
            print(f"\n--- Files in Folder '{p['name']}' (ID: {p['id']}) ---")
            resp_files = drive_svc.files().list(
                q=f"'{p['id']}' in parents and trashed = false",
                fields="files(id,name,mimeType)"
            ).execute()
            for f in resp_files.get('files', []):
                print(f"  - Name: '{f['name']}' | Type: {f['mimeType']}")
