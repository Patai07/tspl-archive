import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

with open('config.json', 'r') as f: config = json.load(f)
SERVICE_ACCOUNT_FILE = 'service-account.json'
DRIVE_FOLDER_ID = config['DRIVE_FOLDER_ID']

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly'])
drive_service = build('drive', 'v3', credentials=creds)

items = drive_service.files().list(q=f"'{DRIVE_FOLDER_ID}' in parents and trashed = false", fields="files(id, name, mimeType)").execute().get('files', [])
print(f"Total files in drive: {len(items)}")
for i in items[:5]:
    print(i['name'])
