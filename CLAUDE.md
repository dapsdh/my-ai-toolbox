# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **언어 설정:** 모든 설명과 답변은 **한국어**로 작성한다.

## Project Overview

`my-ai-toolbox` is a collection of Claude Code skills for integrating with Atlassian (Jira/Confluence), GitLab, and Google services. Skills are slash commands invoked within Claude Code sessions.

## Environment Setup

Credentials live in `shared/.env` (symlinked into each platform directory). Copy `shared/.env.example` to `shared/.env` and fill in:

- `ATLASSIAN_BASE_URL`, `ATLASSIAN_USER`, `ATLASSIAN_API_TOKEN` — for Jira/Confluence skills
- `GITLAB_PRIVATE_TOKEN` (or `GITLAB_ACCESS_TOKEN`), optionally `GITLAB_HOST` — for GitLab MR review
- `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`/`GOOGLE_REFRESH_TOKEN` — for Google Forms
- `COMMIT_AUTHOR_NAMES` (optional, comma-separated) — GitLab bot display names to classify as code commits in jira-filter-summarizer

For Google Forms, install the required Python packages:
```bash
pip install google-api-python-client google-auth
```

## Skill Structure

Skills are defined under each platform directory (`.claude/skills/`, `.cursor/skills/`). Each `SKILL.md` specifies the trigger phrase, step-by-step workflow, and output format for Claude to follow. Python scripts live in `shared/scripts/<skill-name>/` and are symlinked into each platform's `skills/<skill-name>/scripts/`.

### Available Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/git-commit` | `/git-commit [issue-branch]` | Auto-generates and commits staged changes |
| `/jira-filter-summarizer` | `<filter URL> 요약해줘` | Summarizes all issues in a Jira filter |
| `/wiki-page-summarizer` | `<page URL> 요약해줘` | Summarizes a Jira issue or Confluence page; add `하위 페이지까지` to recurse into child pages |
| `/jira-issue-debug` | `<issue URL> 문제코드를 찾아줘` | Finds problem code in the codebase for a Jira bug |
| `/git-mr-review` | `<MR URL> 코드 리뷰 해줘` | Structured code review for a GitLab MR |
| `/google-forms-viewer` | `<form URL> 접속해줘` | Displays Google Form questions and responses |

## Architecture

- **`shared/`** — Shared resources: Python scripts (`scripts/<skill>/`) and `.env` credentials
- **`.claude/`** — Claude Code platform: SKILL.md definitions, `.env` → `../shared/.env` (symlink), `scripts/` → `shared/scripts/<skill>/` (symlink)
- **`.cursor/`** — Cursor platform: same structure as `.claude/`, symlinks to `shared/`
- Scripts use only Python stdlib (urllib) except `google-forms-viewer` which requires the Google client library

## Adding or Modifying Skills

1. Create/update `SKILL.md` under `.claude/skills/<name>/` (or `.cursor/skills/<name>/`) with trigger, workflow steps, and output format
2. If a Python script is needed, place it in `shared/scripts/<name>/` and create symlinks from each platform's `skills/<name>/scripts/`
3. Implement `_load_dotenv()` using `os.path.abspath(__file__)` (not `Path.resolve()`) to preserve symlink paths
3. Ensure Windows UTF-8 compatibility if the script prints Unicode:
   ```python
   if sys.platform == "win32":
       sys.stdout.reconfigure(encoding="utf-8")
   ```

## Commit Message Convention

Format: `[scope] verb summary` (scope optional for broad changes)
Verbs: `add` (new), `update` (enhance), `fix` (bug), `remove`, `refactor`, `docs`
Language: Korean if the changed content is Korean, otherwise English. Max 72 chars per line.
