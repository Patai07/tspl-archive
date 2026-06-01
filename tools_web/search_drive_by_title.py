import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re

with open('config.json') as f:
    config = json.load(f)

DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)

# We want to search for files or folders in Drive that contain certain words
keywords = ["ใบไม้", "สามแฉก", "กระเบื้อง", "ดอกจัน", "พิกุล", "แตงโม", "ครุฑ", "มกร", "มังกร", "นาค", "ม้า", "นกคุ้ม", "ก้างปลา", "ช้าง", "สร้อยสา", "จั่ว", "ภควัม", "สังวาล"]

print("Searching Google Drive for matching folders/files...")
for kw in keywords:
    q = f"name contains '{kw}' and trashed = false"
    resp = drive_svc.files().list(q=q, fields="files(id,name,mimeType,parents)").execute()
    files = resp.get('files', [])
    if files:
        print(f"\nKeyword: '{kw}' ({len(files)} results)")
        for f in files:
            print(f"  - Name: '{f['name']}' | Type: {f['mimeType']} | ID: {f['id']} | Parents: {f.get('parents')}")
