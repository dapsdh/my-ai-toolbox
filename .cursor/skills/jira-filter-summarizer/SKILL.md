---
name: jira-filter-summarizer
description: Accepts a Jira filter page URL and "요약해줘", then summarizes each issue in the filter with description, comments, and code commits (GitLab push comments) in a fixed format. Use when the user pastes a Jira filter link and asks to summarize it ("필터 요약해줘", "요약해줘"). Fetches via Jira REST API using .env credentials; separates GitLab (e.g. gitlab.example.com) comments as "코드 커밋".
---

# Jira 필터 결과 요약 (Subagent/Skill)

사용자가 **Jira 필터 페이지 링크**와 함께 **"요약해줘"**를 입력하면, 필터에 걸린 **각 이슈**를 아래 포맷으로 정리한다.  
코드가 push될 때 **GitLab (e.g. gitlab.example.com)**가 Jira에 작성한 코멘트는 일반 코멘트와 구분해 **코드 커밋** 항목으로만 요약한다.

## 트리거

| 사용자 입력 예시 | 동작 |
|------------------|------|
| **\<Jira 필터 페이지 링크\> 요약해줘** / 필터 요약해줘 / 정리해줘 | 필터 결과 이슈 목록을 가져와, 이슈별로 아래 출력 포맷으로 요약·정리한다. |

예: `https://example.atlassian.net/issues/?filter=12345 요약해줘`

## 인증

- Jira 인증은 **프로젝트 루트(.ai)의 `.env`**에서 로드한다. 루트의 `.env.example`을 참고해 루트에 `.env`를 두고 `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN`을 채운다.
- 인증이 없으면 "프로젝트 루트(.ai)의 .env에 ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN을 설정해 주세요" 안내.

## 워크플로

1. **URL에서 필터 ID 추출**  
   필터 페이지 URL에서 `filter=숫자` 또는 `filter/id/숫자` 형태로 filter ID를 추출한다.  
   (예: `https://example.atlassian.net/issues/?filter=12345` → `12345`)

2. **필터 JQL 조회**  
   `python .cursor/skills/jira-filter-summarizer/scripts/jira/summarize_jira_filter.py <필터_URL_또는_filter_ID>` 를 실행한다.  
   스크립트는 내부적으로:
   - `GET /rest/api/3/filter/{id}` 로 필터의 JQL을 가져오고
   - `GET /rest/api/3/search?jql=...` 로 이슈 목록을 조회한 뒤
   - 각 이슈에 대해 이슈 상세 + 코멘트(`GET /rest/api/3/issue/{key}/comment`)를 조회한다.

3. **코멘트 분류**  
   - **코드 커밋**: 작성자 `displayName`(또는 계정 식별자)이 **GitLab (e.g. gitlab.example.com)** 또는 **GitLab** 관련 봇인 코멘트.  
     (예: `gitlab.example.com`, `GitLab` 등 포함 시 코드 커밋으로 간주)
   - **코멘트**: 위가 아닌 나머지 코멘트.

4. **출력 포맷**  
   스크립트 출력을 그대로 사용하거나, 에이전트가 아래 형식에 맞게 정리해 사용자에게 보여 준다.

## 출력 포맷 (이슈당)

```text
[이슈키] 이슈 요약문 (상태)
 - 설명: ~~
 - 코멘트: ~~
 - 코드 커밋: ~~
```

- **이슈키**: Jira 이슈 키 (예: PROJ-123).
- **이슈 요약문**: 이슈의 Summary 한 줄.
- **상태**: 현재 상태 (예: To Do, In Progress, Done).
- **설명**: Description 본문 요약 또는 전문(짧을 경우).
- **코멘트**: GitLab 봇이 **아닌** 코멘트만 요약·나열.
- **코드 커밋**: **GitLab**(및 동일 봇, e.g. gitlab.example.com)가 작성한 코멘트만 요약·나열 (push 시 자동 작성 코멘트).

항목이 없으면 해당 줄은 생략하거나 "(없음)"으로 표시한다.

## 스크립트 사용

```bash
python .cursor/skills/jira-filter-summarizer/scripts/jira/summarize_jira_filter.py "https://example.atlassian.net/issues/?filter=12345"
# 또는
python .cursor/skills/jira-filter-summarizer/scripts/jira/summarize_jira_filter.py 12345
```

성공 시: 표준 출력에 위 포맷의 요약이 이슈별로 출력된다.  
실패 시: stderr에 오류 메시지, exit code 1. 인증 실패 시 사용자에게 루트 .env 설정 안내.

## 요약

- **입력**: Jira 필터 페이지 URL + "요약해줘".
- **처리**: 필터 ID → JQL → 이슈 목록 → 이슈별 상세·코멘트 조회 → GitLab 봇 코멘트는 "코드 커밋", 나머지는 "코멘트"로 구분.
- **출력**: `[이슈키] 이슈 요약문 (상태)` + 설명 / 코멘트 / 코드 커밋 포맷으로 정리.
