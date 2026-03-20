#!/usr/bin/env python3
"""
Jira 이슈를 REST API로 조회 (Basic auth: 이메일 + API 토큰).
환경 변수: ATLASSIAN_BASE_URL, ATLASSIAN_USER(이메일), ATLASSIAN_API_TOKEN
- 프로젝트 루트(.ai)의 .env에서 로드
"""
import json
import os
import re
import sys
from base64 import b64encode
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Windows 콘솔 UTF-8 출력 (cp949 인코딩 오류 방지)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def _load_dotenv():
    d = Path(os.path.abspath(__file__)).parent
    for _ in range(8):
        env_path = d / ".env"
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
            return
        if d == d.parent:
            break
        d = d.parent

_load_dotenv()

ATLASSIAN_BASE = (os.environ.get("ATLASSIAN_BASE_URL") or "").rstrip("/")
ATLASSIAN_USER = os.environ.get("ATLASSIAN_USER", "").strip()
ATLASSIAN_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "").strip()


def get_issue(key: str) -> dict:
    url = f"{ATLASSIAN_BASE}/rest/api/3/issue/{key}"
    auth = b64encode(f"{ATLASSIAN_USER}:{ATLASSIAN_TOKEN}".encode()).decode()
    req = Request(url, headers={"Accept": "application/json", "Authorization": f"Basic {auth}"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def issue_to_text(data: dict) -> str:
    key = data.get("key", "")
    fields = data.get("fields") or {}
    summary = (fields.get("summary") or "").strip()
    status = (fields.get("status") or {}).get("name", "")
    priority = (fields.get("priority") or {}).get("name", "")
    assignee = (fields.get("assignee") or {}).get("displayName") or (fields.get("assignee") or {}).get("emailAddress", "")
    reporter = (fields.get("reporter") or {}).get("displayName") or ""
    desc = fields.get("description")
    if isinstance(desc, dict) and "content" in desc:
        parts = []
        for block in desc.get("content", []):
            if block.get("type") == "paragraph":
                for c in block.get("content", []):
                    if c.get("type") == "text":
                        parts.append((c.get("text") or "").strip())
        description_text = " ".join(parts)
    else:
        description_text = str(desc).strip() if desc else ""
    labels = ", ".join(fields.get("labels") or [])
    components = ", ".join((c.get("name") or "") for c in (fields.get("components") or []))
    subtasks = []
    for st in (fields.get("subtasks") or []):
        sk = st.get("key", "")
        sf = (st.get("fields") or {}).get("summary", "")
        ss = (st.get("fields") or {}).get("status") or {}
        ss_name = ss.get("name", "")
        subtasks.append(f"- [ ] {sk}: {sf} ({ss_name})")
    subtask_block = "\n".join(subtasks) if subtasks else "(없음)"
    return f"""키: {key}
제목: {summary}
상태: {status}
우선순위: {priority}
담당자: {assignee}
리포터: {reporter}
라벨: {labels}
컴포넌트: {components}

설명:
{description_text}

서브태스크:
{subtask_block}
"""


def main():
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print("Usage: fetch_jira_issue.py <issue-key-or-url>", file=sys.stderr)
        sys.exit(2)
    match = re.search(r"([A-Z][A-Z0-9]+-\d+)", raw, re.I)
    key = match.group(1).upper() if match else raw
    if not ATLASSIAN_USER or not ATLASSIAN_TOKEN:
        print("ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN 환경 변수 또는 .env를 설정하세요.", file=sys.stderr)
        sys.exit(1)
    try:
        data = get_issue(key)
        print(issue_to_text(data))
    except HTTPError as e:
        if e.code in (401, 403):
            print("인증 실패: 이메일 또는 API 토큰을 확인하세요.", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"연결 오류: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
