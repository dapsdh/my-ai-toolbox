---
name: jira-bug-analyzer
description: Accepts a Jira issue URL, then analyzes the issue description, finds problem code if it is a fixable bug, and suggests fixes. Use when the user pastes a Jira issue link and asks to find problem code or debug ("문제코드를 찾아줘", "디버깅해줘"). Uses project root .env for Jira auth.
argument-hint: <Jira 이슈 URL>
allowed-tools: Bash, Grep, Glob, Read
---

# Jira 이슈 기반 문제 코드 찾기 / 디버깅

사용자 입력: $ARGUMENTS

위 입력에서 **Jira 이슈 URL**을 추출해 아래 워크플로를 따른다.

## 인증

- Jira 인증은 **프로젝트 루트(.ai)의 `.env`**에서 로드한다.
- **필수 변수**: `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN`
- 인증이 없거나 API 호출이 실패하면 "프로젝트 루트(.ai)의 .env에 ATLASSIAN_USER(이메일)와 ATLASSIAN_API_TOKEN을 설정해 주세요" 안내 후, 사용자에게 이슈 설명을 직접 붙여넣어 달라고 요청할 수 있다.

## 이슈 내용 가져오기

1. URL에서 이슈 키 추출 (예: `.../browse/PROJ-123` → `PROJ-123`).
2. 다음 명령으로 이슈 상세(제목, 설명, 상태 등)를 가져온다.
   ```bash
   python .claude/skills/jira-bug-analyzer/scripts/jira/fetch_jira_issue.py <이슈키 또는 URL>
   ```
   출력을 1단계(분석)의 입력으로 사용한다.

## 워크플로

### 1. 이슈 설명 분석

해당 Jira 이슈의 **설명(Description)**과 제목·상태 등을 보고 **무엇이 문제인지** 분석한다.

- 현상, 재현 절차, 예상 동작 vs 실제 동작, 로그/에러 메시지, 환경 정보 등을 정리한다.
- **판단**: 이 이슈가 **코드 수정이 필요한 문제(버그/개선)**인지, 아니면 **수정이 필요 없는 경우**(문의만 있음, 이미 해결됨, 설정/운영 이슈만 해당, 요청이 모호함 등)인지 결정한다.

### 2. 분기 처리

#### 2.1 수정이 필요한 문제인 경우

- **2.1.1 문제 코드 찾기**
  이슈 설명에 나온 **모듈명, 파일명, 함수명, 키워드, 스택 트레이스, API 경로** 등을 바탕으로 현재 **프로젝트 코드베이스**에서 관련 코드를 검색한다.
  (codebase search, grep, 파일 탐색 등 활용.)

- **문제 코드를 찾은 경우**
  - 해당 코드 위치(파일:줄 또는 경로)를 명시하고,
  - **어떻게 수정하면 좋을지** 구체적으로 분석·제안한다.
  - 가능하면 수정 예시(패치 스니펫)를 제시한다.

- **문제 코드를 찾지 못한 경우**
  - **"버그 분석 실패"**라고 사용자에게 알린다.
  - 가능한 이유(키워드 부족, 다른 레포/서비스 코드, 빌드 산출물만 해당 등)를 짧게 적을 수 있다.

#### 2.2 수정이 필요한 문제가 아닌 경우

- **그 이유를 설명**한다.
  예: "이슈는 기능 문의이며 재현 가능한 버그가 아님", "이미 다른 이슈로 수정된 내용임", "코드 변경이 아닌 설정/배포 이슈로 보임" 등.

## 출력 요약

| 상황 | 출력 |
|------|------|
| 수정 필요 + 문제 코드 발견 | 문제 요약, 코드 위치, 수정 방안(및 예시) |
| 수정 필요 + 문제 코드 미발견 | "버그 분석 실패" + 간단한 이유 |
| 수정 불필요 | 수정이 필요하지 않은 이유 설명 |
