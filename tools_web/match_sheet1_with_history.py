import json
from google.oauth2.service_account import Credentials
import gspread

with open('config.json') as f:
    config = json.load(f)

SPREADSHEET_ID = config.get('SPREADSHEET_ID')
SERVICE_ACCOUNT  = config.get('SERVICE_ACCOUNT_FILE', 'service-account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
gc = gspread.authorize(creds)

sh = gc.open_by_key(SPREADSHEET_ID)

# Read Sheet 1 (first tab)
ws1 = sh.get_worksheet(0)
rows1 = ws1.get_all_values()

# Let's collect Doc Name mappings from ALL worksheets that have it
doc_mappings = {}
for ws in sh.worksheets():
    # Only read sheets that might have Doc Name
    if ws.title.startswith('Haiku_Scan') or ws.title == 'DB_Mirror':
        rows = ws.get_all_values()
        if not rows:
            continue
        headers = rows[0]
        doc_idx = None
        title_idx = None
        for idx, h in enumerate(headers):
            if 'doc' in h.lower() or 'file' in h.lower():
                doc_idx = idx
            if 'title_th' in h.lower() or 'title th' in h.lower() or 'title (th)' in h.lower():
                title_idx = idx
        
        if doc_idx is not None and title_idx is not None:
            print(f"Reading mappings from worksheet '{ws.title}' (Title index: {title_idx}, Doc index: {doc_idx})")
            for r in rows[1:]:
                if len(r) > max(title_idx, doc_idx):
                    title = r[title_idx].strip()
                    doc = r[doc_idx].strip()
                    if title and doc:
                        doc_mappings[title] = doc

print("-" * 80)
print(f"Total mappings collected: {len(doc_mappings)}")
print("-" * 80)

mismatches = [
    ('TSP-LST-NAT-029', 'ลายใบไม้สามแฉกก้านคดกับกากบาทรูปใบกลาง'),
    ('TSP-LST-NAT-031', 'ลายใบไม้สามแฉกบนกระเบื้องโบราณ'),
    ('TSP-LST-NAT-033', 'ลายดอกจันกากบาทกลีบพัด'),
    ('TSP-LST-NAT-039', 'ลายดอกจันกังหันเวียนสลับสี'),
    ('TSP-LST-NAT-040', 'ลายขิดดอกพิกุล'),
    ('TSP-LST-NAT-043', 'ลายแตงโม'),
    ('TSP-LST-FAU-006', 'ครุฑปูนปั้น'),
    ('TSP-LST-FAU-008', 'องค์มกรคายนาค'),
    ('TSP-LST-FAU-016', 'ลายมังกรนูนต่ำ'),
    ('TSP-LST-FAU-017', 'ลายขิดนาคและโคมเรขาคณิต'),
    ('TSP-LST-FAU-018', 'ลายม้า'),
    ('TSP-LST-FAU-019', 'ลายขิดมกรและโคมเรขาคณิต'),
    ('TSP-LST-FAU-021', 'ลายขิดคชลักษณ์และโคมเรขาคณิต'),
    ('TSP-LST-FAU-022', 'ลายนกคุ้ม'),
    ('TSP-LST-FAU-023', 'ลายขิดกนกสัตวลักษณ์เรขาคณิต'),
    ('TSP-LST-FAU-024', 'ลายขิดก้างปลาและโคมเรขาคณิต'),
    ('TSP-LST-FAU-025', 'ลายช้าง'),
    ('TSP-LST-GEO-009', 'ลายคลื่นและลายก้านขดบนเครื่องปั้นดินเผา'),
    ('TSP-LST-GEO-012', 'ลายแถบสามเหลี่ยมปะสลับสี'),
    ('TSP-LST-GEO-014', 'ลายหน้าหมอนขิดไทพวน'),
    ('TSP-LST-GEO-015', 'ลายสามเหลี่ยมฟันปลา'),
    ('TSP-LST-GEO-017', 'ลายหน้าหมอนดอกแก้วไทพวน'),
    ('TSP-LST-GEO-018', 'ลายขิดสร้อยสา'),
    ('TSP-LST-GEO-020', 'ลายขิดดอกในตารางสี่เหลี่ยม'),
    ('TSP-LST-GEO-022', 'ดาวเพดานไม้แกะสลักประดับกระจก'),
    ('TSP-LST-SAC-012', 'จั่วภควัมหน้าพรหม'),
    ('TSP-LST-SAC-020', 'เม็ดสร้อยสังวาลพระพุทธชินราช')
]

for sid, title in mismatches:
    doc = doc_mappings.get(title)
    if doc:
        p_name = doc.split('_')[0]
        print(f"✅ {sid} | Title: '{title}' -> Drive Folder: '{p_name}' | Doc: '{doc}'")
    else:
        # Try fuzzy match
        found = False
        for m_title, m_doc in doc_mappings.items():
            if title in m_title or m_title in title:
                p_name = m_doc.split('_')[0]
                print(f"⚠️ {sid} | Title: '{title}' (Fuzzy Match '{m_title}') -> Drive Folder: '{p_name}' | Doc: '{m_doc}'")
                found = True
                break
        if not found:
            print(f"❌ {sid} | Title: '{title}' -> No match found in any sheet history!")
