# my-ai-toolbox

AI 에이전트(Cursor 등)에서 사용하는 스킬·설정을 모아 둔 저장소입니다.

## 저장소 클론

로컬에서 폴더 이름을 `.ai`로 두고 쓰려면, 클론 시 대상 디렉터리를 `.ai`로 지정하세요.

```bash
git clone https://github.com/dapsdh/my-ai-toolbox.git .ai
```

이렇게 하면 `my-ai-toolbox` 저장소 내용이 현재 디렉터리의 `.ai` 폴더에 내려받아집니다.

예: `d:\Projects`에서 실행 시 → `d:\Projects\.ai`에 클론됨.

## 초기 설정

클론 후 아래 두 단계를 1회 실행합니다.

### 1. 환경 변수 설정

```powershell
copy shared\.env.example shared\.env
# shared\.env 파일을 열어 필요한 인증 정보를 채우세요
```

### 2. 로컬 링크 복원

`shared/`의 스크립트와 `.env`를 각 플랫폼(`.claude/`, `.cursor/`)에서 참조할 수 있도록 junction/하드링크를 생성합니다.

```powershell
.\setup.ps1
```

---

## 스킬 설치

전역(`~/.claude/` 등)이나 다른 프로젝트에 스킬을 설치합니다. `-Platform` 생략 시 `.claude` 스킬을 설치합니다.

```powershell
# .claude 전체 스킬을 전역에 설치
.\install-skills.ps1 -Target global

# 특정 스킬만 전역 설치
.\install-skills.ps1 -Target global -Skills git-mr-review

# .cursor 플랫폼 스킬을 전역에 설치
.\install-skills.ps1 -Target global -Platform cursor

# 특정 프로젝트에 설치
.\install-skills.ps1 -Target D:\Projects\myapp -Skills git-mr-review,wiki-page-summarizer
```

### 재설치 (스킬 업데이트)

이미 설치된 스킬은 기본적으로 건너뜁니다. 저장소를 `git pull`한 뒤 스킬을 업데이트하려면 `-Force` 옵션을 사용하세요. `-Force`는 기존 scripts 디렉토리를 삭제하고 SKILL.md와 junction을 다시 생성합니다.

```powershell
# 특정 스킬 재설치
.\install-skills.ps1 -Target global -Skills jira-bug-analyzer -Force

# 전체 스킬 재설치
.\install-skills.ps1 -Target global -Force
```

---

## 스킬 목록

각 스킬은 플랫폼별 디렉토리(`.claude/skills/`, `.cursor/skills/`) 아래에 있으며, `SKILL.md`에 상세 워크플로가 정의되어 있습니다. Python 스크립트와 `.env`는 `shared/`에서 공동 관리하고, 각 플랫폼에서 symlink로 참조합니다.

### jira-filter-summarizer

- **설명**: Jira 필터 페이지 링크와 "요약해줘"를 주면, 필터에 걸린 **각 이슈**를 설명·코멘트·코드 커밋으로 구분해 정리합니다. GitLab이 Jira에 남긴 푸시 코멘트는 "코드 커밋"으로만 묶습니다.
- **트리거 예**: `https://example.atlassian.net/issues/?filter=12345 요약해줘`
- **인증**: 스킬 디렉터리 `.env`에 `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` 등 설정.

### wiki-page-summarizer

- **설명**: Jira 이슈 또는 Confluence 페이지 URL을 주고 "요약해줘" / "하위 페이지까지 요약해줘"를 요청하면, 해당 페이지만 또는 **하위 페이지를 재귀적으로 포함한 전체**를 가져와 구조화해 요약합니다. 로그인이 필요하면 `.env` 인증으로 API 호출합니다.
- **트리거 예**: `<페이지 링크> 요약해줘`, `<페이지 링크> 하위 페이지까지 요약해줘`
- **인증**: 스킬 디렉터리 `.env`에 `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` 등 설정.

### jira-bug-analyzer

- **설명**: Jira 이슈 URL과 함께 "문제코드를 찾아줘" 또는 "디버깅해줘"를 주면, 이슈 설명을 분석하고 수정이 필요하면 코드베이스에서 문제 코드를 찾아 수정 방안을 제안합니다. 수정이 불필요한 이슈면 그 이유를 설명합니다.
- **트리거 예**: `https://example.atlassian.net/browse/PROJ-123 문제코드를 찾아줘`
- **인증**: 스킬 디렉터리 `.env`에 Jira API 인증 정보 설정.

