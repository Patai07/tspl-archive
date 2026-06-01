import csv

csv_path = "/Users/phu/Desktop/งานพี่กบ/Web/tspl_database - Master.csv"
with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Local csv file 'tspl_database - Master.csv' has {len(rows)} rows in total.")
non_empty = [r for r in rows if r.get('Symbol ID') and r.get('Symbol ID').strip()]
print(f"Number of rows with Symbol ID: {len(non_empty)}")
for idx, r in enumerate(non_empty[:10]):
    print(f"  {idx+1}. ID: {r['Symbol ID']} | Title: '{r['Title (TH)']}'")
