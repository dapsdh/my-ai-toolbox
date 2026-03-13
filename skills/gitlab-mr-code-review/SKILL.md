---
name: gitlab-mr-code-review
description: Accepts a GitLab merge request URL and "코드 리뷰 해줘", then fetches the MR metadata and diffs via GitLab API using .env credentials and performs a structured code review. Use when the user pastes a GitLab MR link (e.g. gitlab.example.com/.../merge_requests/23/diffs) and asks for a code review ("코드 리뷰 해줘", "리뷰해줘").
---

# GitLab MR 코드 리뷰

사용자가 **GitLab 머지 리퀘스트 URL**과 함께 **"코드 리뷰 해줘"**를 입력하면, GitLab API로 MR 정보와 diff를 가져온 뒤 **구조화된 코드 리뷰**를 수행해 아래 출력 포맷으로 정리한다.

## 트리거

| 사용자 입력 예시 | 동작 |
|------------------|------|
| **\<GitLab MR URL\> 코드 리뷰 해줘** / 리뷰해줘 / 리뷰 부탁해 | MR URL에서 호스트·프로젝트·MR 번호를 추출해 diff를 가져온 뒤, 코드 리뷰를 수행해 아래 포맷으로 출력한다. |

예: `https://gitlab.example.com/platform-api/chatbot/frontend-lib/-/merge_requests/23/diffs 코드 리뷰 해줘`

## 인증

- GitLab 인증은 **프로젝트 루트(.ai)의 `.env`**에서 로드한다. 루트의 `.env.example`을 참고해 루트에 `.env`를 두고 `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN`, (선택) `GITLAB_HOST`를 채운다.
- 인증이 없으면 "프로젝트 루트(.ai)의 .env에 GITLAB_PRIVATE_TOKEN(또는 GITLAB_ACCESS_TOKEN)을 설정해 주세요" 안내.

## 워크플로

1. **URL에서 호스트·프로젝트·MR 번호 추출**  
   - `https://gitlab.example.com/group/subgroup/project/-/merge_requests/23` 또는 `.../merge_requests/23/diffs` 형태에서  
     호스트(`gitlab.example.com`), 프로젝트 경로(`group/subgroup/project`), MR IID(`23`) 추출.

2. **MR diff 조회**  
   `python .cursor/skills/gitlab-mr-code-review/scripts/fetch_mr_diffs.py "<MR_URL>"` 를 실행한다.  
   스크립트는:
   - `GET /api/v4/projects/:id/merge_requests/:merge_request_iid/changes` 로 MR 메타데이터와 변경 파일 목록·diff 조회.
   - 프로젝트 ID는 URL 인코딩된 프로젝트 경로(예: `platform-api%2Fchatbot%2Ffrontend-lib`).

3. **코드 리뷰 수행**  
   스크립트 출력(MR 제목, 설명, 변경 파일별 diff)을 바탕으로 에이전트가 코드 리뷰를 수행한다.  
   - 로직·버그·엣지 케이스, 보안, 가독성·유지보수성, 스타일·컨벤션, 테스트·문서화 등을 검토.
   - 아래 출력 포맷에 맞춰 정리해 사용자에게 보여 준다.

4. **출력 포맷**  
   에이전트가 아래 형식에 맞게 리뷰 결과를 정리한다.

## 출력 포맷 (리뷰 결과)

```text
# [MR 제목] (!MR번호)

## 요약
- 소스 브랜치 → 타깃 브랜치, 변경 파일 N개
- (MR 설명 요약 또는 한 줄 요약)

## 파일별 리뷰

### [파일 경로]
- **리뷰 의견**: (해당 파일에 대한 종합 의견, 필수 수정/권장/참고 등)
- **코드 라인별 코멘트** (있을 경우):
  - Ln: (의견)

### [다음 파일]
...
```

- **필수 수정**: 반드시 고쳐야 할 항목.
- **권장**: 개선을 권하는 항목.
- **참고**: 참고만 하면 되는 항목.

## 스크립트 사용

스크립트는 Python 표준 라이브러리만 사용하므로 별도 패키지 설치가 필요 없다.

```bash
python .cursor/skills/gitlab-mr-code-review/scripts/fetch_mr_diffs.py "https://gitlab.example.com/platform-api/chatbot/frontend-lib/-/merge_requests/23/diffs"
```

성공 시: 표준 출력에 MR 제목·설명·변경 파일별 diff가 출력된다. 에이전트는 이 내용을 바탕으로 코드 리뷰를 작성한다.  
실패 시: stderr에 오류 메시지, exit code 1. 인증 실패 시 사용자에게 루트 .env 설정 안내.

## 요약

- **입력**: GitLab MR URL + "코드 리뷰 해줘".
- **처리**: URL 파싱 → GitLab API로 MR changes(diff) 조회 → 코드 리뷰 수행.
- **출력**: MR 요약 + 파일별 리뷰(의견·라인별 코멘트) 포맷으로 정리.
