import csv
import urllib.request
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import re

with open('config.json') as f:
    config = json.load(f)

csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv"
DRIVE_ASSET_ROOT = config.get('DRIVE_ASSET_ROOT', '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
drive_svc = build('drive', 'v3', credentials=creds)

cats = drive_svc.files().list(
    q=f"'{DRIVE_ASSET_ROOT}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
    fields="files(id,name)"
).execute().get('files', [])

drive_folders_by_cat = {}
for cat in cats:
    cat_folders = []
    token = None
    while True:
        resp = drive_svc.files().list(
            q=f"'{cat['id']}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken,files(id,name)", pageSize=100, pageToken=token
        ).execute()
        for p in resp.get('files', []):
            cat_folders.append(p['name'])
        token = resp.get('nextPageToken')
        if not token: break
    drive_folders_by_cat[cat['name']] = cat_folders

# Fetch CSV
response = urllib.request.urlopen(csv_url)
csv_content = response.read().decode('utf-8')
reader = csv.DictReader(csv_content.splitlines())

mismatches = []
for row in reader:
    sid = row.get('Symbol ID', '').strip()
    if not sid or sid.startswith('#'):
        continue
    title = row.get('Title (TH)', '')
    cat_val = row.get('Category', '')
    mismatches.append((sid, title, cat_val))

# Map category values to Google Drive category folder prefixes
cat_map = {
    'Nature & Botany': '01-พันธุ์พฤกษา',
    'Fauna & Mythical': '02-สรรพสัตว์',
    'Geometric & Synthetic': '03-เรขาคณิต',
    'Sacred & Belief': '04-สัญลักษณืความเชื่อ'
}

def normalize(name):
    n = re.sub(r'^\d+', '', name.strip())
    n = re.sub(r'^[-.\s]+', '', n)
    n = re.sub(r'^ลาย', '', n)
    n = re.sub(r'กระหนก', 'กนก', n)
    n = re.sub(r'\s*\(.*?\)', '', n)
    return re.sub(r'\s+', '', n).lower()

print("Analyzing mismatches...")
for sid, title, cat_val in mismatches:
    norm = normalize(title)
    drive_cat_name = cat_map.get(cat_val)
    if not drive_cat_name:
        continue
    folders = drive_folders_by_cat.get(drive_cat_name, [])
    # Check if normalized title matches any of normalized folders
    matched = False
    for f in folders:
        if normalize(f) == norm:
            matched = True
            break
    if not matched:
        print(f"\n❌ ID: {sid} | Title: '{title}' | Category: '{cat_val}'")
        # List all folders in this category to help manual mapping
        print(f"  Drive folders in '{drive_cat_name}':")
        for f in sorted(folders):
            # Print if it has common characters or words
            common_chars = set(title) & set(f)
            if len(common_chars) > 3 or any(w in f for w in title.split()):
                print(f"    - '{f}'")
