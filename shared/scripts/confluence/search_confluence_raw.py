# Fetch Confluence page 2015562714 and all children, search for connection pool
import os
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from base64 import b64encode

# .env 로드: 상위 디렉토리를 탐색해 .env 파일을 찾음
_d = Path(os.path.abspath(__file__)).parent
for _ in range(8):
    _env_path = _d / ".env"
    if _env_path.is_file():
        for line in _env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and k not in os.environ:
                    os.environ[k] = v
        break
    if _d == _d.parent:
        break
    _d = _d.parent

BASE = (os.environ.get("ATLASSIAN_BASE_URL") or "").rstrip("/")
WIKI = BASE + "/wiki" if "/wiki" not in BASE else BASE
USER = os.environ.get("ATLASSIAN_USER", "").strip()
TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "").strip()
auth = b64encode(f"{USER}:{TOKEN}".encode()).decode()
headers = {"Accept": "application/json", "Authorization": f"Basic {auth}"}

def get_page(pid):
    url = f"{WIKI}/rest/api/content/{pid}?expand=body.storage,version"
    with urlopen(Request(url, headers=headers), timeout=30) as r:
        return json.loads(r.read().decode())

def get_children(pid):
    out = []
    start = 0
    while True:
        url = f"{WIKI}/rest/api/content/{pid}/child/page?limit=25&start={start}"
        with urlopen(Request(url, headers=headers), timeout=30) as r:
            data = json.loads(r.read().decode())
        for item in (data.get("results") or []):
            if item.get("type") == "page":
                out.append((item["id"], item.get("title", "")))
        if len(data.get("results") or []) < 25:
            break
        start += 25
    return out

def search_in_html(html, page_id, title, results):
    terms = ["pool", "풀", "connection", "커넥션", "conn", "사이즈", "커넥션 풀"]
    for term in terms:
        pattern = re.compile(re.escape(term), re.I)
        for m in pattern.finditer(html):
            start = max(0, m.start() - 80)
            end = min(len(html), m.end() + 120)
            snippet = re.sub(r"<[^>]+>", " ", html[start:end])
            snippet = " ".join(snippet.split())[:250]
            results.append((page_id, title, term, snippet))

def collect_pages(pid, title, results, depth=0):
    if depth > 5:
        return
    try:
        data = get_page(pid)
        body = (data.get("body") or {}).get("storage") or {}
        html = body.get("value", "")
        search_in_html(html, pid, title, results)
        for cid, ctitle in get_children(pid):
            collect_pages(cid, ctitle, results, depth + 1)
    except Exception as e:
        results.append((pid, title, "error", str(e)))

root_id = "2015562714"
root_data = get_page(root_id)
root_title = root_data.get("title", "")
results = []
collect_pages(root_id, root_title, results)

out_path = Path(r"d:\Projects\Platform-API\confluence_pool_search.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("Connection pool related matches in page and children:\n\n")
    for page_id, title, term, snippet in results:
        if term == "error":
            f.write(f"[{title} (id={page_id})] Error: {snippet}\n\n")
        else:
            f.write(f"[{title} (id={page_id})] match '{term}':\n{snippet}\n\n")
if not any(r[2] != "error" for r in results):
    with open(out_path, "a", encoding="utf-8") as f:
        f.write("(No pool/connection/풀/커넥션 matches in page or children.)\n")
print("Wrote", out_path)
