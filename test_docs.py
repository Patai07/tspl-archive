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
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
    fields="files(id,name)", pageSize=50
).execute().get('files', [])

docs = []
for c in cats:
    children = drive_svc.files().list(
        q=f"'{c['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)", pageSize=100
    ).execute().get('files', [])
    for p in children:
        # find documents inside pattern folder
        files = drive_svc.files().list(
            q=f"'{p['id']}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder' and mimeType != 'image/jpeg' and mimeType != 'image/png'",
            fields="files(id,name,mimeType)", pageSize=50
        ).execute().get('files', [])
        for f in files:
            docs.append(f"{c['name']} / {p['name']} / {f['name']} ({f['mimeType']})")

print(f"Found {len(docs)} documents/other files:")
for d in docs:
    print(d)
