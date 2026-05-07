---
name: install-gbrain
description: >
  Garry Tan의 GBrain(개인 두뇌, MCP 서버)을 설치·초기화하고 Claude Code의 MCP 레지스트리에 등록하는 스킬.
  GBrain은 머신·사용자 단위 글로벌 1회 설치를 전제로 하므로, 첫 실행 시에만 본격적인 설치를 수행하고
  이후 호출에서는 이미 설치된 상태를 감지해 자동으로 건너뛴다. 선택적으로 Dream Cycle cron 등록과
  초기 노트 import 까지 한 번에 처리한다.
  사용자가 "install-gbrain", "gbrain 설치", "두뇌 설치", "MCP에 gbrain 등록",
  "/install-gbrain" 등을 입력하면 트리거한다.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# install-gbrain

Garry Tan의 [GBrain](https://github.com/garrytan/gbrain)은 사용자 단위의 개인 두뇌(Source of Truth, Postgres + pgvector / PGLite)다. `bun add -g`로 글로벌 설치하고 `claude mcp add gbrain` 으로 Claude Code MCP에 한 번 등록해 두면, 모든 프로젝트에서 같은 두뇌를 공유한다.

이 스킬은 다음을 보장한다:

1. 사전 요구사항 확인 (Claude Code, Bun)
2. **글로벌 GBrain 설치** (`bun add -g github:garrytan/gbrain`) — 이미 있으면 건너뜀
3. PGLite DB 초기화 (`gbrain init`) — 이미 초기화돼 있으면 건너뜀
4. Claude Code MCP에 `gbrain` 등록 — 이미 등록돼 있으면 건너뜀
5. (선택) Dream Cycle 야간 cron 등록
6. (선택) 초기 노트 import + 임베딩
7. (선택) 현재 프로젝트 `CLAUDE.md`에 "## GBrain 연동" 섹션 추가

## 사전 준비

별도 환경 변수는 필요 없다. 다음 도구가 PATH에 있어야 한다.

- **Claude Code CLI** (`claude --version`)
- **Bun 1.0+** (`bun --version`)

## 워크플로우

### 0단계 — 옵션 확인

`AskUserQuestion` 도구로 두 가지를 묻는다 (글로벌 설치 자체는 항상 수행).

1. **Dream Cycle cron 등록**
   - header: "야간 Cron"
   - question: "GBrain의 Dream Cycle(야간 학습 루프)을 매일 새벽 3시에 자동 실행하도록 cron에 등록할까요?"
   - options:
     - "예" — `0 3 * * * gbrain dream-cycle` 을 crontab에 추가 (Recommended on macOS/Linux)
     - "아니오" — 수동으로 실행

2. **초기 노트 import**
   - header: "노트 Import"
   - question: "기존 노트/문서 폴더가 있으면 GBrain에 import 할까요? (예: `~/notes/`)"
   - options:
     - "지금 import" — 사용자에게 경로를 추가로 물어본 뒤 `gbrain import <경로> --no-embed` + `gbrain embed --stale` 실행
     - "건너뛰기" — 나중에 직접 실행 (Recommended for first run)

선택값을 `INSTALL_CRON`(`yes`/`no`), `IMPORT_NOTES`(`yes`/`no`)로 보관한다. `IMPORT_NOTES == "yes"` 인 경우 **6단계에서 추가 입력을 받는다**.

### 1단계 — 사전 요구사항 점검

```bash
claude --version || echo "MISSING: claude"
bun --version    || echo "MISSING: bun"
```

- `MISSING: claude` 면 Claude Code 설치 안내 후 종료.
- `MISSING: bun` 인 경우:
  ```
  Bun이 설치되어 있지 않습니다. 아래 명령으로 설치 후 다시 실행해 주세요.

    curl -fsSL https://bun.sh/install | bash
    source ~/.bashrc   # 또는 source ~/.zshrc

  Windows의 경우 PowerShell:
    powershell -c "irm bun.sh/install.ps1 | iex"
  ```
  안내 후 종료.

### 2단계 — GBrain 설치 (idempotent)

이미 설치돼 있는지 먼저 확인한다.

```bash
command -v gbrain && gbrain --version
```

- **출력이 정상**이면 이미 설치된 상태로 간주하고 다음 단계로 진행한다 (`Already installed` 로 사용자에게 보고).
- **명령을 찾을 수 없으면** 설치를 진행한다:
  ```bash
  bun add -g github:garrytan/gbrain
  ```
  실패 시 stdout/stderr 그대로 보여주고 종료.

### 3단계 — DB 초기화 (idempotent)

`gbrain doctor --json` 으로 현재 상태를 확인한다.

```bash
gbrain doctor --json
```

- 응답에 DB가 이미 존재하고 정상이면 초기화 단계를 **건너뛴다**.
- DB가 없거나 미초기화 상태면 다음 명령으로 초기화 (PGLite DB, 약 2분 소요):
  ```bash
  gbrain init
  ```
- 초기화 후 다시 `gbrain doctor --json` 으로 검증한다.

진행 상황을 사용자에게 요약해 보고한다 (특히 `gbrain init` 은 시간이 걸리므로).

### 4단계 — Claude Code MCP 등록 (idempotent)

```bash
claude mcp list
```

출력에 `gbrain` 이 포함돼 있는지 확인한다.

- **포함돼 있으면**: `gbrain MCP가 이미 등록되어 있습니다.` 라고 보고하고 건너뛴다.
- **없으면**: 등록 후 재확인.
  ```bash
  claude mcp add gbrain -- gbrain mcp serve
  claude mcp list
  ```

### 5단계 — (선택) Dream Cycle cron 등록

`INSTALL_CRON == "yes"` 인 경우에만 진행한다.

먼저 OS를 확인한다 (`uname` 또는 사용자에게 확인).

- **macOS / Linux**:
  ```bash
  # 기존 crontab을 보존하며 라인 중복을 방지
  ( crontab -l 2>/dev/null | grep -v "gbrain dream-cycle"; \
    echo "0 3 * * * gbrain dream-cycle" ) | crontab -
  crontab -l | grep "gbrain dream-cycle"
  ```
- **Windows**: cron이 없으므로 다음 안내만 출력한다:
  ```
  Windows에는 cron이 없습니다. 작업 스케줄러로 매일 03:00에 다음 명령을 실행하도록 설정해 주세요.

    gbrain dream-cycle

  PowerShell 한 줄 등록 예시:
    schtasks /Create /SC DAILY /TN "GBrain Dream Cycle" /TR "gbrain dream-cycle" /ST 03:00
  ```

### 6단계 — (선택) 초기 노트 import + 임베딩

`IMPORT_NOTES == "yes"` 인 경우에만 진행한다.

`AskUserQuestion` 으로 추가 입력을 받는다.

- header: "Import 경로"
- question: "GBrain에 import 할 노트/문서 폴더 경로를 입력해 주세요. (예: `~/notes`, `D:/Documents/notes`)"
- options:
  - "직접 입력" — 사용자가 경로를 입력
  - "취소" — 6단계를 건너뛰고 7단계로

경로를 받았으면 다음을 실행한다.

```bash
NOTES_PATH="<사용자 입력 경로>"
gbrain import "$NOTES_PATH" --no-embed
gbrain embed --stale
```

각 단계의 결과(문서 수, 임베딩 수 등)를 사용자에게 요약 보고한다.

### 7단계 — (선택) 현재 프로젝트 CLAUDE.md에 GBrain 연동 섹션 추가

현재 cwd에 `CLAUDE.md` 가 있는지 `Read` 로 확인한다.

- **없으면**: 이 단계를 건너뛴다 (GBrain은 글로벌이므로 CLAUDE.md가 없는 디렉터리에서도 정상 작동).
- **있으면**: 파일에 `## GBrain 연동` 섹션이 이미 있는지 확인.
  - 이미 있으면 건너뜀.
  - 없으면 `Edit` 도구로 파일 끝(또는 적절한 위치)에 다음 섹션을 추가한다:
    ```markdown

    ## GBrain 연동

    이 프로젝트는 GBrain(MCP 서버 `gbrain`)에 연결되어 있다.

    - `gbrain import <경로>` — 노트/문서 가져오기
    - `gbrain embed --stale` — 임베딩 동기화
    - `gbrain query "<질문>"` — 의미 기반 검색
    - 야간 정기 작업: `0 3 * * * gbrain dream-cycle`
    ```
  - 변경 전 원본을 `CLAUDE.md.before-gbrain` 으로 백업한다.

### 8단계 — 결과 보고

설치를 마치면 다음 형식으로 사용자에게 요약을 출력한다.

```
GBrain 설치를 완료했습니다.

- gbrain 바이너리: {경로 또는 "이미 설치됨"}
- DB 초기화: {완료 / 이미 초기화됨}
- Claude Code MCP 등록: {신규 / 이미 등록됨}
- Dream Cycle cron: {등록 / 건너뜀 / Windows 수동 안내}
- 노트 Import: {N개 import, M개 embed / 건너뜀}
- CLAUDE.md GBrain 섹션: {추가 / 이미 있음 / CLAUDE.md 없음}

사용 예시
  gbrain query "지난주에 정리한 RAG 문서 어디 있더라"
  gbrain import ~/Documents/new-notes
  gbrain dream-cycle      # 수동 실행

Claude Code 새 세션에서 /mcp 입력 시 `gbrain: connected` 가 보이면 정상입니다.
```

## 예시

### Input

```
/install-gbrain
```

### Output (대화 흐름 요약)

```
Dream Cycle cron 등록? > 예
초기 노트 import? > 건너뛰기

[사전 요구사항 점검 중...]
  claude --version → 1.x.x ✓
  bun --version    → 1.0.x ✓

[GBrain 설치 확인 중...]
  command -v gbrain → not found
  bun add -g github:garrytan/gbrain → 설치 완료

[DB 초기화 중... (약 2분)]
  gbrain init → ✓
  gbrain doctor --json → status: healthy

[MCP 등록 중...]
  claude mcp list | grep gbrain → not found
  claude mcp add gbrain -- gbrain mcp serve → ✓

[Dream Cycle cron 등록 중...]
  crontab → "0 3 * * * gbrain dream-cycle" 추가 ✓

[CLAUDE.md 검사 중...]
  현재 cwd에 CLAUDE.md 없음 → 스킵

GBrain 설치를 완료했습니다.

- gbrain 바이너리: ~/.bun/bin/gbrain
- DB 초기화: 완료
- Claude Code MCP 등록: 신규
- Dream Cycle cron: 등록 (매일 03:00)
- 노트 Import: 건너뜀
- CLAUDE.md GBrain 섹션: CLAUDE.md 없음 (스킵)

Claude Code 새 세션에서 /mcp 입력 시 `gbrain: connected` 가 보이면 정상입니다.
```
