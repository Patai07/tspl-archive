import csv
import urllib.request
import os

web_dir = "/Users/phu/Desktop/งานพี่กบ/Web"
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv"

print("Fetching and checking Google Sheet CSV...")

try:
    response = urllib.request.urlopen(csv_url)
    csv_content = response.read().decode('utf-8')
except Exception as e:
    print(f"Error fetching CSV: {e}")
    exit(1)

reader = csv.DictReader(csv_content.splitlines())
missing_count = 0
total_count = 0

cols = ['Image Main', 'Image Vector', 'Image Mid', 'Image Detail', 'Image Extra1', 'Image Extra2']

for row in reader:
    sid = row.get('Symbol ID', '').strip()
    if not sid or sid.startswith('#'):
        continue
    total_count += 1
    
    for col in cols:
        val = row.get(col, '').strip()
        if val:
            full_path = os.path.join(web_dir, val)
            if not os.path.exists(full_path):
                print(f"❌ [{sid}] {row.get('Title (TH)', '')} - Missing {col}: {val}")
                missing_count += 1

print(f"Done. Checked {total_count} records. Found {missing_count} missing images.")
