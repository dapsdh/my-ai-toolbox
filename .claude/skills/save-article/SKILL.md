---
name: save-article
argument-hint: "<article URL>"
description: >
  웹 URL을 입력받아 해당 페이지의 제목과 요약을 추출한 뒤,
  지정된 Confluence 페이지 하단에 링크와 요약을 추가하는 스킬.
  사용자가 "save-article", "아티클 저장", "기사 저장", "이 글 저장해줘",
  "URL 컨플루언스에 추가", "페이지에 링크 추가" 등을 입력하면 트리거한다.
allowed-tools:
  - Read
  - Bash
  - WebFetch
  - AskUserQuestion
---

# save-article

웹 URL을 입력받아 해당 페이지의 제목과 요약을 추출하고, 지정된 Confluence 페이지에 항목을 추가한다. 동일 URL이 이미 있으면 해당 섹션 바로 아래에 삽입하여 비교할 수 있게 한다.

## 사전 준비

환경 변수는 스킬 폴더의 `.env` 파일에서 먼저 찾고, 없는 경우 `~/.claude/.env`에서 찾는다.

- `ATLASSIAN_BASE_URL` : Atlassian 인스턴스 URL (예: `https://hancom.atlassian.net`)
- `ATLASSIAN_USER` : Atlassian 계정 이메일
- `ATLASSIAN_API_TOKEN` : Atlassian API 토큰
- `CONFLUENCE_PAGE_URL` : 항목을 추가할 Confluence 페이지 URL (예: `https://hancom.atlassian.net/wiki/spaces/example/pages/1234567890`)

## 워크플로우

### 0단계: URL 입력 확인

스킬 인자(ARGUMENTS)로 URL이 전달되었으면 그대로 사용한다. URL이 없으면 AskUserQuestion 도구로 입력을 요청한다.

- question: "저장할 웹 페이지 URL을 입력해 주세요. (예: https://example.com/article)"
- header: "URL"
- options: 사용자가 직접 입력할 수 있도록 일반적인 선택지만 제공한다:
  - "직접 입력" — "저장할 아티클의 웹 URL을 입력하세요"
  - "취소" — "스킬 실행을 취소합니다"

### 1단계: 환경 변수 로드

1. 스킬 폴더의 `.env` 파일을 읽어 환경 변수를 파싱한다.
2. 스킬 폴더 `.env`에 없는 변수는 `~/.claude/.env`에서 찾는다.
3. `CONFLUENCE_PAGE_URL`에서 **pageId**를 추출한다 (URL 경로의 `pages/` 뒤 숫자).

### 2단계: 웹 페이지 내용 가져오기

1. 사용자가 제공한 웹 URL에 대해 **WebFetch** 도구를 사용한다.
2. 프롬프트:
   ```
   이 웹 페이지의 내용을 한국어로 기술 문서 스타일로 정리해줘.
   독자가 기술의 흐름과 핵심 원리를 쉽게 이해할 수 있도록 구어체와 문어체를 적절히 섞어 작성해.
   반드시 다음 형식으로 응답해:

   제목: <한국어 제목: 원문 주제를 반영한 설명적 제목>
   원문_제목: <원문 페이지의 제목 원어 그대로>
   요약: <전체 내용을 관통하는 핵심 개념 1-2문장>

   상세_내용:
   ### <주제 1: 문제 제기나 핵심 배경>
   <해당 주제에 대한 설명. 비유나 쉬운 용어를 사용하여 2-3개 문장으로 작성. 필요시 글머리 기호 사용>

   ### <주제 2: 해결책이나 핵심 기술>
   <해당 기술의 동작 원리와 특징 설명>

   ### <주제 3: 발전 방향이나 구성 요소>
   <단계별 프로세스나 에이전트의 역할 등 기술의 심화 내용>

   ### <주제 4: 인프라 및 기반 환경> (내용이 있을 경우만)
   <시맨틱 레이어, 거버넌스 등 기반 환경 설명>

   핵심_인사이트: <이 글에서 가장 중요한 결론이나 시사점을 인용구 스타일로 1-2문장>
   ```
3. 응답에서 **제목**, **원문_제목**, **요약**, **주제 1**, **주제 2**, **주제 3**, **주제 4**, **핵심_인사이트**를 추출한다. 내용이 없는 카테고리는 생략한다.
4. WebFetch가 실패하면(SSL 오류 등) curl -sL -k로 HTML을 가져온 뒤 메타 태그(og:title, og:description)와 본문에서 직접 분석한다.

### 3단계: 기존 Confluence 페이지 내용 조회

Bash 도구로 Confluence REST API를 호출하여 현재 페이지 내용을 가져온다.

```bash
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" \
  "$ATLASSIAN_BASE_URL/wiki/rest/api/content/$PAGE_ID?expand=body.storage,version" \
  -H "Accept: application/json"
```

API 응답의 HTTP 상태 코드를 확인한다:
- **404 또는 페이지를 찾을 수 없는 경우**: 사용자에게 `"CONFLUENCE_PAGE_URL에 해당하는 페이지를 찾을 수 없습니다. URL을 확인해 주세요: {CONFLUENCE_PAGE_URL}"` 메시지를 출력하고 스킬을 종료한다.
- **401/403 (인증 실패)**: 사용자에게 인증 정보를 확인하라는 메시지를 출력하고 종료한다.
- **성공 시** 응답에서 다음을 추출한다:
  - `body.storage.value` : 현재 페이지 HTML 본문
  - `version.number` : 현재 버전 번호

