import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

SPREADSHEET_ID = config.get('SPREADSHEET_ID')
PROD_SPREADSHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)

def inspect_sheet(sheet_id, name):
    print(f"\n--- Inspecting {name} ({sheet_id}) ---")
    try:
        sh = gc.open_by_key(sheet_id)
        for ws in sh.worksheets():
            rows = ws.get_all_values()
            print(f"Worksheet '{ws.title}': {len(rows)} rows")
            if not rows:
                continue
            headers = rows[0]
            print(f"  Headers: {headers}")
            # Find which column contains 'Doc Name' or 'Document'
            doc_col_idx = None
            for idx, h in enumerate(headers):
                if 'doc' in h.lower() or 'file' in h.lower():
                    doc_col_idx = idx
            
            # Print sample rows with Doc Name if found
            if doc_col_idx is not None:
                print(f"  Found Doc column at index {doc_col_idx} ('{headers[doc_col_idx]}')")
                count = 0
                for r in rows[1:]:
                    if len(r) > doc_col_idx and r[doc_col_idx].strip():
                        sid = r[0] if len(r) > 0 else ''
                        title = r[1] if len(r) > 1 else ''
                        doc_val = r[doc_col_idx]
                        print(f"    ID: {sid} | Title: '{title}' | Doc: '{doc_val}'")
                        count += 1
                        if count >= 10:
                            print("    ...")
                            break
    except Exception as e:
        print(f"Error inspecting {name}: {e}")

inspect_sheet(SPREADSHEET_ID, "Staging Sheet (Sheet 1)")
inspect_sheet(PROD_SPREADSHEET_ID, "Production Sheet (Sheet 2)")
