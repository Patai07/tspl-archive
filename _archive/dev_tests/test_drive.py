import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

with open('config.json') as f:
    config = json.load(f)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)

DRIVE_ASSET_ROOT = '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt'

# List top-level folders
cats = drive_svc.files().list(
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false",
    fields="files(id,name,mimeType)", pageSize=50
).execute().get('files', [])

print("Top Level items:")
for c in cats:
    print(f" - {c['name']} ({c['mimeType']})")
    if c['mimeType'] == 'application/vnd.google-apps.folder':
        # list children
        children = drive_svc.files().list(
            q=f"'{c['id']}' in parents and trashed=false",
            fields="files(id,name,mimeType)", pageSize=10
        ).execute().get('files', [])
        for child in children:
            print(f"   * {child['name']} ({child['mimeType']})")
