#!/usr/bin/env python3
"""
GitLab MR URL을 받아 API로 merge request changes(diff)를 조회해 출력.
- 환경 변수: 프로젝트 루트(.ai)의 .env — GITLAB_PRIVATE_TOKEN 또는 GITLAB_ACCESS_TOKEN, 선택 GITLAB_HOST
- MR URL 예: https://gitlab.example.com/group/project/-/merge_requests/23/diffs
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Windows 콘솔 UTF-8 출력 (diff에 유니코드 문자가 있을 때 cp949 오류 방지)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def _load_dotenv():
    base = Path(os.path.abspath(__file__)).parent
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

# GITLAB_ACCESS_TOKEN 우선, 없으면 GITLAB_PRIVATE_TOKEN
GITLAB_TOKEN = (
    os.environ.get("GITLAB_ACCESS_TOKEN") or os.environ.get("GITLAB_PRIVATE_TOKEN") or ""
).strip()


def _parse_mr_url(url: str):
    """MR URL에서 host, project_path, mr_iid 추출. (scheme 포함 host 반환)"""
    url = url.strip()
    # merge_requests/숫자 또는 merge_requests/숫자/...
    mr_match = re.search(r"/merge_requests/(\d+)", url)
    if not mr_match:
        return None, None, None
    mr_iid = mr_match.group(1)
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    host = (os.environ.get("GITLAB_HOST") or parsed.netloc or "").strip()
    if not host:
        return None, None, None
    base_url = f"{scheme}://{host}"
    path = (parsed.path or "").strip("/")
    idx = path.find("/-/merge_requests/")
    if idx == -1:
        return None, None, None
    project_path = path[:idx]
    if not project_path:
        return None, None, None
    return base_url, project_path, mr_iid


def _get(url: str, token: str) -> dict:
    headers = {"Accept": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token
    req = Request(url, headers=headers)
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def main():
    if len(sys.argv) < 2:
        print("사용법: fetch_mr_diffs.py <GitLab_MR_URL>", file=sys.stderr)
        sys.exit(1)

    base_url, project_path, mr_iid = _parse_mr_url(sys.argv[1])
    if not base_url or not project_path or not mr_iid:
        print("올바른 GitLab MR URL이 아닙니다. 예: https://gitlab.example.com/group/project/-/merge_requests/23", file=sys.stderr)
        sys.exit(1)

    if not GITLAB_TOKEN:
        print(
            "프로젝트 루트(.ai)의 .env에 GITLAB_PRIVATE_TOKEN 또는 GITLAB_ACCESS_TOKEN을 설정해 주세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    project_id = quote(project_path, safe="")
    changes_url = f"{base_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"

    try:
        data = _get(changes_url, GITLAB_TOKEN)
    except HTTPError as e:
        if e.code == 401:
            print("인증 실패. 토큰을 확인하세요.", file=sys.stderr)
        elif e.code == 404:
            print("MR 또는 프로젝트를 찾을 수 없습니다. URL과 토큰 권한을 확인하세요.", file=sys.stderr)
        else:
            print(f"API 오류: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"연결 오류: {e.reason}", file=sys.stderr)
        sys.exit(1)

    title = data.get("title", "(제목 없음)")
    description = (data.get("description") or "").strip()
    source_branch = data.get("source_branch", "?")
    target_branch = data.get("target_branch", "?")
    state = data.get("state", "?")

    print(f"# {title} (!{mr_iid})")
    print(f"상태: {state} | {source_branch} → {target_branch}")
    if description:
        print(f"\n## 설명\n{description}\n")
    print("## 변경 파일 (diff)\n")

    changes = data.get("changes") or []
    for ch in changes:
        old_path = ch.get("old_path", "")
        new_path = ch.get("new_path", "")
        diff = (ch.get("diff") or "").strip()
        label = new_path if new_path else old_path
        if old_path and new_path and old_path != new_path:
            label = f"{old_path} → {new_path}"
        print(f"### {label}")
        if diff:
            print(diff)
        else:
            print("(빈 diff)")
        print()

    if not changes:
        print("(변경된 파일 없음)")


if __name__ == "__main__":
    main()
