"""
line_dashboard.py — Unified Control Panel
เปิด http://localhost:5556 เพื่อจัดการ pipeline ทั้งหมดในที่เดียว
"""
import json, subprocess, threading, queue, os, socket, signal, time, re
from flask import Flask, jsonify, request, Response, stream_with_context
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

with open('config.json', 'r') as f:
    config = json.load(f)

SPREADSHEET_ID = config['SPREADSHEET_ID']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds  = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
gc     = gspread.authorize(creds)
sh     = gc.open_by_key(SPREADSHEET_ID)

app = Flask(__name__)
log_queue = queue.Queue()
running_proc = {}

def stream_script(name, cmd):
    def run():
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, bufsize=1, cwd=os.getcwd(), env=env)
        running_proc[name] = proc
        for line in proc.stdout:
            log_queue.put({'name': name, 'line': line.rstrip()})
        proc.wait()
        api_cache.clear()  # Clear cache so fresh data loads immediately after task finishes
        log_queue.put({'name': name, 'line': f'✅ {name} เสร็จแล้ว (exit {proc.returncode})', 'done': True})
        running_proc.pop(name, None)
    t = threading.Thread(target=run, daemon=True)
    t.start()

api_cache = {}
def get_cached(key, ttl, fetch_func):
    now = time.time()
    if key in api_cache and now - api_cache[key]['time'] < ttl:
        return api_cache[key]['data']
    data = fetch_func()
    api_cache[key] = {'time': now, 'data': data}
    return data

@app.route('/api/stats')
def stats():
    def fetch():
        try:
            ws   = sh.worksheet('LINE_Review')
            rows = ws.get_all_values()
            if len(rows) < 2: return dict(approved=0, rejected=0, pending=0, total=0)
            data = rows[1:]
            return dict(
                approved=sum(1 for r in data if r and r[0]=='APPROVED'),
                rejected=sum(1 for r in data if r and r[0]=='REJECTED'),
                pending =sum(1 for r in data if r and r[0]=='PENDING'),
                total   =len(data)
            )
        except: return dict(approved=0, rejected=0, pending=0, total=0)
    return jsonify(get_cached('stats', 15, fetch))

@app.route('/api/asset_stats')
def asset_stats():
    def fetch():
        try:
            ws   = sh.worksheet('Asset_Map')
            rows = ws.get_all_values()
            if len(rows) < 2: return dict(complete=0, missing=0, new=0, total=0, missing_list=[])
            h = rows[0]
            si = next((i for i,v in enumerate(h) if 'status' in v.lower()), -1)
            data = rows[1:]
            missing_list = [r[0] for r in data if len(r)>si and r[si]=='MISSING' and len(r)>0] if si >= 0 else []
            return dict(
                complete=sum(1 for r in data if si>=0 and len(r)>si and r[si]=='COMPLETE'),
                missing =sum(1 for r in data if si>=0 and len(r)>si and r[si]=='MISSING'),
                new     =sum(1 for r in data if si>=0 and len(r)>si and r[si]=='NEW'),
                total   =len(data),
                missing_list=missing_list
            )
        except: return dict(complete=0, missing=0, new=0, total=0, missing_list=[])
    return jsonify(get_cached('asset_stats', 15, fetch))

