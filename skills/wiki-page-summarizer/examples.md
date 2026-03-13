# Wiki 페이지 정리 — 사용 예시

## 예시 1: URL로 요청

**사용자**:  
`https://hancom.atlassian.net/browse/HCDOQ-1313` 이 이슈 내용 정리해줘

**에이전트**:
1. `mcp_web_fetch`로 URL fetch 시도
2. 로그인 페이지면 → "로그인이 필요합니다. 본문을 복사해 붙여넣어 주시면 정리해 드리겠습니다."
3. 성공 시 → SKILL.md의 기본 템플릿으로 정리해 출력

---

## 예시 2: 본문 붙여넣기

**사용자**:  
Jira 로그인이라 못 가져온다며, 아래 복사한 거 정리해줘.

```
HCDOQ-1313 [국회도서관] 키워드 검색 부하테스트 성능 관련 문의 (긴급)
Status: In Progress
Assignee: 홍길동
Description:
개발 환경에서는 retrieval이 빠른데 배포(국회 도서관)에서는 10배 이상 느립니다.
원인 파악 및 개선 방안을 정리해 주세요.
```

**에이전트**:  
동일한 메타·요약·설명 구조로 마크다운 정리해 출력.

---

## 예시 3: 형식 지정

**사용자**:  
위 이슈에서 **액션 아이템만** 뽑아줘.

**에이전트**:  
할 일/서브태스크·체크리스트 위주로만 bullet 또는 테이블로 출력.

---

## 예시 4: Confluence — 해당 페이지만 요약

**사용자**:  
`https://hancom.atlassian.net/wiki/.../pages/1997013274/M11+document+retrieval` 요약해줘

**에이전트**:  
`fetch_confluence_page.py <URL>` 실행(옵션 없음) → 해당 페이지만 가져와 요약·정리.

---

## 예시 5: Confluence — 하위 페이지(폴더)까지 모두 요약

**사용자**:  
`https://hancom.atlassian.net/wiki/.../pages/1997013274/M11+document+retrieval` **하위 페이지까지** 요약해줘

**에이전트**:  
`fetch_confluence_page.py <URL> --with-children` 실행 → 본문 + **직접 하위 + 그 하위의 하위 + …** 를 재귀적으로 모두 가져온 뒤, 계층 구조를 유지한 채 본문 요약 + 각 페이지별 요약을 구분해 정리.
