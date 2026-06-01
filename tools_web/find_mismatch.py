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

def normalize(name):
    n = re.sub(r'^\d+', '', name.strip())            # Remove ANY leading digits unconditionally
    n = re.sub(r'^[-.\s]+', '', n)                   # Remove dangling punctuation/spaces
    n = re.sub(r'^ลาย', '', n)                       # Remove leading ลาย
    n = re.sub(r'กระหนก', 'กนก', n)                    # Normalize spelling variations
    n = re.sub(r'\s*\(.*?\)', '', n)                 # Remove (English subtitle)
    return re.sub(r'\s+', '', n).lower()

# Get Drive Folders
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

# Fetch CSV
try:
    response = urllib.request.urlopen(csv_url)
    csv_content = response.read().decode('utf-8')
except Exception as e:
    print(f"Error fetching CSV: {e}")
    exit(1)

reader = csv.DictReader(csv_content.splitlines())
sheet_records = []
for row in reader:
    sid = row.get('Symbol ID', '').strip()
    if not sid or sid.startswith('#'):
        continue
    sheet_records.append(row)

print(f"Total Sheet Records: {len(sheet_records)}")
print(f"Total Drive Folders: {len(drive_folders)}")

mismatches = []
for row in sheet_records:
    sid = row.get('Symbol ID', '')
    title = row.get('Title (TH)', '')
    norm = normalize(title)
    if norm not in drive_folders:
        mismatches.append((sid, title, norm))

print(f"\n--- MISMATCHES ({len(mismatches)}) ---")
for sid, title, norm in mismatches:
    print(f"ID: {sid} | Title: '{title}' | Norm: '{norm}'")
    # Find potential fuzzy matches in drive folders
    potentials = []
    for d_norm, d_name in drive_folders.items():
        # Check if the title shares keywords
        words = [w for w in re.split(r'[\s\-\:\(\)]+', title) if w and w != 'ลาย']
        matches_word = any(w in d_name for w in words)
        # Check if substring
        is_sub = norm in d_norm or d_norm in norm
        if matches_word or is_sub:
            potentials.append(d_name)
    if potentials:
        print(f"  └─ Potential Drive Folders: {list(set(potentials))}")
