---
name: create-my-skill
description: >
  Claude 스킬(SKILL.md)을 대화형으로 생성하고 검증하는 스킬.
  사용자가 "create-my-skill", "스킬 만들어줘", "새 스킬 생성",
  "SKILL.md 만들어줘" 등을 입력하면 트리거한다.
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
---

# create-my-skill

사용자와 대화하며 Claude Code 스킬(SKILL.md)을 생성하고, 품질 검증까지 수행한다.

## 워크플로우

### 1단계 — 정보 수집

AskUserQuestion 도구를 사용하여 다음 두 가지를 **순서대로** 묻는다.

1. **스킬 이름** — kebab-case 권장 (예: `jira-helper`, `pdf-summarizer`)
   - 입력값을 소문자 kebab-case로 정규화한다 (공백/언더스코어 → 하이픈)
2. **스킬 사용 예시** — 이 스킬을 어떤 상황에서 어떻게 쓸지 자유롭게 입력받는다
   - 예: "Jira 이슈를 자연어로 만들어줘", "PDF 요약해줘"

두 정보를 모두 수집한 뒤, `{프로젝트 루트}/.claude/skills/{skill_name}/SKILL.md` 경로에 이미 파일이 존재하는지 확인한다.

- **파일이 존재하면**: 사용자에게 `"이미 같은 이름의 스킬이 존재합니다: .claude/skills/{skill_name}/SKILL.md"` 메시지를 출력하고 스킬을 종료한다.
- **파일이 없으면**: 2단계로 진행한다.

### 2단계 — SKILL.md 작성

수집한 스킬 이름과 사용 예시를 바탕으로 SKILL.md를 작성한다.

#### 작성 규칙

1. YAML frontmatter에 `name`, `description`, `argument-hint`, `allowed-tools`를 포함한다.
2. `description`은 스킬 트리거 조건을 구체적으로 기술한다. 사용자가 입력할 법한 문구와 맥락을 포함하여 Claude가 스킬을 과소 트리거하지 않도록 한다.
3. `argument-hint`는 커맨드 입력 시 표시되는 인자 힌트다. 스킬이 인자를 받는 경우 `"<인자 설명>"` 형식으로 작성한다. 인자가 없으면 생략한다.
4. `allowed-tools`는 스킬이 사용하는 도구 목록이다. 워크플로우에서 실제로 사용하는 도구만 나열한다. (예: Read, Write, Edit, Bash, WebFetch, WebSearch, Grep, Glob, AskUserQuestion, Agent 등)
5. 본문 구조: 스킬 설명, 워크플로우(단계별 지시사항), 예시(Input/Output)를 반드시 포함한다.
6. 500줄을 넘지 않는다.
7. 수정 사항이 있는 경우(3단계에서 FAIL 후 재작성), 해당 피드백을 반영하여 개선한다.

#### SKILL.md 템플릿

```markdown
---
name: <스킬-이름>
argument-hint: "<인자 설명>"
description: >
  언제 이 스킬을 사용해야 하는지 구체적으로 기술한다.
  사용자가 입력할 법한 문구와 맥락을 포함한다.
allowed-tools:
  - <사용하는 도구 1>
  - <사용하는 도구 2>
---

# <스킬 이름>

스킬이 하는 일을 간결하게 설명한다.

## 워크플로우
(단계별 지시사항)

## 예시
(Input / Output 형식)
```

#### 파일 저장

Write 도구를 사용하여 다음 두 파일을 저장한다.

**1) SKILL.md** — `{프로젝트 루트}/.claude/skills/{skill_name}/SKILL.md`

**2) README.md** — `{프로젝트 루트}/.claude/skills/{skill_name}/README.md` (아래 내용 포함)

```markdown
# <스킬 이름>

<스킬이 하는 일 1-2문장 설명>

## 설치

스킬 폴더를 원하는 위치에 복사합니다:

# 특정 프로젝트에서만 사용
cp -r .claude/skills/<스킬-이름> <대상-프로젝트>/.claude/skills/<스킬-이름>

# 모든 프로젝트에서 사용 (글로벌)
cp -r .claude/skills/<스킬-이름> ~/.claude/skills/<스킬-이름>

## 환경 변수

환경 변수는 스킬 폴더의 `.env` 파일에서 먼저 찾고, 없는 경우 `~/.claude/.env`에서 찾습니다.

(스킬이 사용하는 환경 변수를 표로 정리한다. 없으면 "이 스킬은 별도 환경 변수가 필요하지 않습니다."로 표시)

| 변수명 | 필수 | 설명 |
|--------|------|------|
| 예: API_TOKEN | Y | API 인증 토큰 |

## 사용법

/<스킬-이름> <인자가 있으면 표시>
```

