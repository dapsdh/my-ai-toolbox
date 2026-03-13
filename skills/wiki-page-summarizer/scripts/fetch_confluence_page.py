#!/usr/bin/env python3
"""
Confluence 페이지를 REST API로 조회 (Basic auth: 이메일 + API 토큰).
환경 변수: 프로젝트 루트(.ai)의 .env — ATLASSIAN_BASE_URL, ATLASSIAN_USER, ATLASSIAN_API_TOKEN
사용법:
  fetch_confluence_page.py <페이지ID 또는 URL>
    → 해당 페이지만 가져옴.
  fetch_confluence_page.py <페이지ID 또는 URL> --with-children
    → 전달한 링크의 하위 폴더를 포함해 재귀적으로 모든 페이지를 가져옴 (직접 하위 + 그 하위의 하위 + … 전부).
"""
import json
import os
import re
import sys
import html
from base64 import b64encode
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote

def _load_dotenv():
    base = Path(__file__).resolve().parent
    skill_dir = base.parent
    root = skill_dir.parent.parent
    env_path = root / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and k not in os.environ:
                    os.environ[k] = v

_load_dotenv()

BASE = (os.environ.get("ATLASSIAN_BASE_URL") or "").rstrip("/")
WIKI_BASE = f"{BASE}/wiki" if "/wiki" not in BASE else BASE
USER = os.environ.get("ATLASSIAN_USER", "").strip()
TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "").strip()


def _auth_header():
    auth = b64encode(f"{USER}:{TOKEN}".encode()).decode()
    return {"Accept": "application/json", "Authorization": f"Basic {auth}"}


def get_page(page_id: str) -> dict:
    url = f"{WIKI_BASE}/rest/api/content/{page_id}?expand=body.storage,version"
    req = Request(url, headers=_auth_header())
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get_child_page_ids(page_id: str) -> list:
    """직접 하위 페이지 (id, title) 목록 반환. 페이지네이션으로 전부 수집."""
    out = []
    start = 0
    limit = 25
    while True:
        url = f"{WIKI_BASE}/rest/api/content/{page_id}/child/page?limit={limit}&start={start}"
        req = Request(url, headers=_auth_header())
        with urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        results = data.get("results") or []
        for item in results:
            if item.get("type") == "page":
                out.append((item["id"], item.get("title", "")))
        if len(results) < limit:
            break
        start += len(results)
        if start >= data.get("size", 0):
            break
    return out


def strip_html_to_text(html_str: str) -> str:
    if not html_str:
        return ""
    # 간단한 태그 제거 및 디코딩
    text = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", r"\n## \1\n", html_str, flags=re.DOTALL | re.I)
    text = re.sub(r"<p>(.*?)</p>", r"\1\n", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<tr[^>]*>(.*?)</tr>", r"\1\n", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<td[^>]*>(.*?)</td>", r"\1\t", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<th[^>]*>(.*?)</th>", r"\1\t", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def _page_to_output(data: dict, page_id: str, label: str = "") -> str:
    title = data.get("title", "")
    ver = data.get("version", {})
    ver_num = ver.get("number", "")
    body = (data.get("body") or {}).get("storage") or {}
    storage_val = body.get("value", "")
    plain = strip_html_to_text(storage_val)
    head = f"제목: {title}\n페이지 ID: {page_id} (버전 {ver_num})"
    if label:
        head = f"[{label}]\n{head}"
    return f"{head}\n\n--- 본문 ---\n\n{plain}"


MAX_DEPTH = 20  # 재귀 깊이 상한 (무한 루프 방지)


def _fetch_with_children_recursive(page_id: str, path_label: str, depth: int) -> None:
    """페이지 내용이 없더라도 자식이 있다면 끝까지 재귀적으로 탐색합니다."""
    if depth > MAX_DEPTH:
        return

    # 1. 현재 페이지 정보 가져오기 (제목 확인용)
    try:
        data = get_page(page_id)
        title = data.get("title", "제목 없음")
        
        # 본문 출력 (내용이 없어도 제목과 ID는 출력해서 계층 구조를 보여줌)
        print("\n\n" + "=" * 60)
        print(_page_to_output(data, page_id, path_label))
        
    except Exception as e:
        # 현재 페이지를 가져오는 데 실패해도(예: 권한), 자식 페이지는 시도해볼 수 있도록 pass
        print(f"\n[알림] 페이지 {page_id} 정보를 읽지 못했습니다. (하위 탐색 지속)", file=sys.stderr)

    # 2. 자식 페이지 목록 가져오기 (이 부분이 '폴더' 내부로 들어가는 핵심)
    try:
        children = get_child_page_ids(page_id)
        
        if not children:
            return # 더 이상 하위가 없으면 종료

        for i, (cid, ctitle) in enumerate(children, 1):
            # 다음 계층으로 진입
            sub_path = f"{path_label} > {i}. {ctitle}" if path_label else f"{i}. {ctitle}"
            _fetch_with_children_recursive(cid, sub_path, depth + 1)
            
    except Exception as e:
        print(f"!!! {page_id}의 하위 목록을 가져오지 못했습니다: {e}", file=sys.stderr)


def main():
    args = [a for a in sys.argv[1:] if a.strip()]
    with_children = "--with-children" in args
    args = [a for a in args if a != "--with-children"]
    raw = " ".join(args).strip()
    if not raw:
        print("Usage: fetch_confluence_page.py <page-id-or-url> [--with-children]", file=sys.stderr)
        print("  --with-children: 전달한 링크의 하위 폴더 포함, 재귀적으로 모든 페이지 조회", file=sys.stderr)
        sys.exit(2)
    match = re.search(r"/pages/(\d+)", raw) or re.search(r"^(\d+)$", raw)
    page_id = match.group(1) if match else raw
    if not USER or not TOKEN:
        print("ATLASSIAN_USER와 ATLASSIAN_API_TOKEN을 .env 또는 환경 변수에 설정하세요.", file=sys.stderr)
        sys.exit(1)
    try:
        if with_children:
            _fetch_with_children_recursive(page_id, "루트 페이지", depth=0)
        else:
            data = get_page(page_id)
            print(_page_to_output(data, page_id, "본문"))
    except HTTPError as e:
        if e.code in (401, 403):
            print("인증 실패: ATLASSIAN_USER, ATLASSIAN_API_TOKEN을 확인하세요.", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"연결 오류: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Windows 콘솔에서 이모지 등 UTF-8 출력 시 cp949 오류 방지
    if hasattr(sys.stdout, "buffer"):
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass
    main()