### 4단계: 새 항목 생성 및 페이지 업데이트

1. 현재 날짜를 `YYYY-MM-DD` 형식으로 구한다.
2. **삽입 위치를 결정한다:**
   - 기존 본문 HTML에서 저장할 URL(`href="원본URL"`)이 포함된 `<h2>` 섹션이 있는지 검색한다.
   - **동일 URL 섹션이 있는 경우**: 해당 섹션의 끝(= 다음 `<hr/>` 직전)을 찾아 그 위치에 새 항목을 삽입한다. 이렇게 하면 같은 기사의 두 버전이 나란히 배치되어 사용자가 비교 후 더 나은 것을 남길 수 있다.
   - **동일 URL 섹션이 없는 경우**: 기존 본문 HTML 끝에 추가한다.
3. 다음 형식의 항목을 생성한다.

**HTML 템플릿** (아래 구조를 반드시 따른다):

```html
<hr/>
<h2>제목 <em>(YYYY-MM-DD)</em></h2>
<p>요약 1-2문장.</p>
<p><a href="원본URL">원문 제목 (원어 그대로)</a></p>
<h3>소제목 (주제 1)</h3>
<p>설명 텍스트...</p>
  <ul>
    <li><p>중요 포인트...</p></li>
  </ul>
<h3>소제목 (주제 2)</h3>
<p>설명 텍스트...</p>
<h3>요약</h3>
<p>이 글에서 가장 중요한 인사이트 1-2문장</p>
```

**참고**: Confluence의 기존 항목(예: "Document Indexing Summarizer" 섹션)과 동일한 깊이와 구조로 작성한다. **내용이 없는 카테고리(동작 원리, 기법, 구성요소, 주요 모델)는 반드시 생략한다.**

3. Confluence REST API로 페이지를 업데이트한다:

```bash
curl -s -u "$ATLASSIAN_USER:$ATLASSIAN_API_TOKEN" \
  -X PUT \
  "$ATLASSIAN_BASE_URL/wiki/rest/api/content/$PAGE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "version": { "number": 새버전번호 },
    "title": "기존페이지제목",
    "type": "page",
    "body": {
      "storage": {
        "value": "업데이트된HTML본문",
        "representation": "storage"
      }
    }
  }'
```

**주의**: 버전 번호는 기존 버전 + 1 이어야 한다.

### 5단계: 결과 보고

성공 시 다음 정보를 사용자에게 보고한다:
- 저장된 아티클 제목
- 요약 내용
- Confluence 페이지 URL (사용자가 바로 확인할 수 있도록)

실패 시 오류 메시지와 가능한 원인(인증 실패, 페이지 권한 등)을 안내한다.

## 예시

### Input

```
save-article https://techblog.example.com/2024/microservices-patterns
```

### Output (Confluence에 추가되는 내용)

```html
<hr/>
<h2>마이크로서비스 디자인 패턴 실전 가이드 <em>(2026-04-02)</em></h2>
<p>마이크로서비스 아키텍처에서 자주 사용되는 핵심 패턴들을 실제 사례와 함께 설명한다.</p>
<p><a href="https://techblog.example.com/2024/microservices-patterns">Microservices Design Patterns: A Practical Guide</a></p>
<h3>주요 내용</h3>
<ul>
  <li><p>모놀리스에서 마이크로서비스로의 전환 시 고려사항</p></li>
  <li><p>서비스 간 통신에서 동기/비동기 방식의 트레이드오프</p></li>
  <li><p>데이터 일관성 유지를 위한 분산 트랜잭션 전략</p></li>
</ul>
<h3>동작 원리</h3>
<ol>
  <li><p>API Gateway가 클라이언트 요청을 수신하여 해당 서비스로 라우팅</p></li>
  <li><p>각 서비스는 독립 DB를 소유하며 이벤트 버스를 통해 상태 변경을 전파</p></li>
  <li><p>Saga 오케스트레이터가 분산 트랜잭션의 성공/실패를 관리하고 보상 트랜잭션 실행</p></li>
</ol>
<h3>기법</h3>
<ol>
  <li><p><strong>Saga Pattern</strong><br/>분산 트랜잭션을 로컬 트랜잭션 체인으로 분리. Choreography와 Orchestration 두 가지 방식</p></li>
  <li><p><strong>CQRS</strong><br/>읽기와 쓰기 모델을 분리하여 각각 최적화. 이벤트 소싱과 결합 시 효과적</p></li>
  <li><p><strong>Event Sourcing</strong><br/>상태 변경을 이벤트로 저장. 완전한 감사 추적과 시점 복원 가능</p></li>
</ol>
<!-- "구성요소"와 "주요 모델"은 이 글에 해당 내용이 없으므로 생략 -->
<h3>핵심 인사이트</h3>
<p>패턴 선택은 팀의 운영 역량과 비즈니스 복잡도에 따라 달라지며, 단순한 서비스에 복잡한 패턴을 적용하는 것이 가장 흔한 실수다.</p>
```

### Output (사용자에게 표시)

```
아티클을 Confluence 페이지에 저장했습니다.

- 제목: 마이크로서비스 디자인 패턴 실전 가이드
- 날짜: 2026-04-02
- 페이지: https://hancom.atlassian.net/wiki/spaces/example/pages/1234567890
```
