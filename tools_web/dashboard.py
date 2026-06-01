import json, subprocess, threading, queue, os, signal, time, re, socket
from flask import Flask, jsonify, request, Response, stream_with_context
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

# --- 1. CONFIG ---
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '..', 'config.json')

with open(config_path, 'r') as f: config = json.load(f)

SPREADSHEET_ID = config.get('SPREADSHEET_ID')
PROD_SPREADSHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service-account.json'

app = Flask(__name__)
log_queue = queue.Queue()
running_proc = {}

# --- 2. DRIVE API HELPER ---
def get_drive_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def stream_script(name, cmd):
    def run():
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        # Run from Web root
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, bufsize=1, cwd=root_dir, env=env)
        running_proc[name] = proc
        for line in proc.stdout:
            log_queue.put({'name': name, 'line': line.rstrip()})
        proc.wait()
        log_queue.put({'name': name, 'line': f'✅ {name} เสร็จสิ้น (exit {proc.returncode})', 'done': True})
        running_proc.pop(name, None)
    t = threading.Thread(target=run, daemon=True)
    t.start()

@app.route('/api/scan_duplicates')
def scan_duplicates():
    import re
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.get_worksheet(0)
        rows = ws.get_all_values()
        if len(rows) < 2: return jsonify(groups=[])

        # หาตำแหน่งคอลัมน์ Drive Folder แบบ dynamic
        headers = rows[0] if rows else []
        drive_folder_idx = -1
        for i, h in enumerate(headers):
            if h.strip().lower() == 'drive folder':
                drive_folder_idx = i
                break

        groups = {}
        for idx, r in enumerate(rows[1:], start=2):
            if not r or not r[0].strip() or r[0].strip().startswith('#'): continue
            title = r[1] if len(r) > 1 else ''

            # ถ้ามีคอลัมน์ Drive Folder และมีค่า ให้ใช้เป็น canonical key แทน
            # เพราะชื่อโฟลเดอร์จาก Drive คือชื่อจริง ไม่ใช่ชื่อที่ Haiku ตั้ง
            drive_folder = ''
            if drive_folder_idx != -1 and len(r) > drive_folder_idx:
                drive_folder = r[drive_folder_idx].strip()

            if drive_folder:
                ct = re.sub(r'^ลาย', '', drive_folder).lower()
            else:
                ct = re.sub(r'^ลาย', '', title.strip()).lower()
            ct = re.sub(r'\s+', '', ct)
            if not ct: continue
            if ct not in groups: groups[ct] = []
            groups[ct].append({
                'row_index': idx, 'symbol_id': r[0],
                'title_th': title,
                'drive_folder': drive_folder,
                'timestamp': r[18] if len(r) > 18 else ''
            })
        dup_groups = [g for g in groups.values() if len(g) > 1]
        return jsonify(groups=dup_groups)
    except Exception as e:
        return jsonify(groups=[], error=str(e))

# --- 3. STATS CACHE ---
stats_cache = {'data': None, 'time': 0}

@app.route('/api/db_stats')
def db_stats():
    now = time.time()
    # Return cache if fresh (within 60 seconds)
    if stats_cache['data'] and now - stats_cache['time'] < 60:
        return jsonify(stats_cache['data'])

    try:
        # ดึงค่าจาก config
        PROD_SHEET_ID = config.get('DB_SOURCE_SPREADSHEET_ID')
        
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(PROD_SHEET_ID)
        ws = sh.worksheet('tspl_database')
        
        all_rows = ws.get_all_values()
        if len(all_rows) < 2:
            return jsonify(total=0, scanned=0, pending=0)
            
        # กรองเอาเฉพาะแถวที่มีข้อมูลจริง (ไม่ว่างและไม่ขึ้นต้นด้วย #)
        data = [r for r in all_rows[1:] if len(r) > 0 and r[0].strip() and not r[0].strip().startswith('#')]
        
        # คำนวณความคืบหน้า (Scanned = มีพาธรูปภาพในคอลัมน์ O)
        scanned_count = sum(1 for r in data if len(r) > 14 and r[14].strip())
        
        stats = {
            'total':   len(data),
            'scanned': scanned_count,
            'nature':  sum(1 for r in data if len(r) > 3 and 'Nature' in r[3]),
            'fauna':   sum(1 for r in data if len(r) > 3 and 'Fauna' in r[3]),
            'geo':     sum(1 for r in data if len(r) > 3 and 'Geometric' in r[3]),
            'sacred':  sum(1 for r in data if len(r) > 3 and 'Sacred' in r[3]),
            'pending': max(0, len(data) - scanned_count),
            'drive_pending': 0,
            'drive_pending_list': []
        }
        
        stats_cache.update({'data': stats, 'time': now})
        return jsonify(stats)
    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify(total=0, scanned=0, pending=0)

# --- 4. STAGING STATS ---
stats_staging_cache = {'data': None, 'time': 0}

