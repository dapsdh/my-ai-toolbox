# create-my-skill

Claude Code 스킬(SKILL.md)을 대화형으로 생성하고 품질 검증까지 수행하는 스킬입니다.

## 설치

스킬 폴더를 원하는 위치에 복사합니다:

```bash
# 특정 프로젝트에서만 사용
cp -r .claude/skills/create-my-skill <대상-프로젝트>/.claude/skills/create-my-skill

# 모든 프로젝트에서 사용 (글로벌)
cp -r .claude/skills/create-my-skill ~/.claude/skills/create-my-skill
```

## 환경 변수

이 스킬은 별도 환경 변수가 필요하지 않습니다.

## 사용법

```
/create-my-skill
```

스킬 이름과 사용 예시를 순서대로 입력하면 SKILL.md와 README.md가 자동 생성됩니다.
