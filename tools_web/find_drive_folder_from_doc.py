import csv
import urllib.request

csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv"

response = urllib.request.urlopen(csv_url)
csv_content = response.read().decode('utf-8')
lines = csv_content.splitlines()
reader = csv.DictReader(lines)

print("Row keys in Sheet:")
print(reader.fieldnames)
print("-" * 80)

for idx, row in enumerate(reader):
    sid = row.get('Symbol ID', '').strip()
    # Let's print the first 5 rows regardless
    if idx < 5:
        print(f"Row {idx}: {dict(row)}")