@app.route('/api/db_stats')
def db_stats():
    def fetch():
        try:
            ws = sh.get_worksheet(0)
            rows = ws.get_all_values()
            if len(rows) < 2: return dict(total=0, nature=0, fauna=0, geo=0, sacred=0, scanned=0, pending=0)
            data = [r for r in rows[1:] if len(r) > 0 and r[0].strip() and not r[0].strip().startswith('#')]
            nature = sum(1 for r in data if len(r)>3 and 'Nature' in r[3])
            fauna = sum(1 for r in data if len(r)>3 and 'Fauna' in r[3])
            geo = sum(1 for r in data if len(r)>3 and 'Geometric' in r[3])
            sacred = sum(1 for r in data if len(r)>3 and 'Sacred' in r[3])
            
            scanned_files = set(r[17] for r in rows[1:] if len(r) > 17 and r[17].strip() and r[17].strip() != 'N/A')
            try:
                ws_ig = sh.worksheet('Ignored_Docs')
                for r in ws_ig.get_all_values()[1:]:
                    if r and r[0]: scanned_files.add(r[0])
            except: pass
            
            scanned = len(scanned_files)
            pending = 0
            try:
                drive_creds = Credentials.from_service_account_file('service-account.json', scopes=['https://www.googleapis.com/auth/drive.readonly'])
                drive_service = build('drive', 'v3', credentials=drive_creds)
                drive_folder_id = config.get('LINE_DOC_FOLDER_ID') or config.get('DRIVE_FOLDER_ID')
                q = (f"'{drive_folder_id}' in parents and trashed = false "
                     "and mimeType != 'application/pdf' "
                     "and mimeType != 'image/jpeg' and mimeType != 'image/png' "
                     "and not name contains '.ai' "
                     "and (name contains 'TSPL' or name contains '2025_' or name contains '2026_')")
                items = drive_service.files().list(q=q, fields="files(id)").execute().get('files', [])
                pending = max(0, len(items) - scanned)
            except: pass
            return dict(total=len(data), nature=nature, fauna=fauna, geo=geo, sacred=sacred, scanned=scanned, pending=pending)
        except: return dict(total=0, nature=0, fauna=0, geo=0, sacred=0, scanned=0, pending=0)
    return jsonify(get_cached('db_stats', 20, fetch))

@app.route('/api/scan_duplicates')
def scan_duplicates():
    try:
        ws = sh.get_worksheet(0)
        rows = ws.get_all_values()
        if len(rows) < 2: return jsonify(groups=[])
        
        groups = {}
        for idx, r in enumerate(rows[1:], start=2): # 1-based index in sheet
            if not r or not r[0].strip() or r[0].strip().startswith('#'): continue
            title = r[1] if len(r) > 1 else 'N/A'
            sid = r[0]
            fname = r[17] if len(r) > 17 else 'N/A'
            ts = r[18] if len(r) > 18 else 'N/A'
            
            ct = re.sub(r'^ลาย', '', title.strip()).strip().lower()
            ct = re.sub(r'\s+', '', ct)
            if not ct: continue
            
            if ct not in groups: groups[ct] = []
            groups[ct].append({
                'row_index': idx,
                'symbol_id': sid,
                'title_th': title,
                'filename': fname,
                'timestamp': ts
            })
            
        dup_groups = [list(g) for ct, g in groups.items() if len(g) > 1]
        return jsonify(groups=dup_groups)
    except Exception as e:
        return jsonify(groups=[], error=str(e))

@app.route('/api/delete_row', methods=['POST'])
def delete_row():
    data = request.json
    sid = data.get('symbol_id')
    ts = data.get('timestamp')
    try:
        ws = sh.get_worksheet(0)
        rows = ws.get_all_values()
        for idx, r in enumerate(rows, start=1):
            if len(r) > 18 and r[0] == sid and r[18] == ts:
                ws.delete_rows(idx)
                api_cache.clear()
                return jsonify(ok=True)
        return jsonify(ok=False, error="ไม่พบรายการที่ต้องการลบ")
    except Exception as e:
        return jsonify(ok=False, error=str(e))

@app.route('/api/check_assets')
def check_assets():
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'tools_web/asset_manager.py', 'check'],
            capture_output=True, text=True, timeout=60
        )
        data = json.loads(result.stdout.strip().split('\n')[-1])
        return jsonify(items=data)
    except Exception as e:
        return jsonify(items=[], error=str(e))

@app.route('/api/list_backups')
def list_backups():
    import glob
    files = sorted(glob.glob('tools_web/backups/asset_backup_*.json'), reverse=True)
    return jsonify(backups=[os.path.basename(f) for f in files[:10]])

