"""
line_review.py — Local Review Server
=====================================
เปิด http://localhost:5555 เพื่อ review ผลการ classify
ใช้ keyboard กด A=Approve, R=Reject, E=Edit name
บันทึกผลลัพธ์กลับเข้า LINE_Review tab โดยอัตโนมัติ
"""

import json
import io
import base64
from flask import Flask, jsonify, request, send_file
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
import anthropic

# ─── CONFIG ───────────────────────────────────────────────────────────────────
with open('config.json', 'r') as f:
    config = json.load(f)

SERVICE_ACCOUNT_FILE = 'service-account.json'
SPREADSHEET_ID       = config['SPREADSHEET_ID']
REVIEW_TAB           = 'LINE_Review'
PORT                 = 5555

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
]

creds         = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)
gc            = gspread.authorize(creds)
sh            = gc.open_by_key(SPREADSHEET_ID)
rev_ws        = sh.worksheet(REVIEW_TAB)

anthropic_client = anthropic.Anthropic(api_key=config['ANTHROPIC_API_KEY'])
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

app = Flask(__name__)

# ─── API ──────────────────────────────────────────────────────────────────────
@app.route('/api/items')
def get_items():
    rows = rev_ws.get_all_values()
    if len(rows) < 2:
        return jsonify([])
    headers = rows[0]
    col = {h: i for i, h in enumerate(headers)}
    items = []
    for idx, row in enumerate(rows[1:], start=2):  # 1-indexed, row 1=header
        items.append({
            'row':       idx,
            'status':    row[col.get('STATUS', 0)]            if len(row) > col.get('STATUS', 0)    else '',
            'symbol':    row[col.get('haiku_symbol', 1)]      if len(row) > col.get('haiku_symbol', 1) else '',
            'confidence':row[col.get('confidence', 2)]        if len(row) > col.get('confidence', 2) else '',
            'override':  row[col.get('override_name', 3)]     if len(row) > col.get('override_name', 3) else '',
            'note':      row[col.get('haiku_note', 4)]        if len(row) > col.get('haiku_note', 4) else '',
            'filename':  row[col.get('img_real_name', 5)]     if len(row) > col.get('img_real_name', 5) else '',
            'ext':       row[col.get('img_extension', 6)]     if len(row) > col.get('img_extension', 6) else '',
            'view_link': row[col.get('img_view_link', 7)]     if len(row) > col.get('img_view_link', 7) else '',
            'file_id':   row[col.get('file_id', 9)]           if len(row) > col.get('file_id', 9)    else '',
        })
    return jsonify(items)

@app.route('/api/image/<file_id>')
def proxy_image(file_id):
    try:
        data = drive_service.files().get_media(fileId=file_id).execute()
        return send_file(io.BytesIO(data), mimetype='image/jpeg')
    except Exception as e:
        return str(e), 404

