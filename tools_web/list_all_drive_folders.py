import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

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

all_names = []
for cat in cats:
    token = None
    while True:
        resp = drive_svc.files().list(
            q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token
        ).execute()
        for p in resp.get('files', []):
            all_names.append((cat['name'], p['name']))
        token = resp.get('nextPageToken')
        if not token: break

print(f"Total folders found: {len(all_names)}")
for cat_name, p_name in sorted(all_names, key=lambda x: (x[0], x[1])):
    print(f"Cat: {cat_name} | Folder: '{p_name}'")
