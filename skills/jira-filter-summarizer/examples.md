# Jira 필터 요약 사용 예시

## 입력

- `https://example.atlassian.net/issues/?filter=12345 요약해줘`
- `https://example.atlassian.net/issues/?filter=12345` (에이전트가 "요약해줘" 컨텍스트로 실행)

## 출력 예시

```
[PROJ-101] 로그인 API 개선 (In Progress)
 - 설명: 기존 Basic 인증을 JWT 기반으로 전환합니다.
 - 코멘트: QA 환경에서만 먼저 적용 요청했습니다. | 리뷰 반영했습니다.
 - 코드 커밋: (없음)

[PROJ-102] 배치 타임아웃 수정 (Done)
 - 설명: 대용량 처리 시 타임아웃이 발생하는 문제 수정.
 - 코멘트: (없음)
 - 코드 커밋: 2 commits, branch feature/PROJ-102, pushed to main. | 1 commit, branch hotfix/PROJ-102.
```

GitLab에서 push 시 Jira에 남는 코멘트는 작성자가 **GitLab**(e.g. gitlab.example.com) 등으로 등록되어 있어, 위와 같이 "코드 커밋" 항목에만 모아서 표시된다.
