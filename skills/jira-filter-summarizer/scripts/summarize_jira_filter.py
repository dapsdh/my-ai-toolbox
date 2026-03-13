#!/usr/bin/env python3
"""
Jira 필터 결과를 REST API로 조회해 이슈별로 요약 출력.
- 필터 URL 또는 필터 ID 입력 → JQL 조회 → 이슈 목록 → 이슈별 설명·코멘트 조회
- GitLab(및 동일 봇, e.g. gitlab.example.com)가 작성한 코멘트는 '코드 커밋'으로, 나머지는 '코멘트'로 구분.
환경 변수: 프로젝트 루트(.ai)의 .env — ATLASSIAN_BASE_URL, ATLASSIAN_USER(이메일), ATLASSIAN_API_TOKEN
"""
import json
import os
import re
import sys
import textwrap
from base64 import b64encode
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

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


ATLASSIAN_BASE = (os.environ.get("ATLASSIAN_BASE_URL") or "").rstrip("/")
ATLASSIAN_USER = os.environ.get("ATLASSIAN_USER", "").strip()
ATLASSIAN_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "").strip()

# GitLab 봇 식별: COMMIT_AUTHOR_NAMES(쉼표 구분). 설정하지 않으면 코드 커밋으로 분류할 봇 없음
_raw = (os.environ.get("COMMIT_AUTHOR_NAMES") or "").strip()
GITLAB_BOT_NAMES = [x.strip() for x in _raw.split(",") if x.strip()]

# 설명/코멘트 여러 줄 포맷 시 사용할 너비
WRAP_WIDTH = 88
COMMENT_BODY_MAX = 200
CODE_COMMIT_BODY_MAX = 280

# @멘션 → 이름만 표시. 이메일(a@b.com) 제외: 이름 다음이 ". "(마침표+공백), 공백, 쉼표, 괄호, 끝일 때만 치환
_MENTION_PATTERN = re.compile(r"@([가-힣a-zA-Z0-9_]+)(?=\.\s|[\s,\)\]\}]|$)")


def _normalize_mentions(text: str) -> str:
    """@최윤혜 → 최윤혜 처럼 멘션을 이름만 표시하도록 바꿈."""
    if not text or not text.strip():
        return text
    return _MENTION_PATTERN.sub(r"\1", text)


def _auth_headers():
    auth = b64encode(f"{ATLASSIAN_USER}:{ATLASSIAN_TOKEN}".encode()).decode()
    return {"Accept": "application/json", "Authorization": f"Basic {auth}"}


