---
name: git-commit
description: Analyzes staged changes and automatically generates a commit message and commits. Use when the user wants to commit staged changes with an auto-generated message ("/git-commit", "커밋해줘", "커밋 메시지 만들어서 커밋해줘").
argument-hint: "optional issue branch name (e.g. \"my-feature\" → branch \"issue/my-feature\")"
allowed-tools: Bash, AskUserQuestion
---

# 자동 커밋 메시지 생성 및 커밋

사용자 입력: $ARGUMENTS

## 인수 파싱

- `$ARGUMENTS`가 비어 있으면 → `issue-branch` 없음
- `$ARGUMENTS`가 있으면 → `issue-branch = $ARGUMENTS` 전체

예시:
- `/git-commit` → 브랜치 미지정
- `/git-commit my-feature` → issue-branch=my-feature

## 워크플로

### 0. Git 저장소 확인

```bash
git rev-parse --is-inside-work-tree
```

- 실패(exit code 비정상)하면 아래 메시지를 출력하고 **즉시 종료**한다.

  ```
  /git-commit은 Git 저장소 안에서만 사용할 수 있습니다.
  Git 프로젝트 폴더로 이동한 후 다시 실행하세요.
  ```

### 1. 브랜치 결정

#### `issue-branch`가 있는 경우

브랜치 이름을 `issue/<issue-branch>`로 설정한다. 사용자에게 아래 메시지를 출력한다.

```
대상 브랜치: issue/<issue-branch>
```

#### `issue-branch`가 없는 경우

현재 브랜치를 확인한다.

```bash
git rev-parse --abbrev-ref HEAD
```

AskUserQuestion 도구로 아래와 같이 질문한다.

- question: `커밋할 브랜치를 선택하세요 (새 브랜치: 이름 직접 입력 → issue/<입력값> 생성)`
- options:
  1. label: `현재 브랜치 (<현재 브랜치명>)` — description: `<현재 브랜치명> 브랜치에 커밋합니다`
  2. label: `main` — description: `main 브랜치로 체크아웃 후 커밋합니다`

응답에 따라:
- `현재 브랜치` 선택 → 현재 브랜치를 그대로 사용한다.
- `main` 선택 → main 브랜치를 대상으로 설정한다.
- Other로 텍스트 입력 → `issue/<입력값>`으로 브랜치 이름을 설정한다.
  - 브랜치 존재 여부를 확인한다.
    ```bash
    git show-ref --verify --quiet refs/heads/issue/<입력값>
    ```
    - **이미 존재하면**: `브랜치 'issue/<입력값>'은 이미 존재합니다.` 메시지를 출력하고 **즉시 종료**한다.
    - **존재하지 않으면**: 새로 생성 후 체크아웃한다.
      ```bash
      git checkout -b issue/<입력값>
      ```
      사용자에게 아래 메시지를 출력한다.
      ```
      대상 브랜치: issue/<입력값>
      ```

### 2. 대상 브랜치 체크아웃 (없으면 생성)

> 이 단계는 `$ARGUMENTS`로 브랜치가 지정된 경우에만 적용된다. New Branch 경로는 1단계에서 이미 처리되었으므로 건너뛴다.

현재 브랜치와 대상 브랜치가 같으면 이 단계를 건너뛴다.

```bash
git show-ref --verify --quiet refs/heads/<브랜치명>
```

- 브랜치가 **존재**하면:
  ```bash
  git checkout <브랜치명>
  ```

- 브랜치가 **존재하지 않으면** 새로 생성 후 체크아웃:
  ```bash
  git checkout -b <브랜치명>
  ```
  사용자에게 `브랜치 '<브랜치명>'을 새로 생성했습니다.` 메시지를 출력한다.

### 3. 변경사항 스테이징 및 확인

변경된 파일을 모두 스테이징한다.

```bash
git add -A
```

스테이징 상태를 확인한다.

```bash
git status
git diff --cached
```

- 스테이징된 변경사항이 없으면 "커밋할 변경사항이 없습니다." 안내 후 종료.

### 4. 커밋 메시지 생성

`git diff --cached` 출력을 분석해 아래 규칙에 따라 커밋 메시지를 작성한다.

#### 메시지 규칙

- **형식**: `[scope] 변경 내용 요약`
  - `scope`: 변경된 주요 디렉토리·모듈·기능명 (예: `skills`, `jira-filter-summarizer`, `auth`)
  - 변경 범위가 넓으면 scope 생략 가능
- **언어**: 변경된 파일·코드가 한국어 주석/문서 중심이면 한국어, 그 외에는 영어
- **길이**: 제목 1줄 (72자 이내), 필요 시 본문 추가
- **동사 선택**:
  - 새 파일·기능 추가 → `add`
  - 기존 기능 수정·개선 → `update`
  - 버그 수정 → `fix`
  - 삭제 → `remove`
  - 리팩터링 → `refactor`
  - 문서 → `docs`
#### 최근 커밋 스타일 참고

```bash
git log --oneline -5
```

저장소의 기존 커밋 메시지 스타일(언어, 형식, prefix 등)을 참고해 일관성을 유지한다.

### 5. 커밋 실행

생성한 메시지로 커밋한다.

```bash
git commit -m "<생성된 커밋 메시지>"
```

### 6. 결과 출력

커밋 성공 시 아래 형식으로 출력한다.

```
✓ <브랜치명> 브랜치에 커밋 완료: <커밋 해시> <커밋 메시지>
```
