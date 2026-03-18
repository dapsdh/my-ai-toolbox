---
name: google-forms-viewer
description: Accepts a Google Forms URL (view form or viewscore) and fetches form metadata and responses via Google Forms API using .env credentials and displays them in a fixed format. Use when the user pastes a docs.google.com/forms link and asks to open it or show its content ("접속해줘", "보여줘", "내용 표시해줘"). Requires Google Cloud project with Forms API enabled and credentials in .env.
argument-hint: <Google Forms URL>
allowed-tools: Bash
---

# Google 폼 뷰어 (접속·내용 표시)

사용자 입력: $ARGUMENTS

위 입력에서 **Google 폼 URL**을 추출해 아래 워크플로를 따른다.

## 인증

- Google 인증은 **프로젝트 루트(.ai)의 `.env`**에서 로드한다.
- **방법 1 (서비스 계정 권장)**
  - `GOOGLE_APPLICATION_CREDENTIALS`: 서비스 계정 JSON 파일 경로.
  - 해당 폼을 서비스 계정 이메일과 **편집자 또는 뷰어**로 공유해야 한다.
- **방법 2 (OAuth 리프레시 토큰)**
  - `GOOGLE_REFRESH_TOKEN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` 설정.
- 인증이 없으면 "프로젝트 루트(.ai)의 .env에 Google 인증 정보를 설정해 주세요" 안내.

## 워크플로

1. **URL에서 폼 ID 추출**
   - `/forms/d/e/<form_id>/` 또는 `/forms/d/<form_id>/` 패턴에서 form_id 추출.
   - viewscore, viewform 등 경로 뒤에 붙어 있어도 동일하게 추출.

2. **스크립트 실행**
   ```bash
   python .claude/skills/google-forms-viewer/scripts/fetch_google_form.py "<폼_URL_또는_폼_ID>"
   ```
   스크립트는:
   - 프로젝트 루트(.ai)의 .env에서 인증 정보 로드 후 Google Forms API 호출.
   - `forms.get(formId)` 로 폼 제목·문항 정보 조회.
   - `forms.responses.list(formId)` 로 응답 목록 조회.
   - 문항 ID와 응답 값을 매핑해 읽기 쉬운 텍스트로 출력.

3. **출력 포맷**
   스크립트 표준 출력을 그대로 사용하거나, 에이전트가 아래 형식에 맞게 정리해 사용자에게 보여 준다.

## 출력 포맷

```text
# [폼 제목]

## 문항
- (문항 제목 / 설명)

## 응답 (N건)
--- 응답 1 ---
(문항별 답변 나열)

--- 응답 2 ---
...
```

- 응답이 없으면 "응답이 없습니다."로 표시.
- API 오류·인증 실패 시 stderr 메시지와 exit code 1로 종료. 사용자에게 루트 .env 설정 및 폼 공유 안내.

## 사전 설치

스크립트 실행 전 다음 패키지 설치 필요:
```bash
pip install google-api-python-client google-auth
```
