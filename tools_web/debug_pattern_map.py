import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import re

with open('config.json') as f:
    config = json.load(f)

DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def normalize(name):
    n = re.sub(r'^\d+', '', name.strip())            # Remove ANY leading digits unconditionally
    n = re.sub(r'^[-.\s]+', '', n)                   # Remove dangling punctuation/spaces
    n = re.sub(r'^ลาย', '', n)                       # Remove leading ลาย
    n = re.sub(r'กระหนก', 'กนก', n)                    # Normalize spelling variations
    n = re.sub(r'\s*\(.*?\)', '', n)                 # Remove (English subtitle)
    return re.sub(r'\s+', '', n).lower()

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)

cats = drive_svc.files().list(
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
    fields="files(id,name)"
).execute().get('files', [])

drive_folders = {}
for cat in cats:
    token = None
    while True:
        resp = drive_svc.files().list(
            q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token
        ).execute()
        for p in resp.get('files', []):
            norm = normalize(p['name'])
            drive_folders[norm] = p['name']
        token = resp.get('nextPageToken')
        if not token: break

print("--- FOLDERS MAPPED FROM DRIVE ---")
for norm, name in sorted(drive_folders.items()):
    print(f"Norm: '{norm}' -> Name: '{name}'")
