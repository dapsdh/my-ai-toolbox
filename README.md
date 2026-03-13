# my-ai-toolbox

AI 에이전트(Cursor 등)에서 사용하는 스킬·설정을 모아 둔 저장소입니다.

## 저장소 클론

로컬에서 폴더 이름을 `.ai`로 두고 쓰려면, 클론 시 대상 디렉터리를 `.ai`로 지정하세요.

```bash
git clone https://github.com/dapsdh/my-ai-toolbox.git .ai
```

이렇게 하면 `my-ai-toolbox` 저장소 내용이 현재 디렉터리의 `.ai` 폴더에 내려받아집니다.

예: `d:\Projects`에서 실행 시 → `d:\Projects\.ai`에 클론됨.

---

## 스킬 목록

각 스킬은 `skills/<스킬명>/` 아래에 있으며, `SKILL.md`에 상세 워크플로가 정의되어 있습니다.

### jira-filter-summarizer

- **설명**: Jira 필터 페이지 링크와 "요약해줘"를 주면, 필터에 걸린 **각 이슈**를 설명·코멘트·코드 커밋으로 구분해 정리합니다. GitLab이 Jira에 남긴 푸시 코멘트는 "코드 커밋"으로만 묶습니다.
- **트리거 예**: `https://example.atlassian.net/issues/?filter=12345 요약해줘`
- **인증**: 스킬 디렉터리 `.env`에 `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` 등 설정.

### wiki-page-summarizer

- **설명**: Jira 이슈 또는 Confluence 페이지 URL을 주고 "요약해줘" / "하위 페이지까지 요약해줘"를 요청하면, 해당 페이지만 또는 **하위 페이지를 재귀적으로 포함한 전체**를 가져와 구조화해 요약합니다. 로그인이 필요하면 `.env` 인증으로 API 호출합니다.
- **트리거 예**: `<페이지 링크> 요약해줘`, `<페이지 링크> 하위 페이지까지 요약해줘`
- **인증**: 스킬 디렉터리 `.env`에 `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` 등 설정.

### jira-issue-debug

- **설명**: Jira 이슈 URL과 함께 "문제코드를 찾아줘" 또는 "디버깅해줘"를 주면, 이슈 설명을 분석하고 수정이 필요하면 코드베이스에서 문제 코드를 찾아 수정 방안을 제안합니다. 수정이 불필요한 이슈면 그 이유를 설명합니다.
- **트리거 예**: `https://example.atlassian.net/browse/PROJ-123 문제코드를 찾아줘`
- **인증**: 스킬 디렉터리 `.env`에 Jira API 인증 정보 설정.

### google-forms-viewer

- **설명**: Google 폼 URL(폼 보기/응답 보기)과 "접속해줘", "내용 보여줘" 등을 주면, Google Forms API로 폼 제목·문항과 응답 목록을 가져와 정해진 포맷으로 보여 줍니다. 브라우저 로그인 없이 스킬의 `.env` 인증으로 API를 호출합니다.
- **트리거 예**: `https://docs.google.com/forms/d/e/.../viewscore 접속해줘`
- **인증**: 스킬 디렉터리 `.env`에 서비스 계정 JSON 경로 또는 OAuth 리프레시 토큰 등 설정. Google Cloud에서 Forms API 활성화 필요.

### gitlab-mr-code-review

- **설명**: GitLab 머지 리퀘스트 URL과 "코드 리뷰 해줘"를 주면, GitLab API로 MR 메타데이터와 diff를 가져온 뒤 **구조화된 코드 리뷰**(로직·버그·보안·가독성·스타일 등)를 수행해 정리해서 보여 줍니다.
- **트리거 예**: `https://gitlab.example.com/.../merge_requests/23/diffs 코드 리뷰 해줘`
- **인증**: 스킬 디렉터리 `.env`에 `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN` 설정.

---

## 인증·환경 변수

**모든 스킬의 환경 변수는 프로젝트 루트(.ai)의 `.env` 한 곳에서만 관리합니다.**

- 루트의 `.env.example`을 복사해 루트에 `.env`를 만든 뒤, 사용하는 스킬에 맞게 값을 채우면 됩니다.
- **Atlassian** (jira-filter-summarizer, wiki-page-summarizer, jira-issue-debug): `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN`, (선택) `COMMIT_AUTHOR_NAMES`
- **GitLab** (gitlab-mr-code-review): `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN`, (선택) `GITLAB_HOST`
- **Google** (google-forms-viewer): `GOOGLE_APPLICATION_CREDENTIALS` 또는 OAuth용 `GOOGLE_REFRESH_TOKEN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `.env`는 Git에 포함되지 않도록 되어 있으므로, 클론 후 사용 전에 직접 설정해야 합니다.
