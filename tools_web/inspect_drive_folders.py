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

def inspect_folder(folder_name):
    # Find folder ID
    q = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resp = drive_svc.files().list(q=q, fields="files(id,name)").execute()
    files = resp.get('files', [])
    if not files:
        print(f"Folder '{folder_name}' not found!")
        return
    fid = files[0]['id']
    print(f"\n--- Files in Folder '{folder_name}' ({fid}) ---")
    
    # List files inside this folder
    resp_files = drive_svc.files().list(q=f"'{fid}' in parents and trashed = false", fields="files(id,name,mimeType)").execute()
    for f in resp_files.get('files', []):
        print(f"  - Name: '{f['name']}' | Type: {f['mimeType']}")

inspect_folder("ครุฑ")
inspect_folder("ครุฑแบก")
inspect_folder("ครุฑไม้จำหลัก")
inspect_folder("010หน้าบันลูกฟักหน้าพรหม ")
