# install-gstack

Garry Tan의 [gstack](https://github.com/garrytan/gstack)을 현재 프로젝트(또는 글로벌)에 설치하고, gstack 워크플로우 기준으로 CLAUDE.md를 갱신한다. 선택적으로 [GBrain](https://github.com/garrytan/gbrain)까지 함께 설치하고 Claude Code MCP에 등록한다.

## 설치

스킬 폴더를 원하는 위치에 복사합니다:

```bash
# 특정 프로젝트에서만 사용
cp -r .claude/skills/install-gstack <대상-프로젝트>/.claude/skills/install-gstack

# 모든 프로젝트에서 사용 (글로벌)
cp -r .claude/skills/install-gstack ~/.claude/skills/install-gstack
```

## 사전 요구사항

이 스킬은 별도 환경 변수가 필요하지 않습니다. 단, 다음 도구가 PATH에 있어야 합니다.

| 도구 | 필수 | 설명 |
|------|------|------|
| Claude Code CLI | Y | `claude --version` 으로 확인 |
| Bun 1.0+ | Y | gstack/GBrain 런타임. `curl -fsSL https://bun.sh/install \| bash` |
| Git | Y | `git clone` 사용 |

## 사용법

```
/install-gstack
```

스킬 실행 시 다음을 묻습니다.

1. **설치 범위** — 프로젝트 전용(`./.claude/skills/gstack`) vs 글로벌(`~/.claude/skills/gstack`)
2. **GBrain 동시 설치** — 예/아니오

CLAUDE.md가 이미 있으면 `CLAUDE.md.before-gstack` 으로 백업한 뒤, 새 CLAUDE.md 끝에 기존 내용 요약을 `## 기존 프로젝트 컨텍스트(요약)` 섹션으로 붙입니다.

## 참고 링크

- gstack: https://github.com/garrytan/gstack
- GBrain: https://github.com/garrytan/gbrain
- gstack 공식 사이트: https://gstacks.org
