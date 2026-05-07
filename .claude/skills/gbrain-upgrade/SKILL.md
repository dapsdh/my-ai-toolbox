---
name: gbrain-upgrade
description: >
  글로벌 설치된 Garry Tan의 GBrain(`bun add -g github:garrytan/gbrain` 으로 깔린 바이너리)을
  GitHub 최신 버전으로 업데이트하는 스킬. `bun add -g github:garrytan/gbrain` 을 다시 실행해
  깃 URL 패키지를 새로 받고, `gbrain doctor --json` 으로 헬스 체크 + DB 마이그레이션 필요 여부를 확인한다.
  설치되어 있지 않으면 `/install-gbrain`을 안내한다. gstack의 번들 슬래시 커맨드 `/gstack-upgrade`와
  대칭이 되도록 이름을 `gbrain-upgrade`로 둔다. 사용자가 "gbrain-upgrade", "gbrain 업데이트",
  "gbrain 최신으로", "/gbrain-upgrade", "두뇌 업데이트" 등을 입력하면 트리거한다.
allowed-tools:
  - Bash
---

# gbrain-upgrade

글로벌(`bun add -g`로 깔린) [GBrain](https://github.com/garrytan/gbrain)을 최신으로 업데이트한다. idempotent — 이미 최신이면 변화 없음을 보고하고 종료한다. DB 마이그레이션이 필요하면 `gbrain doctor` 가 알려주며, 사용자에게 다음 액션을 안내한다.

> 이름은 gstack의 번들 슬래시 커맨드 `/gstack-upgrade` 와 짝을 맞췄다.

## 사전 준비

별도 환경 변수는 필요 없다. 다음 도구가 PATH에 있어야 한다.

- **Bun 1.0+** (`bun --version`)
- **Claude Code CLI** (`claude --version`) — MCP 재연결 진단에 사용

또한 GBrain이 이미 설치되어 있어야 한다 (`/install-gbrain`).

## 워크플로우

### 1단계 — 설치 여부 확인

```bash
command -v gbrain && gbrain --version || echo "NOT_INSTALLED"
```

- `NOT_INSTALLED` 가 출력되면 다음 안내 후 종료한다:
  ```
  GBrain이 글로벌에 설치되어 있지 않습니다.
  먼저 `/install-gbrain` 을 실행해 주세요.
  ```
- 정상 출력되면 다음 단계로. 이때 출력된 버전 문자열을 `OLD_VERSION` 으로 보관한다.

### 2단계 — Bun으로 GitHub 최신 버전 재설치

`bun add -g github:garrytan/gbrain` 은 git URL 패키지를 매번 GitHub 기본 브랜치에서 다시 받아 설치한다. 따라서 **재실행이 곧 업그레이드**다.

```bash
# 업그레이드 전 위치 (참고용)
which gbrain

# GitHub 최신 main 브랜치를 받아 글로벌 재설치
bun add -g github:garrytan/gbrain

# 업그레이드 후 버전
gbrain --version
```

- 실패하면 stdout/stderr 그대로 사용자에게 보여주고 종료한다.
- 성공 후 새 버전 문자열을 `NEW_VERSION` 으로 보관한다.

### 3단계 — 헬스 체크 + 마이그레이션 안내

```bash
gbrain doctor --json
```

- 출력의 `status` 가 `healthy` 면 정상.
- DB 스키마 마이그레이션이 필요하다는 신호(예: `migrations_pending`, `schema_version_mismatch`)가 있으면 사용자에게 알리고 다음 명령을 안내한다 (gbrain의 표준 마이그레이션 명령은 버전마다 다를 수 있으므로 우선 `doctor` 출력을 그대로 보여주고, 추가 액션이 있으면 그 안내를 따른다):
  ```
  GBrain DB 스키마 마이그레이션이 필요해 보입니다. doctor 출력을 확인 후 안내된 명령을 실행하세요:

    gbrain doctor --json

  자동 마이그레이션 명령이 doctor 출력에 보이면 그대로 따라가고, 없으면 GitHub Releases / CHANGELOG를 확인하세요.
  ```

### 4단계 — Claude Code MCP 연결 확인 (선택)

```bash
claude mcp list | grep gbrain
```

- `gbrain` 항목이 있으면 그대로 OK. 사용자가 새 Claude Code 세션을 시작하면 새 버전의 `gbrain mcp serve` 가 자동으로 실행된다.
- 없으면 다음 명령으로 재등록 안내:
  ```
  Claude Code MCP에 gbrain 등록이 풀려 있습니다. 다음 명령으로 다시 등록하세요:
    claude mcp add gbrain -- gbrain mcp serve
  ```

### 5단계 — 결과 보고

다음 형식으로 사용자에게 요약을 출력한다.

```
GBrain 업그레이드 결과: {업데이트됨 / 동일 버전 / 마이그레이션 필요}

- 이전 버전: {OLD_VERSION}
- 현재 버전: {NEW_VERSION}
- 헬스 체크: {healthy / migrations_pending 등}
- MCP 등록 상태: {connected / 재등록 필요}

다음 단계
  1. 새 Claude Code 세션을 시작하면 새 버전의 gbrain MCP가 자동으로 사용됩니다.
  2. 마이그레이션이 필요하면 위 안내에 따라 처리해 주세요.
  3. 변경 로그: GitHub Releases / CHANGELOG (https://github.com/garrytan/gbrain/releases)
```

## 예시

### Input

```
/gbrain-upgrade
```

### Output (업데이트 발생)

```
[설치 확인]      gbrain 0.4.1 ✓
[bun add -g]     installed gbrain@github:garrytan/gbrain
[버전 비교]      0.4.1 → 0.5.0
[doctor]         status: healthy
[mcp list]       gbrain: connected ✓

GBrain 업그레이드 결과: 업데이트됨

- 이전 버전: 0.4.1
- 현재 버전: 0.5.0
- 헬스 체크: healthy
- MCP 등록 상태: connected

다음 단계
  1. 새 Claude Code 세션을 시작하면 새 버전의 gbrain MCP가 자동으로 사용됩니다.
  2. 변경 로그: https://github.com/garrytan/gbrain/releases
```

### Output (동일 버전)

```
[설치 확인]      gbrain 0.5.0 ✓
[bun add -g]     up-to-date (재설치 후에도 동일)
[버전 비교]      0.5.0 → 0.5.0  (동일)
[doctor]         status: healthy

GBrain 업그레이드 결과: 동일 버전 (이미 최신)

- 이전 버전: 0.5.0
- 현재 버전: 0.5.0
- 헬스 체크: healthy
- MCP 등록 상태: connected
```

### Output (마이그레이션 필요)

```
[설치 확인]      gbrain 0.4.1 ✓
[bun add -g]     installed gbrain@github:garrytan/gbrain
[버전 비교]      0.4.1 → 0.6.0
[doctor]         status: migrations_pending  schema_version: 12 → 14

GBrain 업그레이드 결과: 마이그레이션 필요

- 이전 버전: 0.4.1
- 현재 버전: 0.6.0
- 헬스 체크: migrations_pending (스키마 12 → 14)
- MCP 등록 상태: connected

다음 단계
  1. doctor 출력에 안내된 마이그레이션 명령을 따라 실행해 주세요.
  2. 변경 로그(0.5.x, 0.6.x) 확인: https://github.com/garrytan/gbrain/releases
```
