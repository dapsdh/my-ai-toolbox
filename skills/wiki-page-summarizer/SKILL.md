---
name: wiki-page-summarizer
description: Accepts a Jira or Confluence page URL and produces an organized summary. Use when the user asks to summarize a page ("요약해줘" = that page only; "하위 페이지까지 요약해줘" = include all descendant pages recursively). Fetches via API when login is required (using .env credentials).
---

# Jira / Confluence 페이지 링크 → 내용 정리 (Subagent 워크플로)

## 요청에 따른 동작 구분

| 사용자 요청 예시 | 동작 |
|------------------|------|
| **\<페이지 링크\> 요약해줘** / 정리해줘 / 내용 추출해줘 | **해당 페이지만** 가져와서 요약·정리한다. |
| **\<페이지 링크\> 하위 페이지까지 요약해줘** / 정리해줘 / 내용 추출해줘 | **전달한 링크의 하위 폴더를 포함해 재귀적으로 모든 페이지**를 가져와 요약·정리한다. 해당 페이지 + 직접 하위 + 하위의 하위 + … **전부** 포함. (Confluence 전용; Jira 이슈는 서브태스크가 이미 이슈 조회에 포함됨) |

사용자가 **Jira(또는 Atlassian) 페이지 URL**을 주고 위와 같이 요청하면 아래 워크플로를 따른다.

## 0. 인증 정보 저장 (한 번만 설정)

Jira 로그인이 필요한 페이지에 접근하려면 **저장된 인증 정보**를 사용한다.

- **저장 위치**: **프로젝트 루트(.ai)의 `.env`**에서 로드. 루트의 `.env.example`을 참고해 루트에 `.env`를 두고 값을 채운다.
- **필수 변수**: `ATLASSIAN_USER`(이메일), `ATLASSIAN_API_TOKEN` ([Atlassian API 토큰](https://id.atlassian.com/manage-profile/security/api-tokens) 발급)
- **선택 변수**: `ATLASSIAN_BASE_URL` (예: `https://your-domain.atlassian.net`)

인증이 필요한데 설정이 없거나 토큰이 비어 있으면, 사용자에게 "프로젝트 루트(.ai)의 .env에 ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN을 설정해 주세요"라고 안내한다.

## 1. URL로 내용 가져오기

1. **먼저 `mcp_web_fetch`로 해당 URL을 fetch한다.**
2. **결과 판단**
   - **200 + 본문 내용 있음** → 2단계(파싱·정리)로 진행.
   - **로그인 페이지 / 401·403 / JavaScript 로그인 요구** → **인증 경로 사용**:
     - **Jira 이슈 URL** (예: `.../browse/HCDOQ-1313`): 이슈 키 추출 후 `python .cursor/skills/wiki-page-summarizer/scripts/fetch_jira_issue.py <이슈키>` 실행. 성공 시 출력을 2단계 입력으로 사용.
     - **Confluence URL** (예: `.../wiki/.../pages/1997013274/...`): 페이지 ID 추출 후  
       - **해당 페이지만 요약** → `python .cursor/skills/wiki-page-summarizer/scripts/fetch_confluence_page.py <URL 또는 페이지ID>`  
       - **하위 페이지까지 요약** → `python .cursor/skills/wiki-page-summarizer/scripts/fetch_confluence_page.py <URL 또는 페이지ID> --with-children`  
       `--with-children` 사용 시 전달한 링크의 **하위 폴더를 포함해 재귀적으로 모든 페이지**를 가져온다. 스크립트는 프로젝트 루트(.ai)의 `.env`에서 `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN`을 로드하며, 성공 시 출력(본문 + 모든 하위·손자 페이지)을 2단계 입력으로 사용해 정리한다.
     - 스크립트 실패(인증 오류 등) 시: "프로젝트 루트(.ai)의 .env에 ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN이 올바른지 확인해 주세요. API 토큰은 https://id.atlassian.com/manage-profile/security/api-tokens 에서 발급할 수 있습니다." 안내. 그래도 안 되면 **본문을 복사해 붙여넣어 달라**고 요청한다.

## 2. 내용 파싱 및 정리

가져온 HTML/텍스트에서 다음을 추출해 구조화한다(있는 항목만 사용).

| 항목 | 설명 |
|------|------|
| **제목** | 이슈/페이지 제목 |
| **키(이슈 키)** | PROJ-123 등 |
| **상태** | To Do, In Progress, Done 등 |
| **우선순위** | Critical, High, Medium, Low |
| **담당자/리포터** | Assignee, Reporter |
| **설명** | Description 본문 |
| **요약(한 줄)** | 설명의 핵심을 1~2문장으로 |
| **체크리스트/서브태스크** | 할 일 목록, 하위 이슈 |
| **댓글/이력** | 최근 댓글·업데이트 요약(필요 시) |
| **라벨/컴포넌트** | 있는 경우 나열 |

## 3. 출력 형식(기본 템플릿)

사용자가 별도 형식을 요청하지 않으면 아래 마크다운 구조로 정리해 준다. **하위 페이지까지 요약**한 경우에는 본문 요약 후, **계층 구조(하위 > 하위의 하위 > …)**를 유지한 채 각 페이지별로 소제목을 붙여 요약을 이어 붙인다.

```markdown
# [이슈 키] 제목

## 요약
(한 줄 요약)

## 메타
- **상태**: (상태)
- **우선순위**: (우선순위)
- **담당자**: (담당자)
- **라벨/컴포넌트**: (있으면)

## 설명
(설명 본문 또는 요약)

## 할 일 / 서브태스크
- [ ] 항목1
- [ ] 항목2

## 참고 (댓글·이력)
(필요 시 최근 내용만 간단히)
```

## 4. 사용자 요청에 맞게 변형

- "요약만 해줘" → 요약 + 메타만.
- "액션 아이템만 뽑아줘" → 체크리스트/서브태스크 위주.
- "테이블로 정리해줘" → 메타·할 일을 표로 구성.
- "한국어로 정리해줘" → 전체를 한국어로 출력.

## 5. 인증 실패 시 대안

- **본문 붙여넣기**: 스크립트도 실패하거나 API 토큰을 쓰고 싶지 않으면, 사용자가 Jira에서 본문을 복사해 채팅에 붙여넣으면 같은 템플릿으로 파싱·정리.
- **API 토큰·비밀번호**: 코드나 스킬 파일에 절대 넣지 않고, 루트 `.env` 또는 환경 변수로만 참조한다.

## 요약

- **입력**: Jira(또는 Atlassian) 페이지 URL 또는 붙여넣은 본문.
- **처리**: "요약해줘" → 해당 페이지만 fetch. "**하위 페이지까지** 요약해줘" → Confluence인 경우 `fetch_confluence_page.py ... --with-children`로 전달한 링크의 **하위 폴더 포함 재귀적으로 모든 페이지**를 가져와 파싱·구조화.
- **출력**: 위 기본 템플릿 또는 사용자가 요청한 형식. 하위 포함 시에는 본문 요약 + 계층 구조를 유지한 채 각 페이지(직접 하위·손자·…)별 요약을 구분해 정리한다.
