# .claude

Claude Code 전용 설정 디렉토리입니다.

## 구조

```
.claude/
└── skills/                         # Claude Code 슬래시 커맨드 스킬
    ├── git-commit/                 # /git-commit
    ├── git-mr-review/              # /git-mr-review
    ├── google-forms-viewer/        # /google-forms-viewer
    ├── jira-filter-summarizer/     # /jira-filter-summarizer
    ├── jira-issue-debug/           # /jira-issue-debug
    └── wiki-page-summarizer/       # /wiki-page-summarizer
```

## 스킬 목록

| 커맨드 | 설명 |
|--------|------|
| `/git-commit` | 스테이징된 변경사항을 분석해 커밋 메시지를 자동 생성하고 커밋합니다. |
| `/git-mr-review` | GitLab MR URL을 받아 diff를 조회하고 코드 리뷰를 수행합니다. |
| `/google-forms-viewer` | Google Forms URL을 받아 문항과 응답을 표시합니다. |
| `/jira-filter-summarizer` | Jira 필터 URL을 받아 이슈 목록을 요약합니다. |
| `/jira-issue-debug` | Jira 이슈 URL을 받아 문제 코드를 찾고 수정 방안을 제안합니다. |
| `/wiki-page-summarizer` | Jira/Confluence 페이지 URL을 받아 내용을 정리합니다. |

## 사용법

각 스킬은 슬래시 커맨드로 호출합니다.

```
/git-commit
/git-mr-review https://gitlab.example.com/.../merge_requests/23
/jira-filter-summarizer https://example.atlassian.net/issues/?filter=12345
/jira-issue-debug https://example.atlassian.net/browse/PROJ-123
/wiki-page-summarizer https://example.atlassian.net/wiki/.../pages/...
/google-forms-viewer https://docs.google.com/forms/d/.../viewform
```

## 인증

모든 스킬은 **프로젝트 루트의 `.env`** 파일에서 인증 정보를 로드합니다.
`.env.example`을 참고해 필요한 값을 설정하세요.

| 변수 | 사용 스킬 |
|------|-----------|
| `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN` | git-mr-review |
| `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` | jira-*, wiki-page-summarizer |
| `GOOGLE_APPLICATION_CREDENTIALS` (또는 OAuth 관련 변수) | google-forms-viewer |