@app.route('/api/ask_haiku/<file_id>')
def ask_haiku(file_id):
    try:
        data = drive_service.files().get_media(fileId=file_id).execute()
        data_b64 = base64.standard_b64encode(data).decode('utf-8')
        prompt = (
            "รูปนี้คือลวดลายศิลปะไทยอะไร? หรือเป็นชิ้นส่วนอะไร? "
            "ตอบแค่ชื่อสั้นๆ ไม่ต้องอธิบายเพิ่ม เช่น 'ดอกพิกุล', 'ชิ้นส่วนเครื่องกระเบื้อง' "
            "แต่ถ้าดูไม่ออก หรือไม่ใช่ลวดลาย ให้ตอบว่า 'ไม่ใช่ลวดลาย'"
        )
        msg = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/jpeg", "data": data_b64
                    }},
                    {"type": "text", "text": prompt},
                ]
            }]
        )
        return jsonify({'result': msg.content[0].text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/review', methods=['POST'])
def submit_review():
    data     = request.json
    row      = data.get('row')
    status   = data.get('status')   # APPROVED / REJECTED
    override = data.get('override', '')
    try:
        rev_ws.update_cell(row, 1, status)      # col A = STATUS
        if override:
            rev_ws.update_cell(row, 4, override)  # col D = override_name
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return REVIEW_HTML

# ─── HTML UI ──────────────────────────────────────────────────────────────────
REVIEW_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LINE Image Review</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #0a0a0f;
    --surface:  #12121a;
    --card:     #1a1a26;
    --border:   #2a2a3a;
    --accent:   #7c6fff;
    --green:    #22c55e;
    --red:      #ef4444;
    --yellow:   #eab308;
    --text:     #e8e8f0;
    --muted:    #6b6b80;
    --radius:   16px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans Thai', sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── Header ── */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-shrink: 0;
  }
  header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent);
  }
  .stats {
    display: flex; gap: 16px; margin-left: auto;
    font-size: 0.82rem; color: var(--muted);
  }
  .stat { display: flex; align-items: center; gap: 6px; }
  .stat-dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot-green  { background: var(--green); }
  .dot-red    { background: var(--red); }
  .dot-yellow { background: var(--yellow); }

  /* ── Progress ── */
  .progress-bar {
    height: 3px;
    background: var(--border);
    flex-shrink: 0;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #a78bfa);
    transition: width 0.4s ease;
  }

  /* ── Main layout ── */
  main {
    display: flex;
    flex: 1;
    overflow: hidden;
    gap: 0;
  }

  /* ── Image panel ── */
  .img-panel {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #050508;
    position: relative;
    overflow: hidden;
  }
  .img-panel img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 8px;
    transition: opacity 0.2s;
  }
  .img-panel.loading img { opacity: 0.3; }
  .img-loader {
    position: absolute;
    font-size: 2rem;
    animation: spin 1s linear infinite;
    display: none;
  }
  .img-panel.loading .img-loader { display: block; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Nav arrows ── */
  .nav-arrow {
    position: absolute;
    top: 50%; transform: translateY(-50%);
    background: rgba(255,255,255,0.08);
    border: 1px solid var(--border);
    color: var(--text);
    width: 44px; height: 44px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-size: 1.2rem;
    transition: background 0.2s;
    backdrop-filter: blur(8px);
    z-index: 10;
  }
  .nav-arrow:hover { background: rgba(124,111,255,0.3); }
  .nav-prev { left: 16px; }
  .nav-next { right: 16px; }

  /* ── Side panel ── */
  .side-panel {
    width: 360px;
    flex-shrink: 0;
    background: var(--surface);
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .side-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px 20px;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
  }

  .counter {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 20px;
    letter-spacing: 0.05em;
  }

  .symbol-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 16px;
  }
  .symbol-label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }
  .symbol-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.4;
    margin-bottom: 10px;
  }
  .confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  .conf-high   { background: rgba(34,197,94,0.15);  color: var(--green);  }
  .conf-medium { background: rgba(234,179,8,0.15);  color: var(--yellow); }
  .conf-low    { background: rgba(239,68,68,0.15);  color: var(--red);    }

  .note-text {
    margin-top: 10px;
    font-size: 0.82rem;
    color: var(--muted);
    line-height: 1.6;
  }

  .filename-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 16px;
    font-size: 0.78rem;
    color: var(--muted);
    word-break: break-all;
    line-height: 1.5;
  }

  /* ── Edit field ── */
  .edit-section { margin-bottom: 16px; }
  .edit-section label {
    display: block;
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }
  .edit-section input {
    width: 100%;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    color: var(--text);
    font-family: 'IBM Plex Sans Thai', sans-serif;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
  }
  .edit-section input:focus { border-color: var(--accent); }

  /* ── Status indicator ── */
  .status-indicator {
    margin-bottom: 16px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 500;
    display: none;
  }
  .status-indicator.show { display: block; }
  .status-approved { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }
  .status-rejected { background: rgba(239,68,68,0.15); color: var(--red);   border: 1px solid rgba(239,68,68,0.3); }
  .status-pending  { background: rgba(124,111,255,0.1); color: var(--accent); border: 1px solid rgba(124,111,255,0.2); }

  /* ── Action buttons ── */
  .actions {
    padding: 16px 20px;
    border-top: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex-shrink: 0;
  }
  .btn-row { display: flex; gap: 10px; }
  .btn {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 12px;
    font-family: 'IBM Plex Sans Thai', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.18s ease;
  }
  .btn:active { transform: scale(0.97); }
  .btn-approve {
    background: rgba(34,197,94,0.2);
    color: var(--green);
    border: 1px solid rgba(34,197,94,0.4);
  }
  .btn-approve:hover { background: rgba(34,197,94,0.35); }
  .btn-reject {
    background: rgba(239,68,68,0.15);
    color: var(--red);
    border: 1px solid rgba(239,68,68,0.3);
  }
  .btn-reject:hover { background: rgba(239,68,68,0.3); }
  .btn-skip {
    background: var(--card);
    color: var(--muted);
    border: 1px solid var(--border);
  }
  .btn-skip:hover { border-color: var(--accent); color: var(--text); }

  .kbd {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.72rem;
    font-family: monospace;
  }

  /* ── Filter tabs ── */
  .filter-tabs {
    display: flex;
    gap: 4px;
    padding: 10px 20px 0;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .filter-tab {
    padding: 8px 14px;
    font-size: 0.78rem;
    cursor: pointer;
    border-radius: 8px 8px 0 0;
    color: var(--muted);
    transition: all 0.15s;
    border: 1px solid transparent;
    border-bottom: none;
  }
  .filter-tab.active {
    color: var(--accent);
    background: var(--bg);
    border-color: var(--border);
  }

  /* ── Empty state ── */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--muted);
    gap: 12px;
    font-size: 0.9rem;
  }
  .empty-icon { font-size: 3rem; }
