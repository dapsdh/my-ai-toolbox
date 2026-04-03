# save-article

웹 URL을 입력받아 해당 페이지의 제목과 요약을 추출한 뒤, 지정된 Confluence 페이지 하단에 구조화된 정리 내용을 추가한다.

## 설치

SKILL.md를 원하는 위치에 복사합니다:

```bash
# 특정 프로젝트에서만 사용
cp skills/save-article/SKILL.md <대상-프로젝트>/.claude/skills/save-article/SKILL.md

# 모든 프로젝트에서 사용 (글로벌)
cp skills/save-article/SKILL.md ~/.claude/skills/save-article/SKILL.md
```

## 환경 변수

환경 변수는 스킬 폴더의 `.env` 파일에서 먼저 찾고, 없는 경우 `~/.claude/.env`에서 찾습니다.

| 변수명 | 필수 | 설명 |
|--------|------|------|
| ATLASSIAN_BASE_URL | Y | Atlassian 인스턴스 URL (예: `https://hancom.atlassian.net`) |
| ATLASSIAN_USER | Y | Atlassian 계정 이메일 |
| ATLASSIAN_API_TOKEN | Y | Atlassian API 토큰 ([발급](https://id.atlassian.com/manage-profile/security/api-tokens)) |
| CONFLUENCE_PAGE_URL | Y | 항목을 추가할 Confluence 페이지 URL |

## 사용법

```
/save-article <article URL>
```
