import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

with open('config.json', 'r') as f:
    config = json.load(f)

creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/drive.readonly'])
drive_service = build('drive', 'v3', credentials=creds)

DRIVE_ASSET_ROOT = '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt'

cats = drive_service.files().list(
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false",
    fields="files(id,name,mimeType)", pageSize=10
).execute().get('files', [])

for cat in cats:
    print(f"Cat: {cat['name']}")
    if cat['mimeType'] == 'application/vnd.google-apps.folder':
        patterns = drive_service.files().list(
            q=f"'{cat['id']}' in parents and trashed=false",
            fields="files(id,name,mimeType)", pageSize=5
        ).execute().get('files', [])
        for p in patterns:
            print(f"  -> Pattern: {p['name']}")