</style>
</head>
<body>

<header>
  <h1>🖼️ LINE Image Review</h1>
  <div class="stats">
    <div class="stat"><div class="stat-dot dot-green"></div><span id="count-approved">0 approved</span></div>
    <div class="stat"><div class="stat-dot dot-red"></div><span id="count-rejected">0 rejected</span></div>
    <div class="stat"><div class="stat-dot dot-yellow"></div><span id="count-pending">0 pending</span></div>
  </div>
</header>
<div class="progress-bar"><div class="progress-fill" id="progress" style="width:0%"></div></div>

<main>
  <div class="img-panel" id="imgPanel">
    <div class="img-loader">⏳</div>
    <button class="nav-arrow nav-prev" onclick="navigate(-1)">◀</button>
    <img id="mainImg" src="" alt="">
    <button class="nav-arrow nav-next" onclick="navigate(1)">▶</button>
  </div>

  <div class="side-panel">
    <div class="filter-tabs">
      <div class="filter-tab active" onclick="setFilter('all', this)">ทั้งหมด</div>
      <div class="filter-tab" onclick="setFilter('PENDING', this)">Pending</div>
      <div class="filter-tab" onclick="setFilter('APPROVED', this)">Approved</div>
      <div class="filter-tab" onclick="setFilter('REJECTED', this)">Rejected</div>
    </div>

    <div class="side-content">
      <div class="counter" id="counter">โหลด...</div>

      <div class="status-indicator" id="statusIndicator"></div>

      <div class="symbol-box">
        <div class="symbol-label">Haiku วิเคราะห์ว่า</div>
        <div class="symbol-name" id="symbolName">—</div>
        <span class="confidence-badge" id="confBadge">—</span>
        <div class="note-text" id="noteText"></div>
      </div>

      <div class="filename-box" id="filenameBox">—</div>

      <div class="edit-section">
        <label style="display:flex; justify-content:space-between; align-items:center;">
          แก้ไขชื่อ (ถ้า Haiku ผิด)
          <button type="button" onclick="callHaikuAgain()" style="cursor:pointer; background:var(--accent); color:white; border:none; border-radius:4px; padding:4px 8px; font-family:'IBM Plex Sans Thai'; font-size:0.7rem;">🤖 ให้ Haiku ดูอีกรอบ</button>
        </label>
        <input type="text" id="overrideInput" placeholder="พิมพ์ชื่อลวดลายที่ถูกต้อง...">
      </div>
    </div>

    <div class="actions">
      <div class="btn-row">
        <button class="btn btn-approve" onclick="review('APPROVED')">
          ✅ Approve <span class="kbd">A</span>
        </button>
        <button class="btn btn-reject" onclick="review('REJECTED')">
          ❌ Reject <span class="kbd">R</span>
        </button>
      </div>
      <button class="btn btn-skip" onclick="navigate(1)">
        ข้ามไปก่อน <span class="kbd">Space</span>
      </button>
    </div>
  </div>
</main>

<script>
let items = [];
let filtered = [];
let currentIdx = 0;
let activeFilter = 'all';

async function loadItems() {
  const res = await fetch('/api/items');
  items = await res.json();
  applyFilter();
  updateStats();
}

function applyFilter() {
  if (activeFilter === 'all') filtered = [...items];
  else filtered = items.filter(i => i.status === activeFilter);
  currentIdx = 0;
  showItem(0);
}

function setFilter(f, el) {
  activeFilter = f;
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  applyFilter();
}