### google-forms-viewer

- **설명**: Google 폼 URL(폼 보기/응답 보기)과 "접속해줘", "내용 보여줘" 등을 주면, Google Forms API로 폼 제목·문항과 응답 목록을 가져와 정해진 포맷으로 보여 줍니다. 브라우저 로그인 없이 스킬의 `.env` 인증으로 API를 호출합니다.
- **트리거 예**: `https://docs.google.com/forms/d/e/.../viewscore 접속해줘`
- **인증**: 스킬 디렉터리 `.env`에 서비스 계정 JSON 경로 또는 OAuth 리프레시 토큰 등 설정. Google Cloud에서 Forms API 활성화 필요.

### git-mr-review

- **설명**: GitLab 머지 리퀘스트 URL과 "코드 리뷰 해줘"를 주면, GitLab API로 MR 메타데이터와 diff를 가져온 뒤 **구조화된 코드 리뷰**(로직·버그·보안·가독성·스타일 등)를 수행해 정리해서 보여 줍니다.
- **트리거 예**: `https://gitlab.example.com/.../merge_requests/23/diffs 코드 리뷰 해줘`
- **인증**: 스킬 디렉터리 `.env`에 `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN` 설정.

### create-my-skill

- **설명**: 대화형으로 Claude Code 스킬(SKILL.md)을 생성하고 품질 검증까지 수행합니다. 스킬 이름과 사용 예시를 입력하면 SKILL.md와 README.md를 자동 생성하고, 5가지 기준(트리거 명확성, 예시 포함, 구조 완결성, 지시 명확성, 500줄 이하)으로 검증합니다.
- **트리거 예**: `/create-my-skill`, `스킬 만들어줘`, `새 스킬 생성`
- **인증**: 없음 (별도 환경 변수 불필요)

### save-article

- **설명**: 웹 URL을 입력받아 페이지의 제목과 요약을 추출한 뒤, 지정된 Confluence 페이지 하단에 링크와 요약을 추가합니다. 동일 URL이 이미 있으면 해당 섹션 바로 아래에 삽입하여 비교할 수 있게 합니다.
- **트리거 예**: `/save-article https://example.com/article`, `아티클 저장`, `이 글 저장해줘`
- **인증**: 스킬 디렉터리 `.env`에 Atlassian 인증 정보 + `CONFLUENCE_PAGE_URL` 설정.

### install-gstack

- **설명**: Garry Tan의 [gstack](https://github.com/garrytan/gstack)을 현재 프로젝트(또는 글로벌)에 설치하고, gstack 워크플로우(Think→Plan→Build→Review→Test→Ship→Reflect) 기준으로 CLAUDE.md를 갱신합니다. 기존 CLAUDE.md가 있으면 `CLAUDE.md.before-gstack`으로 백업하고 새 CLAUDE.md 끝에 요약을 붙입니다. 선택적으로 [GBrain](https://github.com/garrytan/gbrain)까지 함께 설치하고 Claude Code MCP에 등록합니다.
- **트리거 예**: `/install-gstack`, `gstack 설치`, `gstack 환경 만들어줘`
- **인증**: 없음 (별도 환경 변수 불필요). Claude Code CLI, Bun 1.0+, Git 필요.

---

## 인증·환경 변수

**환경 변수는 `shared/.env`에서 공동 관리합니다.** 각 플랫폼 디렉토리의 `.env`는 `shared/.env`에 대한 symlink입니다.

- `shared/.env.example`을 복사해 `shared/.env`를 만든 뒤, 사용하는 스킬에 맞게 값을 채우면 됩니다.
- **Atlassian** (jira-filter-summarizer, wiki-page-summarizer, jira-bug-analyzer, save-article): `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN`, (선택) `COMMIT_AUTHOR_NAMES`, (save-article 전용) `CONFLUENCE_PAGE_URL`
- **GitLab** (git-mr-review): `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN`, (선택) `GITLAB_HOST`
- **Google** (google-forms-viewer): `GOOGLE_APPLICATION_CREDENTIALS` 또는 OAuth용 `GOOGLE_REFRESH_TOKEN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `.env`는 Git에 포함되지 않도록 되어 있으므로, 클론 후 사용 전에 직접 설정해야 합니다.
