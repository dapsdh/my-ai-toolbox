# gbrain-upgrade

글로벌 설치된 [GBrain](https://github.com/garrytan/gbrain)을 GitHub 최신 버전으로 업데이트한다. `bun add -g github:garrytan/gbrain` 을 다시 실행하여 깃 URL 패키지를 새로 받고, `gbrain doctor --json` 으로 헬스 체크 + DB 마이그레이션 필요 여부를 확인한다. 이름은 gstack 번들 슬래시 커맨드 `/gstack-upgrade` 와 짝을 맞췄다.

> gstack 자체 업그레이드는 gstack에 번들된 `/gstack-upgrade` 슬래시 커맨드를 그대로 쓰면 된다 (`/install-gstack` 후 자동 활성화).

## 설치

스킬 폴더를 원하는 위치에 복사합니다:

```bash
cp -r .claude/skills/gbrain-upgrade ~/.claude/skills/gbrain-upgrade
```

## 사전 요구사항

별도 환경 변수는 필요 없습니다.

| 도구 | 필수 | 설명 |
|------|------|------|
| Bun 1.0+ | Y | `bun add -g` 사용 |
| Claude Code CLI | Y | `claude mcp list` 로 MCP 연결 확인 |

또한 GBrain이 이미 설치돼 있어야 합니다 (`/install-gbrain`).

## 사용법

```
/gbrain-upgrade
```

질문 없음, idempotent. 동작 흐름:

1. `command -v gbrain` 으로 설치 여부 확인 — 없으면 `/install-gbrain` 안내 후 종료
2. `bun add -g github:garrytan/gbrain` 으로 GitHub 최신 main 브랜치 재설치
3. `gbrain --version` 으로 새 버전 확인 + 이전 버전과 비교
4. `gbrain doctor --json` 으로 헬스 체크 — 스키마 마이그레이션 필요 시 안내
5. `claude mcp list` 로 MCP 등록 상태 확인
6. 결과 보고 (이전/현재 버전, 헬스 상태, MCP 연결, 다음 단계)

업그레이드 후 새 Claude Code 세션을 시작하면 새 버전의 `gbrain mcp serve` 가 자동으로 사용됩니다.

## 참고 링크

- GBrain: https://github.com/garrytan/gbrain
- GBrain Releases: https://github.com/garrytan/gbrain/releases
- gstack: https://github.com/garrytan/gstack
