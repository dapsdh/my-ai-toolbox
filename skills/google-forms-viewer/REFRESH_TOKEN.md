# OAuth 리프레시 토큰 발급 방법

---

## 프로젝트를 전혀 만들 수 없을 때

Google Cloud **프로젝트 생성 자체가 불가**한 경우, 아래 둘 중 하나만 가능합니다.

### ① 동료/관리자에게 OAuth 클라이언트만 발급받기 (권장)

- **프로젝트를 만들 수 있는 사람**(동료, 관리자, 다른 팀)에게 요청합니다.
- 요청할 내용:
  - "Google Cloud 프로젝트 하나에서 **OAuth 2.0 클라이언트 ID(데스크톱 앱)** 하나 만들어 주세요."
  - "**승인된 리디렉션 URI**에 `http://localhost:8080/` 추가해 주세요."
  - "**Google Forms API** 사용 설정해 주세요."
  - "만들어진 **클라이언트 ID**와 **클라이언트 보안 비밀**을 알려주세요."
- 받은 **클라이언트 ID**, **클라이언트 보안 비밀**로 아래 **3. 리프레시 토큰 발급**을 진행합니다.
- **리프레시 토큰**은 본인 Google 계정으로 로그인해서 발급하므로, 클라이언트만 공유받고 토큰은 본인 것만 쓰면 됩니다.

### ② 개인 Gmail로 프로젝트 생성 (회사 정책이 허용할 때만)

- 회사 계정으로는 프로젝트 생성이 막혀 있고 **개인 Gmail** 사용이 허용된다면, [Google Cloud Console](https://console.cloud.google.com/)에 **개인 Gmail로 로그인**한 뒤 새 프로젝트를 만들 수 있습니다. 그 다음 OAuth 데스크톱 클라이언트 + Forms API 설정하고, **회사 Google 계정**으로 리프레시 토큰만 발급받아 사용하면 됩니다.
- 회사 보안/정책에서 개인 계정·개인 프로젝트 사용을 금지할 수 있으므로, 가능한지 확인 후 진행하세요.

---

## 1. 준비: OAuth 클라이언트 ID/시크릿 확보

다음 중 하나가 필요합니다.

- **기존 Google Cloud 프로젝트**가 있다면: 해당 프로젝트에서 OAuth 2.0 클라이언트(데스크톱 앱) 생성
- 프로젝트 생성 권한이 없다면: **관리자에게** “데스크톱 앱용 OAuth 클라이언트 ID 하나 발급해 달라”고 요청

### 1-1. 프로젝트에서 OAuth 클라이언트 만들기 (권한이 있을 때)

1. [Google Cloud Console](https://console.cloud.google.com/) 접속 후 사용할 **프로젝트** 선택.
2. **API 및 서비스 → 사용자 인증 정보** 이동.
3. **+ 사용자 인증 정보 만들기 → OAuth 클라이언트 ID** 선택.
4. **애플리케이션 유형**: **데스크톱 앱** 선택.
5. 이름 입력 후 **만들기**.
6. **클라이언트 ID**와 **클라이언트 보안 비밀**을 복사해 둡니다.

### 1-2. 리디렉션 URI 등록 (스크립트용)

같은 OAuth 클라이언트 설정 화면에서:

1. **승인된 리디렉션 URI**에 아래를 **추가** 후 저장합니다.  
   `http://localhost:8080/`

---

## 2. 사용할 API 사용 설정

해당 프로젝트에서 **Google Forms API**를 사용하도록 설정합니다.

1. **API 및 서비스 → 라이브러리** 이동.
2. “Google Forms API” 검색 후 **사용** 클릭.

(나중에 Docs, Sheets 등도 쓰려면 같은 방식으로 해당 API를 사용 설정하면 됩니다.)

---

## 3. 리프레시 토큰 발급 스크립트 실행

한 번만 실행하면 됩니다.

```bash
cd .cursor/skills/google-forms-viewer/scripts
pip install google-auth-oauthlib
set GOOGLE_CLIENT_ID=여기에_클라이언트_ID
set GOOGLE_CLIENT_SECRET=여기에_클라이언트_보안_비밀
python get_refresh_token.py
```

(PowerShell에서는 `$env:GOOGLE_CLIENT_ID="..."; $env:GOOGLE_CLIENT_SECRET="..."` 로 설정한 뒤 `python get_refresh_token.py` 실행.)

1. 브라우저가 열리면 **Google 계정으로 로그인**합니다.
2. **권한 요청** 화면에서 **허용**을 누릅니다.
3. 터미널에 **리프레시 토큰**이 출력됩니다.  
   이 값을 복사해 `.env`의 `GOOGLE_REFRESH_TOKEN`에 넣습니다.

---

## 4. .env 설정 예시

`.cursor/skills/google-forms-viewer/.env`에 다음처럼 넣습니다.

```env
GOOGLE_CLIENT_ID=123456789-xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxx
GOOGLE_REFRESH_TOKEN=1//0gxxxxxxxxxxxx
```

- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: 1단계에서 만든 OAuth 클라이언트 값  
- `GOOGLE_REFRESH_TOKEN`: 3단계 스크립트로 발급받은 값  

이렇게 설정하면 프로젝트를 새로 만들지 않아도 OAuth 리프레시 토큰으로 Google 폼 뷰어를 사용할 수 있습니다.