@app.route('/api/run/<step>', methods=['POST'])
def run_step(step):
    cmds = {
        'sync':           ['python3', 'pipeline_line/line_sync.py'],
        'classify':       ['python3', 'pipeline_line/line_classify.py'],
        'finalize':       ['python3', 'pipeline_line/line_finalize.py'],
        'extract':        ['python3', 'tools_web/semiotic_extractor.py'],
        'backup':         ['python3', 'tools_web/db_mirror.py'],
        'deploy':         ['bash',    'tools_web/deploy.command'],
        'fix_links':      ['python3', 'tools_web/fix_footer_links.py'],
        'link_assets':    ['python3', 'tools_web/asset_manager.py', 'link'],
        'download_assets':['python3', 'tools_web/asset_manager.py', 'download'],
        'rollback_assets':['python3', 'tools_web/asset_manager.py', 'rollback'],
        'confirm_assets': ['python3', 'tools_web/asset_manager.py', 'confirm'],
        'optimize_images':['python3', 'tools_web/optimize_images.py'],
    }
    if step not in cmds: return jsonify(ok=False, error='unknown step'), 400
    if step in running_proc: return jsonify(ok=False, error='กำลังรันอยู่แล้ว')
    stream_script(step, cmds[step])
    return jsonify(ok=True)

@app.route('/api/cancel/<step>', methods=['POST'])
def cancel_step(step):
    proc = running_proc.get(step)
    if proc:
        try:
            os.kill(proc.pid, signal.SIGTERM)
            log_queue.put({'name': step, 'line': f'🛑 ยกเลิกคำสั่ง {step} แล้ว', 'done': True})
            running_proc.pop(step, None)
            return jsonify(ok=True)
        except Exception as e:
            return jsonify(ok=False, error=str(e))
    return jsonify(ok=False, error="Process not running")

@app.route('/api/start_review', methods=['POST'])
def start_review():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', 5555)) == 0:
            return jsonify(ok=True, message="Review Server is already running")
    
    env = os.environ.copy()
    subprocess.Popen(['python3', 'pipeline_line/line_review.py'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jsonify(ok=True, message="Started Review Server on port 5555")

@app.route('/api/clear_sheet', methods=['POST'])
def clear_sheet():
    try:
        log_queue.put({'name': 'clear_sheet', 'line': 'กำลังล้างข้อมูลใน Sheet...'})
        worksheet = sh.get_worksheet(0)
        worksheet.clear()
        headers = [
            'symbol_id', 'title_th', 'title_en',
            'category', 'location', 'confidence', 'ethics',
            'connotation_th', 'connotation_en',
            'protocol_preserve', 'protocol_do_not',
            'morphemes_th', 'morphemes_en',
            'tags',
            'img_main', 'img_vector', 'img_context',
            'source_filename', 'col_19',
            'source_link'
        ]
        worksheet.append_row(headers)
        log_queue.put({'name': 'clear_sheet', 'line': '✅ ล้างข้อมูลและใส่ Header ใหม่เรียบร้อยแล้ว', 'done': True})
        return jsonify(ok=True)
    except Exception as e:
        log_queue.put({'name': 'clear_sheet', 'line': f'❌ Error: {str(e)}', 'done': True})
        return jsonify(ok=False, error=str(e)), 500

@app.route('/api/logs')
def logs():
    def generate():
        yield 'data: {"line":"🟢 Dashboard พร้อมรับ log..."}\n\n'
        while True:
            try:
                msg = log_queue.get(timeout=30)
                yield f'data: {json.dumps(msg, ensure_ascii=False)}\n\n'
            except queue.Empty:
                yield 'data: {"line":"⏳ รอ..."}\n\n'
    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/')
def index():
    try:
        with open('pipeline_line/dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading template: {e}"

if __name__ == '__main__':
    print("=" * 50)
    print("  LINE Archive Dashboard")
    print("=" * 50)
    print(f"\n  ✅ เปิด http://localhost:5556")
    print(f"  Ctrl+C เพื่อปิด\n")
    app.run(host='0.0.0.0', port=5556, debug=False, threaded=True)
