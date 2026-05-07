# install-gbrain

Garry Tan의 [GBrain](https://github.com/garrytan/gbrain)을 **글로벌 1회** 설치하고 Claude Code MCP에 등록하는 스킬. GBrain은 사용자 단위의 개인 두뇌(Postgres + pgvector / PGLite)이며, 모든 프로젝트에서 같은 두뇌를 공유한다. 재실행 시 이미 설치·등록된 부분은 자동으로 건너뛴다(idempotent).

## 설치

스킬 폴더를 원하는 위치에 복사합니다:

```bash
# 특정 프로젝트에서만 사용
cp -r .claude/skills/install-gbrain <대상-프로젝트>/.claude/skills/install-gbrain

# 모든 프로젝트에서 사용 (글로벌)
cp -r .claude/skills/install-gbrain ~/.claude/skills/install-gbrain
```

## 사전 요구사항

이 스킬은 별도 환경 변수가 필요하지 않습니다. 단, 다음 도구가 PATH에 있어야 합니다.

| 도구 | 필수 | 설명 |
|------|------|------|
| Claude Code CLI | Y | `claude --version` 으로 확인 |
| Bun 1.0+ | Y | gbrain 런타임. `curl -fsSL https://bun.sh/install \| bash` |

## 사용법

```
/install-gbrain
```

스킬 실행 시 다음을 묻습니다.

1. **Dream Cycle cron 등록** — 매일 03:00에 `gbrain dream-cycle` 자동 실행 여부 (예/아니오)
2. **초기 노트 import** — 기존 노트/문서 폴더를 GBrain에 가져올지 (예 → 경로 입력 / 건너뛰기)

내부 동작은 **idempotent** 합니다.

- `command -v gbrain` 로 기존 설치를 감지 → 있으면 설치 단계 스킵
- `gbrain doctor --json` 으로 DB 상태 확인 → 정상이면 `gbrain init` 스킵
- `claude mcp list | grep gbrain` 으로 MCP 등록 확인 → 있으면 등록 스킵

현재 cwd에 `CLAUDE.md` 가 있으면 `## GBrain 연동` 섹션을 자동으로 추가합니다 (기존 파일은 `CLAUDE.md.before-gbrain` 으로 백업).

## 참고 링크

- GBrain GitHub: https://github.com/garrytan/gbrain
- gstack(자매 프로젝트): https://github.com/garrytan/gstack
- Garry Tan 공식: https://gstacks.org
