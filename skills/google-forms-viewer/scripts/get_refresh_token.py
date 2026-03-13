#!/usr/bin/env python3
"""
OAuth 2.0 인증 코드 흐름으로 리프레시 토큰을 발급받아 출력합니다.
한 번만 실행해 .env의 GOOGLE_REFRESH_TOKEN에 넣으면 됩니다.

사용 전:
  1. Google Cloud 프로젝트에서 OAuth 2.0 클라이언트 ID(데스크톱 앱) 생성
  2. 승인된 리디렉션 URI에 http://localhost:8080/ 추가
  3. GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 환경 변수 설정 후 실행

  REFRESH_TOKEN.md 참고.
"""
import os
import sys
from pathlib import Path

# .env 로드
def _load_dotenv():
    base = Path(__file__).resolve().parent
    skill_dir = base.parent
    for d in [skill_dir, skill_dir.parent.parent]:
        env = d / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and v and k not in os.environ:
                        os.environ[k] = v
            break


_load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/forms.body.readonly",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]


def main():
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        print(
            "GOOGLE_CLIENT_ID와 GOOGLE_CLIENT_SECRET을 설정한 뒤 실행하세요.\n"
            "예: set GOOGLE_CLIENT_ID=xxx & set GOOGLE_CLIENT_SECRET=yyy & python get_refresh_token.py\n"
            "자세한 방법은 REFRESH_TOKEN.md를 참고하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("pip install google-auth-oauthlib", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost:8080/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )

    creds = flow.run_local_server(port=8080)
    refresh_token = getattr(creds, "refresh_token", None)
    if not refresh_token:
        print("리프레시 토큰을 받지 못했습니다. OAuth 클라이언트에서 '테스트 앱'이 아닌 게시 상태인지 확인하세요.", file=sys.stderr)
        sys.exit(1)

    print("\n아래 값을 .env의 GOOGLE_REFRESH_TOKEN에 넣으세요.\n")
    print(refresh_token)


if __name__ == "__main__":
    main()
