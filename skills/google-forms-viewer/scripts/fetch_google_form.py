#!/usr/bin/env python3
"""
Google 폼 URL(또는 폼 ID)을 받아 Forms API로 폼 정보와 응답 목록을 조회해 포맷된 텍스트로 출력.
- 환경 변수: 프로젝트 루트(.ai)의 .env — GOOGLE_APPLICATION_CREDENTIALS 또는 GOOGLE_REFRESH_TOKEN+CLIENT_ID+CLIENT_SECRET
- 폼은 서비스 계정 이메일과 공유되어 있어야 함.
"""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

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

SCOPES = [
    "https://www.googleapis.com/auth/forms.body.readonly",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"


def _extract_form_id(url_or_id: str) -> str:
    """URL에서 폼 ID 추출. 이미 ID만 넘어온 경우 그대로 반환."""
    s = url_or_id.strip()
    # /forms/d/e/ID/ 또는 /forms/d/ID/
    m = re.search(r"/forms/d/(?:e/)?([^/?\s]+)", s)
    if m:
        return m.group(1)
    # ID만 있는 경우(영숫자 등)
    if re.match(r"^[\w\-]+$", s):
        return s
    return s


def _get_credentials():
    """서비스 계정 또는 리프레시 토큰으로 Credentials 반환."""
    try:
        from google.oauth2 import service_account
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        if creds_path and Path(creds_path).is_file():
            return service_account.Credentials.from_service_account_file(
                creds_path, scopes=SCOPES
            )
    except Exception:
        pass

    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "").strip()
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if refresh_token and client_id and client_secret:
        try:
            import urllib.request
            body = (
                f"client_id={urllib.parse.quote(client_id)}"
                f"&client_secret={urllib.parse.quote(client_secret)}"
                f"&refresh_token={urllib.parse.quote(refresh_token)}"
                "&grant_type=refresh_token"
            )
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=body.encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            access_token = data.get("access_token")
            if access_token:
                from google.oauth2.credentials import Credentials
                return Credentials(token=access_token)
        except Exception as e:
            print("OAuth 리프레시 토큰으로 인증 실패:", e, file=sys.stderr)
    return None


def _build_question_map(form: dict) -> dict:
    """form['items']에서 questionId -> (제목, 설명) 맵 생성."""
    qmap = {}
    for item in form.get("items", []):
        title = item.get("title", "(제목 없음)")
        desc = (item.get("description") or "").strip()
        qitem = item.get("questionItem") or {}
        question = qitem.get("question") or {}
        qid = question.get("questionId")
        if qid:
            qmap[qid] = (title, desc)
        # questionGroupItem 안의 questions
        group = item.get("questionGroupItem") or {}
        for q in group.get("questions", []):
            qid = q.get("questionId")
            if qid:
                qmap[qid] = (title, desc)
    return qmap


def _answer_text(answer: dict) -> str:
    """단일 답변 객체를 읽기 쉬운 문자열로."""
    if not answer:
        return ""
    if "textAnswers" in answer:
        vals = answer["textAnswers"].get("answers", [])
        return "; ".join(a.get("value", "") for a in vals if a.get("value"))
    if "fileUploadAnswers" in answer:
        return "(파일 업로드)"
    return str(answer)


def main():
    if len(sys.argv) < 2:
        print("사용법: fetch_google_form.py <폼_URL_또는_폼_ID>", file=sys.stderr)
        sys.exit(1)

    form_id = _extract_form_id(sys.argv[1])
    creds = _get_credentials()
    if not creds:
        print(
            "프로젝트 루트(.ai)의 .env에 Google 인증 정보를 설정해 주세요.\n"
            "  - GOOGLE_APPLICATION_CREDENTIALS: 서비스 계정 JSON 파일 경로 (폼을 해당 계정과 공유)\n"
            "  또는\n"
            "  - GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from googleapiclient.discovery import build
        service = build(
            "forms",
            "v1",
            credentials=creds,
            discoveryServiceUrl=DISCOVERY_DOC,
            static_discovery=False,
        )
    except Exception as e:
        print("Google API 클라이언트 로드 실패. pip install google-api-python-client google-auth", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    try:
        form = service.forms().get(formId=form_id).execute()
    except Exception as e:
        print("폼 조회 실패:", e, file=sys.stderr)
        print("폼이 서비스 계정(또는 OAuth 계정)과 공유되어 있는지 확인하세요.", file=sys.stderr)
        sys.exit(1)

    info = form.get("info") or {}
    title = info.get("title") or info.get("documentTitle") or "(제목 없음)"
    description = (info.get("description") or "").strip()

    qmap = _build_question_map(form)

    print(f"# {title}")
    if description:
        print(f"\n{description}\n")
    print("## 문항")
    for qid, (qtitle, qdesc) in qmap.items():
        if qdesc:
            print(f"- {qtitle}: {qdesc}")
        else:
            print(f"- {qtitle}")

    responses = []
    try:
        result = service.forms().responses().list(formId=form_id).execute()
        responses = result.get("responses") or []
    except Exception as e:
        print("\n응답 목록 조회 실패:", e, file=sys.stderr)

    print(f"\n## 응답 ({len(responses)}건)")
    if not responses:
        print("응답이 없습니다.")
        return

    for i, resp in enumerate(responses, 1):
        print(f"\n--- 응답 {i} ---")
        if resp.get("lastSubmittedTime"):
            print(f"제출 시각: {resp['lastSubmittedTime']}")
        if resp.get("respondentEmail"):
            print(f"응답자: {resp['respondentEmail']}")
        answers = resp.get("answers") or {}
        for qid, (qtitle, _) in qmap.items():
            if qid in answers:
                text = _answer_text(answers[qid])
                if text:
                    print(f"  {qtitle}: {text}")


if __name__ == "__main__":
    main()
