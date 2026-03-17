---
name: gitlab-mr-code-review
description: Accepts a GitLab merge request URL, then fetches the MR metadata and diffs via GitLab API using .env credentials and performs a structured code review. Use when the user pastes a GitLab MR link (e.g. gitlab.example.com/.../merge_requests/23/diffs) and asks for a code review ("코드 리뷰 해줘", "리뷰해줘").
argument-hint: <GitLab MR URL>
allowed-tools: Bash
---

# GitLab MR 코드 리뷰

사용자 입력: $ARGUMENTS

위 입력에서 **GitLab 머지 리퀘스트 URL**을 추출해 아래 워크플로를 따른다.

## 인증

- GitLab 인증은 **프로젝트 루트(.ai)의 `.env`**에서 로드한다.
- **필수 변수**: `GITLAB_PRIVATE_TOKEN` 또는 `GITLAB_ACCESS_TOKEN`
- **선택 변수**: `GITLAB_HOST` (기본값: URL에서 자동 추출)
- 인증이 없으면 "프로젝트 루트(.ai)의 .env에 GITLAB_PRIVATE_TOKEN(또는 GITLAB_ACCESS_TOKEN)을 설정해 주세요" 안내.

## 워크플로

1. **URL에서 호스트·프로젝트·MR 번호 추출**
   - `https://gitlab.example.com/group/subgroup/project/-/merge_requests/23` 또는 `.../merge_requests/23/diffs` 형태에서
     호스트(`gitlab.example.com`), 프로젝트 경로(`group/subgroup/project`), MR IID(`23`) 추출.

2. **MR diff 조회**
   ```bash
   python skills/gitlab-mr-code-review/scripts/fetch_mr_diffs.py "<MR_URL>"
   ```
   스크립트는:
   - `GET /api/v4/projects/:id/merge_requests/:merge_request_iid/changes` 로 MR 메타데이터와 변경 파일 목록·diff 조회.
   - 프로젝트 ID는 URL 인코딩된 프로젝트 경로(예: `platform-api%2Fchatbot%2Ffrontend-lib`).

3. **코드 리뷰 수행**
   스크립트 출력(MR 제목, 설명, 변경 파일별 diff)을 바탕으로 에이전트가 코드 리뷰를 수행한다.
   - 로직·버그·엣지 케이스, 보안, 가독성·유지보수성, 스타일·컨벤션, 테스트·문서화 등을 검토.
   - 아래 출력 포맷에 맞춰 정리해 사용자에게 보여 준다.

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

스크립트는 Python 표준 라이브러리만 사용하므로 별도 패키지 설치가 필요 없다.