function showItem(idx) {
  if (filtered.length === 0) {
    document.getElementById('counter').textContent = 'ไม่มีรูปในตัวกรองนี้';
    document.getElementById('mainImg').src = '';
    document.getElementById('symbolName').textContent = '—';
    document.getElementById('confBadge').textContent = '—';
    document.getElementById('noteText').textContent = '';
    document.getElementById('filenameBox').textContent = '—';
    document.getElementById('overrideInput').value = '';
    return;
  }
  idx = Math.max(0, Math.min(idx, filtered.length - 1));
  currentIdx = idx;
  const item = filtered[idx];

  // counter
  document.getElementById('counter').textContent =
    `รูปที่ ${idx+1} / ${filtered.length}`;

  // progress
  const done = items.filter(i => i.status !== 'PENDING').length;
  document.getElementById('progress').style.width =
    (done / items.length * 100) + '%';

  // image
  const panel = document.getElementById('imgPanel');
  const img   = document.getElementById('mainImg');
  panel.classList.add('loading');
  img.src = '';
  if (item.file_id) {
    img.onload  = () => panel.classList.remove('loading');
    img.onerror = () => panel.classList.remove('loading');
    img.src = `/api/image/${item.file_id}`;
  }

  // symbol
  document.getElementById('symbolName').textContent = item.symbol || '—';
  document.getElementById('noteText').textContent   = item.note   || '';

  // confidence badge
  const badge = document.getElementById('confBadge');
  badge.textContent = { high:'🟢 High', medium:'🟡 Medium', low:'🔴 Low' }[item.confidence] || item.confidence;
  badge.className = 'confidence-badge conf-' + (item.confidence || 'low');

  // filename
  document.getElementById('filenameBox').textContent =
    item.filename || item.file_id || '—';

  // override
  document.getElementById('overrideInput').value = item.override || '';

  // status indicator
  const si = document.getElementById('statusIndicator');
  if (item.status && item.status !== 'PENDING') {
    si.textContent = item.status === 'APPROVED' ? '✅ Approved' : '❌ Rejected';
    si.className = 'status-indicator show status-' + item.status.toLowerCase();
  } else {
    si.className = 'status-indicator status-pending show';
    si.textContent = '⏳ รอ review';
  }
}

async function review(status) {
  if (!filtered.length) return;
  const item     = filtered[currentIdx];
  const override = document.getElementById('overrideInput').value.trim();

  // optimistic update
  item.status = status;
  if (override) item.override = override;

  // update in main items array
  const orig = items.find(i => i.row === item.row);
  if (orig) { orig.status = status; if (override) orig.override = override; }

  showItem(currentIdx);
  updateStats();

  // save to sheet
  await fetch('/api/review', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ row: item.row, status, override }),
  });

  // auto-advance to next pending
  const nextPending = filtered.findIndex((it, i) => i > currentIdx && it.status === 'PENDING');
  if (nextPending >= 0) { currentIdx = nextPending; showItem(currentIdx); }
  else { navigate(1); }
}

async function callHaikuAgain() {
  if (!filtered.length) return;
  const item = filtered[currentIdx];
  if (!item.file_id) return;
  
  const inp = document.getElementById('overrideInput');
  inp.value = "🤖 กำลังให้ Haiku วิเคราะห์...";
  inp.disabled = true;
  
  try {
    const res = await fetch('/api/ask_haiku/' + item.file_id);
    const data = await res.json();
    if (data.result) {
      inp.value = data.result;
    } else {
      inp.value = "❌ " + (data.error || "ดูไม่ออก");
    }
  } catch(e) {
    inp.value = "❌ เกิดข้อผิดพลาด";
  }
  inp.disabled = false;
}

function navigate(dir) {
  showItem(currentIdx + dir);
}

function updateStats() {
  const approved = items.filter(i => i.status === 'APPROVED').length;
  const rejected = items.filter(i => i.status === 'REJECTED').length;
  const pending  = items.filter(i => i.status === 'PENDING').length;
  document.getElementById('count-approved').textContent = `${approved} approved`;
  document.getElementById('count-rejected').textContent = `${rejected} rejected`;
  document.getElementById('count-pending').textContent  = `${pending} pending`;
}

// keyboard
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'a' || e.key === 'A') review('APPROVED');
  if (e.key === 'r' || e.key === 'R') review('REJECTED');
  if (e.key === ' ' || e.key === 'ArrowRight') { e.preventDefault(); navigate(1); }
  if (e.key === 'ArrowLeft') navigate(-1);
});

loadItems();
setInterval(updateStats, 30000);
</script>
</body>
</html>
"""

if __name__ == '__main__':
    print("=" * 50)
    print("  LINE Review Server")
    print("=" * 50)
    print(f"\n  ✅ เปิด http://localhost:{PORT} ในเบราว์เซอร์")
    print(f"  🎹 Keyboard: A=Approve  R=Reject  Space/→=Next  ←=Prev")
    print(f"  Ctrl+C เพื่อปิด\n")
    app.run(host='0.0.0.0', port=PORT, debug=False)