### 3단계 — 품질 검증

저장된 SKILL.md를 Read 도구로 읽고, 아래 5가지 기준으로 검증한다.

| # | 항목 | 확인 내용 |
|---|------|-----------|
| 1 | **트리거 명확성** | description이 언제 이 스킬을 써야 하는지 충분히 설명하는가 |
| 2 | **예시 포함** | 사용자가 입력할 법한 실제 문구가 description에 있는가 |
| 3 | **구조 완결성** | YAML frontmatter(`name`, `description`), 본문, 워크플로우, 예시가 모두 갖춰져 있는가 |
| 4 | **지시 명확성** | Claude가 스킬을 읽고 무엇을 해야 할지 명확히 알 수 있는가 |
| 5 | **500줄 이하** | 스킬 본문이 500줄을 넘지 않는가 |

검증 결과를 아래 형식으로 정리한다:

```
## 검증 결과

| 항목 | 통과 여부 | 비고 |
|------|-----------|------|
| 트리거 명확성 | PASS/FAIL | ... |
| 예시 포함 | PASS/FAIL | ... |
| 구조 완결성 | PASS/FAIL | ... |
| 지시 명확성 | PASS/FAIL | ... |
| 500줄 이하 | PASS/FAIL | ... |

**최종 판정:** PASS 또는 FAIL
```

- 5가지 항목이 모두 PASS이면 `**최종 판정:** PASS`
- 하나라도 FAIL이면 `**최종 판정:** FAIL`과 함께 구체적인 수정 사항을 항목별로 나열한다

**미통과 처리:**

FAIL인 경우:
1. 수정 사항을 반영하여 SKILL.md를 다시 작성한다 (2단계로 돌아감).
2. 재작성된 SKILL.md를 다시 검증한다.
3. 최대 3회까지 반복한다. 3회 후에도 미통과 시 현재 상태로 저장하고 사용자에게 알린다.

### 4단계 — 저장 및 완료

검증을 통과한 SKILL.md는 이미 `.claude/skills/<스킬-이름>/SKILL.md`에 저장되어 있다.

완료 후 사용자에게 다음을 안내한다:

1. **저장된 파일 경로** — `.claude/skills/<스킬-이름>/SKILL.md`
2. **SKILL.md 상단 20줄 미리보기** — Read 도구로 파일을 읽어 상단 20줄을 표시한다
3. **사용 방법** — 아래 안내를 표시한다:

```
이 스킬을 사용하려면 스킬 폴더를 원하는 위치에 복사하세요:

# 특정 프로젝트에서만 사용
cp -r .claude/skills/<스킬-이름> <대상-프로젝트>/.claude/skills/<스킬-이름>

# 모든 프로젝트에서 사용 (글로벌)
cp -r .claude/skills/<스킬-이름> ~/.claude/skills/<스킬-이름>

복사 후 /<스킬-이름> 으로 사용할 수 있습니다.
```

## 예시

**Input:**
```
create-my-skill
```

**Output (대화 흐름):**
```
스킬 이름을 입력해 주세요 (kebab-case 권장):
> pdf-summarizer

이 스킬을 어떤 상황에서 어떻게 사용하나요?
> PDF 파일을 요약해줘, PDF 링크 넣으면 핵심만 뽑아줘

[SKILL.md 작성 중...]
[품질 검증 중...]

✓ 검증 통과

.claude/skills/pdf-summarizer/SKILL.md가 생성되었습니다.

이 스킬을 사용하려면 스킬 폴더를 원하는 위치에 복사하세요:
  프로젝트 전용: cp -r .claude/skills/pdf-summarizer <대상-프로젝트>/.claude/skills/pdf-summarizer
  글로벌:       cp -r .claude/skills/pdf-summarizer ~/.claude/skills/pdf-summarizer
복사 후 /pdf-summarizer 로 사용할 수 있습니다.
```
