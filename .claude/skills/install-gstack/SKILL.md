---
name: install-gstack
description: >
  Garry Tan의 gstack(Claude Code 스킬 모음)을 머신·사용자 단위 글로벌 1회 설치하는 스킬.
  `~/.claude/skills/gstack`에 클론·setup 하면 내부 스킬들이 `~/.claude/skills/<skill-name>/`로
  심링크되어 /office-hours, /autoplan, /review, /qa, /ship 등 슬래시 커맨드가
  모든 프로젝트에서 사용 가능해진다. idempotent — 이미 설치돼 있으면 자동으로 건너뛴다.
  프로젝트별 설정은 다루지 않으며, CLAUDE.md도 수정하지 않는다.
  사용자가 "install-gstack", "gstack 설치", "gstack 깔아줘", "/install-gstack" 등을 입력하면 트리거한다.
allowed-tools:
  - Bash
---

# install-gstack

Garry Tan의 [gstack](https://github.com/garrytan/gstack)을 글로벌(`~/.claude/skills/gstack`)에 1회 설치한다. 한 번만 깔아두면 모든 프로젝트에서 같은 슬래시 커맨드를 공유한다.

이 스킬은 **글로벌 설치만** 다룬다. 프로젝트별 부트스트랩(`./setup --team`)이나 `CLAUDE.md` 갱신은 하지 않는다.

## 사전 준비

별도 환경 변수는 필요 없다. 다음 도구가 PATH에 있어야 한다.

- **Claude Code CLI** (`claude --version`)
- **Bun 1.0+** (`bun --version`) — gstack 런타임
- **Git** (`git --version`)

## 워크플로우

### 1단계 — 사전 요구사항 점검

`Bash` 도구로 다음을 한 번에 실행한다.

```bash
claude --version || echo "MISSING: claude"
bun --version    || echo "MISSING: bun"
git --version    || echo "MISSING: git"
```

- `MISSING: claude` 가 나오면 Claude Code 설치를 안내하고 종료.
- `MISSING: bun` 인 경우 다음을 안내하고 종료:
  ```
  Bun이 설치되어 있지 않습니다. 아래 명령으로 설치 후 다시 실행해 주세요.

    curl -fsSL https://bun.sh/install | bash
    source ~/.bashrc   # 또는 source ~/.zshrc

  Windows의 경우 PowerShell:
    powershell -c "irm bun.sh/install.ps1 | iex"
  ```
- `MISSING: git` 이면 Git 설치를 요청하고 종료.

### 2단계 — 기존 설치 감지 (idempotent)

```bash
if [ -d ~/.claude/skills/gstack ] && [ -d ~/.claude/skills/gstack/.git ]; then
  echo "ALREADY_INSTALLED"
  ls ~/.claude/skills/ | head -30
fi
```

- `ALREADY_INSTALLED` 가 출력되면 사용자에게 다음과 같이 보고하고 **3단계를 건너뛴다**:
  ```
  gstack은 이미 글로벌(`~/.claude/skills/gstack`)에 설치되어 있습니다.

  - 슬래시 커맨드는 모든 프로젝트에서 사용 가능합니다 (예: /office-hours, /autoplan, /review)
  - 업데이트하려면: /gstack-upgrade
  - 완전히 재설치하려면: rm -rf ~/.claude/skills/gstack 후 /install-gstack 다시 실행
  ```
  이후 4단계(결과 보고)로 바로 진행한다.
- 출력이 없으면 설치되지 않은 상태이므로 3단계로 진행한다.

### 3단계 — 글로벌 클론 + setup

대상 경로: `~/.claude/skills/gstack` (gstack 공식 권장 경로).

```bash
mkdir -p ~/.claude/skills
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && (cd ~/.claude/skills/gstack && ./setup)
```

- `git clone` 또는 `./setup` 이 실패하면 stdout/stderr 전체를 사용자에게 그대로 보여주고 종료한다.
- 성공 후 `ls ~/.claude/skills/` 로 새로 등록된 슬래시 커맨드 디렉터리(`office-hours`, `autoplan`, `review`, `qa`, `ship` …)를 확인하고 사용자에게 보고한다.

### 4단계 — 결과 보고

다음 형식으로 사용자에게 요약을 출력한다.

```
gstack 설치 상태: {신규 설치 / 이미 설치됨}

- 위치: ~/.claude/skills/gstack
- 등록된 슬래시 커맨드(예시): /office-hours, /autoplan, /review, /qa, /ship, /retro …

다음 단계
  1. 새 Claude Code 세션을 시작하면 슬래시 커맨드가 인식됩니다.
  2. 어떤 프로젝트에서든 /office-hours 로 첫 상담을 시작해 보세요.
  3. (선택) GBrain(개인 두뇌, MCP)도 쓰려면 `/install-gbrain` 한 번 실행.
  4. 업데이트는 `/gstack-upgrade`, 재설치는 `rm -rf ~/.claude/skills/gstack` 후 `/install-gstack`.
```

## 예시

### Input

```
/install-gstack
```

### Output (신규 설치 — 대화 흐름 요약)

```
[사전 요구사항 점검 중...]
  claude --version → 1.x.x ✓
  bun --version    → 1.0.x ✓
  git --version    → 2.x.x ✓

[기존 설치 감지 중...]
  ~/.claude/skills/gstack → 없음

[글로벌 클론 중... ~/.claude/skills/gstack]
[./setup 실행 중...]
  ✓ 23개 슬래시 커맨드가 ~/.claude/skills/ 에 심링크 등록되었습니다.

gstack 설치 상태: 신규 설치

- 위치: ~/.claude/skills/gstack
- 등록된 슬래시 커맨드(예시): /office-hours, /autoplan, /review, /qa, /ship, /retro …

다음 단계
  1. 새 Claude Code 세션을 시작하면 슬래시 커맨드가 인식됩니다.
  2. 어떤 프로젝트에서든 /office-hours 로 첫 상담을 시작해 보세요.
```

### Output (이미 설치됨 — idempotent skip)

```
[사전 요구사항 점검 중...]  ✓
[기존 설치 감지 중...]       ALREADY_INSTALLED

gstack은 이미 글로벌(`~/.claude/skills/gstack`)에 설치되어 있습니다.

- 슬래시 커맨드는 모든 프로젝트에서 사용 가능합니다 (예: /office-hours, /autoplan, /review)
- 업데이트하려면: /gstack-upgrade
- 완전히 재설치하려면: rm -rf ~/.claude/skills/gstack 후 /install-gstack 다시 실행
```