def _get(url: str) -> dict:
    req = Request(url, headers=_auth_headers())
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _post(url: str, data: dict) -> dict:
    body = json.dumps(data).encode("utf-8")
    h = dict(_auth_headers())
    h["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=h, method="POST")
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _adf_to_plain_text(node) -> str:
    """Atlassian Document Format 노드에서 평문 텍스트 추출."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if node.get("type") == "text":
            return (node.get("text") or "").strip()
        # 멘션(@이름) 노드: attrs.text에 표시 이름이 있음
        if node.get("type") == "mention":
            return (node.get("attrs") or {}).get("text") or ""
        parts = []
        for c in node.get("content", []):
            parts.append(_adf_to_plain_text(c))
        parts = [p.strip() for p in parts if p and p.strip()]
        return " ".join(parts) if parts else ""
    if isinstance(node, list):
        parts = [_adf_to_plain_text(c) for c in node]
        parts = [p.strip() for p in parts if p and p.strip()]
        return " ".join(parts) if parts else ""
    return ""


def _description_text(fields: dict) -> str:
    desc = fields.get("description")
    if not desc:
        return ""
    if isinstance(desc, dict) and "content" in desc:
        return _adf_to_plain_text(desc).strip()
    return str(desc).strip()


def _is_gitlab_comment(author: dict) -> bool:
    if not author:
        return False
    name = (author.get("displayName") or author.get("name") or "").lower()
    email = (author.get("emailAddress") or "").lower()
    for token in GITLAB_BOT_NAMES:
        if token in name or token in email:
            return True
    return False


def extract_filter_id(raw: str) -> str:
    """URL 또는 문자열에서 필터 ID 추출. filter=12345 또는 /filter/12345 형태."""
    raw = (raw or "").strip()
    # filter=12345
    m = re.search(r"filter=(\d+)", raw, re.I)
    if m:
        return m.group(1)
    # /filter/12345
    m = re.search(r"/filter/(\d+)", raw, re.I)
    if m:
        return m.group(1)
    # 숫자만
    if raw.isdigit():
        return raw
    return ""


def get_filter_jql(filter_id: str) -> str:
    """GET /rest/api/3/filter/{id} → jql 반환."""
    url = f"{ATLASSIAN_BASE}/rest/api/3/filter/{filter_id}"
    data = _get(url)
    return (data.get("jql") or "").strip()


def search_issues(jql: str, max_results: int = 100) -> list:
    """JQL로 이슈 검색, 이슈 키 목록 반환. POST /rest/api/3/search/jql 사용 (GET /search 410 대응)."""
    if not jql:
        return []
    url = f"{ATLASSIAN_BASE}/rest/api/3/search/jql"
    payload = {"jql": jql, "maxResults": max_results, "fields": ["summary", "status", "description"]}
    data = _post(url, payload)
    return [i.get("key") for i in (data.get("issues") or []) if i.get("key")]


def get_issue(key: str) -> dict:
    """이슈 상세 조회 (summary, status, description)."""
    url = f"{ATLASSIAN_BASE}/rest/api/3/issue/{key}?fields=summary,status,description"
    return _get(url)


def get_comments(key: str) -> list:
    """이슈 코멘트 목록. 각 항목: { body_plain, author, created, is_gitlab }."""
    url = f"{ATLASSIAN_BASE}/rest/api/3/issue/{key}/comment"
    data = _get(url)
    comments = []
    for c in (data.get("comments") or []):
        body = c.get("body")
        if isinstance(body, dict) and "content" in body:
            body_plain = _adf_to_plain_text(body).strip()
        else:
            body_plain = (body or "").strip() if body else ""
        author = c.get("author") or {}
        is_gitlab = _is_gitlab_comment(author)
        comments.append({
            "body": body_plain,
            "author": author.get("displayName") or author.get("name") or "",
            "created": c.get("created") or "",
            "is_gitlab": is_gitlab,
        })
    return comments


def _wrap_block(label: str, body: str, width: int = WRAP_WIDTH, max_chars: int = 0) -> list:
    """한 문단을 여러 줄로 감싸서, 첫 줄에 label을 붙이고 이어서 들여쓰기된 줄들을 반환."""
    lines = []
    text = (body or "").strip()
    if not text:
        return [f" - {label}: (없음)"]
    if max_chars and len(text) > max_chars:
        text = text[: max_chars - 4].rstrip() + "...."
    wrapped = textwrap.wrap(text, width=width, drop_whitespace=True)
    lines.append(f" - {label}: {wrapped[0]}" if wrapped else f" - {label}: (없음)")
    for w in wrapped[1:]:
        lines.append("    " + w)
    return lines


def format_issue_block(key: str, summary: str, status: str, description: str, comments: list) -> str:
    """한 이슈에 대한 출력 블록 생성. 설명은 여러 줄로, 코멘트는 항목별로 간략히 표시."""
    lines = [f"[{key}] {summary} ({status})"]

    # 설명: @멘션 → 이름만 표시 후 여러 줄로 감싸서 표시 (최대 600자)
    desc_text = _normalize_mentions(description.strip() if description else "")
    lines.extend(_wrap_block("설명", desc_text or "(없음)", max_chars=600))

    # 코멘트: @멘션 → 이름만 표시 후 항목별로 줄을 나누어 간략 표시
    normal = [c for c in comments if not c["is_gitlab"]]
    if normal:
        lines.append(" - 코멘트:")
        for i, c in enumerate(normal, 1):
            body = _normalize_mentions((c["body"] or "").strip())
            if len(body) > COMMENT_BODY_MAX:
                body = body[: COMMENT_BODY_MAX - 4].rstrip() + "...."
            author = (c.get("author") or "").strip()
            prefix = f"    [{i}]"
            if author:
                prefix += f" ({author})"
            prefix += " "
            if body:
                sub = textwrap.wrap(body, width=WRAP_WIDTH - 6, drop_whitespace=True)
                lines.append(prefix + (sub[0] if sub else ""))
                for s in (sub[1:] or []):
                    lines.append("       " + s)
            else:
                lines.append(prefix + "(내용 없음)")
    else:
        lines.append(" - 코멘트: (없음)")

    # 코드 커밋: @멘션 → 이름만 표시 후 항목별로 줄을 나누어 간략 표시
    gitlab_comments = [c for c in comments if c["is_gitlab"]]
    if gitlab_comments:
        lines.append(" - 코드 커밋:")
        for i, c in enumerate(gitlab_comments, 1):
            body = _normalize_mentions((c["body"] or "").strip())
            if len(body) > CODE_COMMIT_BODY_MAX:
                body = body[: CODE_COMMIT_BODY_MAX - 4].rstrip() + "...."
            prefix = f"    [{i}] "
            if body:
                sub = textwrap.wrap(body, width=WRAP_WIDTH - 6, drop_whitespace=True)
                lines.append(prefix + (sub[0] if sub else ""))
                for s in (sub[1:] or []):
                    lines.append("       " + s)
            else:
                lines.append(prefix + "(내용 없음)")
    else:
        lines.append(" - 코드 커밋: (없음)")

    return "\n".join(lines)


def main():
    raw = " ".join(sys.argv[1:]).strip()
    out_path = None
    if "-o" in sys.argv:
        i = sys.argv.index("-o")
        if i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
            # 인자 목록에서 -o와 경로 제거
            args = [a for a in sys.argv[1:] if a != "-o" and a != out_path]
            raw = " ".join(args).strip()
    if not raw:
        print("Usage: summarize_jira_filter.py <filter_url_or_filter_id> [-o output.txt]", file=sys.stderr)
        sys.exit(2)

    # Windows 콘솔 UTF-8 출력 (cp949 등으로 인한 UnicodeEncodeError 방지)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    filter_id = extract_filter_id(raw)
    if not filter_id:
        print("필터 URL에서 filter ID를 찾을 수 없습니다. (예: ...?filter=12345)", file=sys.stderr)
        sys.exit(2)

    if not ATLASSIAN_USER or not ATLASSIAN_TOKEN:
        print("ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN 환경 변수 또는 .env를 설정하세요.", file=sys.stderr)
        sys.exit(1)

    try:
        jql = get_filter_jql(filter_id)
        if not jql:
            print("필터 JQL을 가져올 수 없습니다.", file=sys.stderr)
            sys.exit(1)

        keys = search_issues(jql)
        if not keys:
            print("필터에 해당하는 이슈가 없습니다.", file=sys.stderr)
            sys.exit(0)

        out_lines = []
        for key in keys:
            issue = get_issue(key)
            fields = issue.get("fields") or {}
            summary = (fields.get("summary") or "").strip()
            status = (fields.get("status") or {}).get("name", "")
            description = _description_text(fields)
            comments = get_comments(key)
            block = format_issue_block(key, summary, status, description, comments)
            out_lines.append(block)
            out_lines.append("")

        text = "\n".join(out_lines)
        if out_path:
            Path(out_path).write_text(text, encoding="utf-8")
        else:
            print(text)

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
