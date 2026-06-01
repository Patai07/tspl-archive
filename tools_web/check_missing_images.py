import csv
import os

web_dir = "/Users/phu/Desktop/งานพี่กบ/Web"
csv_path = os.path.join(web_dir, "tspl_database - Master.csv")

print("Checking local images referenced in 'tspl_database - Master.csv'...")

if not os.path.exists(csv_path):
    print(f"Error: {csv_path} does not exist!")
    exit(1)

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    missing_count = 0
    total_count = 0
    for row in reader:
        sid = row.get('Symbol ID', '').strip()
        if not sid or sid.startswith('#'):
            continue
        total_count += 1
        
        # Check columns
        cols = ['Image Main', 'Image Vector', 'Image Context', 'Image Mid', 'Image Detail']
        for col in cols:
            val = row.get(col, '').strip()
            if val:
                full_path = os.path.join(web_dir, val)
                if not os.path.exists(full_path):
                    print(f"❌ [{sid}] {row.get('Title (TH)', '')} - Missing {col}: {val}")
                    missing_count += 1

print(f"Done. Checked {total_count} records. Found {missing_count} missing images.")
