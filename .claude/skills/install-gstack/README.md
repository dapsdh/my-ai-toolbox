# install-gstack

Garry Tan의 [gstack](https://github.com/garrytan/gstack)을 **글로벌 1회**(`~/.claude/skills/gstack`)에 설치하는 스킬. 한 번만 깔아두면 `/office-hours`, `/autoplan`, `/review`, `/qa`, `/ship` 등 23+개 슬래시 커맨드가 모든 프로젝트에서 사용 가능해진다. idempotent — 이미 설치돼 있으면 자동으로 건너뛴다.

이 스킬은 **글로벌 설치만** 다룬다. 프로젝트별 설정(team 부트스트랩, CLAUDE.md 갱신)은 하지 않는다.

> [GBrain](https://github.com/garrytan/gbrain) 설치는 별도 스킬 `/install-gbrain` 을 사용한다.

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
| Bun 1.0+ | Y | gstack 런타임. `curl -fsSL https://bun.sh/install \| bash` |
| Git | Y | `git clone` 사용 |

## 사용법

```
/install-gstack
```

질문 없음, idempotent. 다음 흐름으로 동작합니다.

1. 사전 요구사항 점검 (claude / bun / git)
2. `~/.claude/skills/gstack` 존재 확인 — 있으면 안내만 하고 종료
3. 없으면 글로벌 클론 + `./setup` (각 스킬이 `~/.claude/skills/<skill>/` 로 심링크되어 슬래시 커맨드 등록)
4. 결과 보고

업데이트는 `/gstack-upgrade`, 완전 재설치는 `rm -rf ~/.claude/skills/gstack && /install-gstack`.

GBrain(개인 두뇌, MCP 서버)을 함께 쓰려면 `/install-gbrain` 을 별도로 한 번 실행하세요.

## 참고 링크

- gstack: https://github.com/garrytan/gstack
- GBrain: https://github.com/garrytan/gbrain
- gstack 공식 사이트: https://gstacks.org