@app.route('/api/db_stats_staging')
def db_stats_staging():
    now = time.time()
    if stats_staging_cache['data'] and now - stats_staging_cache['time'] < 60:
        return jsonify(stats_staging_cache['data'])
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID) # Sheet 1
        ws = sh.get_worksheet(0)
        rows = ws.get_all_values()
        if len(rows) < 2: return jsonify(total=0, scanned=0)
        
        data = [r for r in rows[1:] if len(r) > 0 and r[0].strip() and not r[0].strip().startswith('#')]
        scanned_count = sum(1 for r in data if len(r) > 17 and r[17].strip()) # ใน Sheet 1 คอลัมน์ 17 คือตัวบ่งชี้การสแกน
        
        stats = {
            'total':   len(data),
            'scanned': scanned_count,
            'pending': 0,
            'nature':  sum(1 for r in data if len(r) > 3 and 'Nature' in r[3]),
            'fauna':   sum(1 for r in data if len(r) > 3 and 'Fauna' in r[3]),
            'geo':     sum(1 for r in data if len(r) > 3 and 'Geometric' in r[3]),
            'sacred':  sum(1 for r in data if len(r) > 3 and 'Sacred' in r[3]),
        }
        
        # ตรวจสอบจำนวนโฟลเดอร์ใน Drive จริงๆ เพื่อดูว่ามีของใหม่ที่ยังไม่ได้ Scan ไหม
        try:
            drive_svc = get_drive_service()
            root_id = config.get('DRIVE_ASSET_ROOT')
            drive_folders_count = 0
            # สแกนโฟลเดอร์หมวดหมู่ก่อน
            cats = drive_svc.files().list(q=f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false").execute().get('files', [])
            for c in cats:
                # นับโฟลเดอร์ลายข้างในแต่ละหมวด
                subs = drive_svc.files().list(q=f"'{c['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false", pageSize=1000).execute().get('files', [])
                drive_folders_count += len(subs)
            
            # Pending Scan = จำนวนใน Drive - จำนวนที่อยู่ใน Sheet 1 แล้ว
            stats['pending'] = max(0, drive_folders_count - stats['total'])
        except Exception as drive_err:
            print(f"Drive Count Error: {drive_err}")

        stats_staging_cache.update({'data': stats, 'time': now})
        return jsonify(stats)
    except Exception as e:
        return jsonify(total=0, error=str(e))

@app.route('/staging')
def staging_dashboard():
    return open('tools_web/staging_ui.html', 'r', encoding='utf-8').read()

@app.route('/api/run/<step>', methods=['POST'])
def run_step(step):
    cmds = {
        'extract':        ['python3', 'tools_web/semiotic_extractor.py'],
        'merge_haiku':    ['python3', 'tools_web/merge_haiku_to_db.py'],
        'download_assets':['python3', 'tools_web/asset_manager.py', 'download'],
        'link_assets':    ['python3', 'tools_web/asset_manager.py', 'link'],
        'optimize_images':['python3', 'tools_web/optimize_images.py'],
        'mirror_db':      ['python3', 'tools_web/db_mirror.py'],
        'scan_duplicates':['python3', 'tools_web/scan_duplicates.py'],
        'deploy':         ['bash',    'tools_web/deploy.command'],
        'open_folder':    ['open',    'assets/images/database'],
    }
    if step not in cmds: return jsonify(ok=False, error='Unknown command'), 400
    if step in running_proc: return jsonify(ok=False, error='กำลังทำงานอยู่...')
    stream_script(step, cmds[step])
    return jsonify(ok=True)

@app.route('/api/stop/<step>', methods=['POST'])
def stop_step(step):
    proc = running_proc.get(step)
    if proc:
        try:
            # ใช้ os.kill เพื่อให้แน่ใจว่าหยุดทั้งกลุ่ม process (กรณีรัน shell script)
            os.kill(proc.pid, signal.SIGTERM)
            log_queue.put({'name': step, 'line': f'🛑 สั่งหยุดงาน {step} แล้ว', 'done': True})
            return jsonify(ok=True)
        except Exception as e:
            return jsonify(ok=False, error=str(e))
    return jsonify(ok=False, error='ไม่พบงานที่กำลังรันอยู่')

@app.route('/api/stop_all', methods=['POST'])
def stop_all():
    count = 0
    for name, proc in list(running_proc.items()):
        try:
            os.kill(proc.pid, signal.SIGTERM)
            count += 1
        except: pass
    running_proc.clear()
    log_queue.put({'name': 'system', 'line': f'🛑 สั่งหยุดงานทั้งหมด ({count} งาน) เรียบร้อยแล้ว', 'done': True})
    return jsonify(ok=True, count=count)

@app.route('/api/logs')
def logs():
    def generate():
        yield 'data: {"line":"🟢 ระบบ TSPL พร้อมทำงาน..."}\n\n'
        while True:
            try:
                msg = log_queue.get(timeout=30)
                yield f'data: {json.dumps(msg, ensure_ascii=False)}\n\n'
            except queue.Empty:
                yield 'data: {"line":"..."}\n\n'
    return Response(stream_with_context(generate()), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/')
def index():
    ui_path = os.path.join(os.path.dirname(__file__), 'dashboard_ui.html')
    with open(ui_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Get IDs from config
    s_id = (config.get('SPREADSHEET_ID') or '').strip()
    p_id = (config.get('DB_SOURCE_SPREADSHEET_ID') or '').strip()
    d_id = (config.get('DRIVE_ASSET_ROOT') or '1iSWw_Y3iUPwnuiy7kZWCksObFKETLlzt').strip()
    
    print(f"DEBUG: Rendering Dashboard with DRIVE_ID={d_id}")
    
    content = content.replace('{{SPREADSHEET_ID}}', s_id)
    content = content.replace('{{PROD_SPREADSHEET_ID}}', p_id)
    content = content.replace('{{DRIVE_ID}}', d_id)
    return content

if __name__ == '__main__':
    PORT = 5556
    print(f"TSPL Control Center running at http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
