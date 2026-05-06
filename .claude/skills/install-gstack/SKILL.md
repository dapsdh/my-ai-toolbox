---
name: install-gstack
description: >
  Garry Tan의 gstack(Claude Code 스킬 모음)을 현재 프로젝트에 설치하는 스킬.
  Claude Code/Bun/Git 사전 요구사항을 점검하고, gstack 저장소를 클론·setup 한 뒤,
  프로젝트의 CLAUDE.md를 gstack 워크플로우 기준으로 갱신한다.
  사용자가 "install-gstack", "gstack 설치", "gstack 환경 만들어줘",
  "이 프로젝트에 gstack 깔아줘", "/install-gstack" 등을 입력하면 트리거한다.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# install-gstack

Garry Tan의 [gstack](https://github.com/garrytan/gstack)을 현재 작업 중인 프로젝트에 설치하고, gstack 워크플로우(Think → Plan → Build → Review → Test → Ship → Reflect)에 맞춘 CLAUDE.md를 구성한다. 선택적으로 GBrain까지 함께 설치한다.

## 사전 준비

이 스킬은 외부 환경 변수를 요구하지 않는다. 다음 도구가 필요하다:

- **Claude Code CLI** (`claude --version`)
- **Bun 1.0+** (`bun --version`) — gstack/GBrain의 런타임
- **Git** (`git --version`)

## 워크플로우

### 0단계 — 설치 옵션 확인

`AskUserQuestion` 도구로 한 가지만 묻는다. 설치 범위는 **항상 프로젝트 전용**(`<프로젝트 루트>/.claude/skills/gstack`)으로 고정이며 묻지 않는다.

1. **GBrain 동시 설치 여부**
   - header: "GBrain"
   - question: "GBrain(개인 두뇌, MCP 연동)도 함께 설치할까요?"
   - options:
     - "예" — `bun add -g github:garrytan/gbrain` 후 `gbrain init`, Claude Code MCP 등록까지 진행
     - "아니오" — gstack만 설치 (Recommended)

선택값을 변수 `INSTALL_GBRAIN`(`yes`/`no`)으로 보관한다.

### 1단계 — 사전 요구사항 점검

`Bash` 도구로 다음 명령을 순서대로 실행한다.

```bash
claude --version || echo "MISSING: claude"
bun --version    || echo "MISSING: bun"
git --version    || echo "MISSING: git"
```

- `MISSING: claude` 가 출력되면 Claude Code 설치를 안내하고 스킬을 종료한다.
- `MISSING: bun` 인 경우 사용자에게 다음 안내 후 종료한다:
  ```
  Bun이 설치되어 있지 않습니다. 아래 명령으로 설치 후 다시 실행해 주세요.

    curl -fsSL https://bun.sh/install | bash
    source ~/.bashrc   # 또는 source ~/.zshrc

  Windows의 경우 PowerShell:
    powershell -c "irm bun.sh/install.ps1 | iex"
  ```
- `MISSING: git` 이면 Git 설치를 요청하고 종료한다.

### 2단계 — gstack 클론 및 setup

대상 디렉터리는 항상 `<프로젝트 루트>/.claude/skills/gstack` 으로 고정한다.

이미 디렉터리가 존재하면 사용자에게 다음 중 하나를 선택하게 한다.

- header: "기존 설치"
- question: "{대상 경로}에 이미 gstack이 있습니다. 어떻게 할까요?"
- options:
  - "건너뛰기" — 클론 단계만 생략하고 다음 단계로 (Recommended)
  - "재설치" — 기존 폴더를 백업(`gstack.bak.<timestamp>`)한 뒤 새로 클론
  - "취소" — 스킬 종료

클론·setup은 다음 명령으로 수행한다:

```bash
TARGET=".claude/skills/gstack"
mkdir -p "$(dirname "$TARGET")"
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$TARGET"
cd "$TARGET" && ./setup
```

- `./setup`이 실패하면 출력 로그를 그대로 사용자에게 보여주고 스킬을 종료한다.
- 성공하면 사용자에게 `gstack 슬래시 커맨드(/office-hours, /autoplan, /review, /qa, /ship 등)가 활성화되었습니다.` 를 알린다.

### 3단계 — (선택) GBrain 설치 및 MCP 등록

`INSTALL_GBRAIN == "yes"` 인 경우에만 진행한다.

```bash
# 1) GBrain 글로벌 설치
bun add -g github:garrytan/gbrain

# 2) PGLite DB 초기화 (약 2분)
gbrain init

# 3) 설치 진단
gbrain doctor --json

# 4) Claude Code MCP에 등록
claude mcp add gbrain -- gbrain mcp serve

# 5) MCP 연결 확인
claude mcp list
```

각 단계의 stdout/stderr 를 사용자에게 요약해 보여준다. 실패하면 어떤 단계에서 멈췄는지 명시한다.

### 4단계 — CLAUDE.md 작성·갱신

`<프로젝트 루트>/CLAUDE.md` 파일이 존재하는지 `Read` 도구로 확인한다.

#### 4-A. 기존 CLAUDE.md가 있는 경우

1. 기존 CLAUDE.md 전체를 읽는다.
2. **기존 내용을 6~12줄 정도의 불릿 요약**으로 압축한다. 다음을 반드시 포함한다:
   - 프로젝트의 목적/도메인
   - 사용 언어·프레임워크
   - 핵심 디렉터리 구조
   - 빌드/테스트/실행 명령
   - 코딩 컨벤션·커밋 규칙
   - 기타 특수 지시사항(언어 설정 등)
3. **gstack 운영 가이드**를 본문 상단에 두고, 기존 요약은 `## 기존 프로젝트 컨텍스트(요약)` 섹션으로 **뒤에 붙인다**.
4. 원본 CLAUDE.md는 `CLAUDE.md.before-gstack` 으로 백업한다 (덮어쓰기 방지).

#### 4-B. CLAUDE.md가 없는 경우

gstack 운영 가이드만 새로 생성한다 (백업·요약 단계 생략).

#### CLAUDE.md 템플릿

`Write` 도구로 다음 내용을 작성한다. `{...}` 자리표시자는 실제 값으로 치환한다.

```markdown
# CLAUDE.md

이 프로젝트는 [gstack](https://github.com/garrytan/gstack) 워크플로우를 기반으로 운영된다.

## 운영 원칙

- **Source of Truth는 코드와 문서**다. 자연어 요청은 항상 Plan → Build → Review → Test → Ship → Reflect 흐름으로 변환해 처리한다.
- 모든 답변은 **한국어**로 작성한다. (필요 시 사용자가 영어로 요청하면 그에 따른다)
- 위험·비가역 작업(파일 삭제, force push, 배포 등)은 사용자 명시 승인 없이 실행하지 않는다.

## gstack 워크플로우

| 단계 | 슬래시 커맨드 | 목적 |
|------|---------------|------|
| Think | `/office-hours` | CEO 모드 1:1 상담, 방향 정하기 |
| Plan | `/autoplan` | 작업 자동 분해 |
| Plan Review | `/plan-ceo-review`, `/plan-eng-review` | 비즈니스/엔지니어링 관점 리뷰 |
| Design | `/design-consultation` | UI/UX 설계 상담 |
| Review | `/review` | Chromium 기반 UI 리뷰 |
| QA | `/qa` | OWASP + STRIDE 보안·품질 점검 |
| Ship | `/cso`, `/ship` | 통합 점검 후 배포 + PR |
| Reflect | `/retro`, `/learn` | 회고 및 학습 루프 |
| 안전장치 | `/careful`, `/freeze`, `/guard` | 위험 작업 방지 |
| 브라우저 | `/open-gstack-browser` | gstack 전용 Chromium 실행 |
| 업그레이드 | `/gstack-upgrade` | gstack 자체 업데이트 |

> 상세 사용법은 `{GSTACK_PATH}/README.md` 또는 `https://github.com/garrytan/gstack` 참조.

{GBRAIN_SECTION_IF_INSTALLED}

## 일반 작업 가이드

- 작업 시작 전: `/office-hours` 또는 `/autoplan` 으로 계획 수립.
- 코드 변경 후: `/review` → `/qa` → `/ship` 순으로 점검.
- 정기 회고: `/retro` 와 `/learn` 으로 학습 결과를 누적.

## 기존 프로젝트 컨텍스트(요약)

{기존 CLAUDE.md 요약 — 4-A 단계에서 만든 6~12줄 불릿. 4-B(신규 생성)인 경우 이 섹션은 생략한다.}
```

`{GBRAIN_SECTION_IF_INSTALLED}` 는 GBrain을 설치한 경우에만 다음으로 치환하고, 아니면 빈 문자열로 둔다:

```markdown
## GBrain 연동

이 프로젝트는 GBrain(MCP 서버 `gbrain`)에 연결되어 있다.

- `gbrain import <경로>` — 노트/문서 가져오기
- `gbrain embed --stale` — 임베딩 동기화
- `gbrain query "<질문>"` — 의미 기반 검색
- 야간 정기 작업: `0 3 * * * gbrain dream-cycle`
```

### 5단계 — 결과 보고

설치를 마치면 다음 형식으로 사용자에게 요약을 출력한다.

```
gstack 설치를 완료했습니다.

- 설치 위치: {대상 경로}
- GBrain 설치: {예/아니오}
- CLAUDE.md: {생성/업데이트, 백업 경로 명시}

다음 단계
  1. 새 Claude Code 세션을 시작해 슬래시 커맨드를 인식시킵니다.
  2. /office-hours 로 첫 상담을 진행해 보세요.
  3. 문제가 생기면 `gbrain doctor --json` 또는 `{GSTACK_PATH}/README.md` 를 확인하세요.
```

## 예시

### Input

```
/install-gstack
```

### Output (대화 흐름 요약)

```
GBrain도 설치할까요? > 아니오

[사전 요구사항 점검 중...]
  claude --version → 1.x.x ✓
  bun --version    → 1.0.x ✓
  git --version    → 2.x.x ✓

[gstack 클론 중... .claude/skills/gstack]
[./setup 실행 중...]
  ✓ 23개 슬래시 커맨드가 등록되었습니다.

[CLAUDE.md 갱신 중...]
  - 기존 CLAUDE.md → CLAUDE.md.before-gstack 으로 백업
  - 새 CLAUDE.md 작성 (gstack 가이드 + 기존 요약 7줄)

gstack 설치를 완료했습니다.

- 설치 위치: D:/Projects/myapp/.claude/skills/gstack
- GBrain 설치: 아니오
- CLAUDE.md: 업데이트 (백업: CLAUDE.md.before-gstack)

다음 단계
  1. 새 Claude Code 세션을 시작해 슬래시 커맨드를 인식시킵니다.
  2. /office-hours 로 첫 상담을 진행해 보세요.
```
