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
- `CONFLUENCE_PAGE_URL` — target Confluence page URL for save-article skill

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
| `/jira-bug-analyzer` | `<issue URL> 문제코드를 찾아줘` | Finds problem code in the codebase for a Jira bug |
| `/git-mr-review` | `<MR URL> 코드 리뷰 해줘` | Structured code review for a GitLab MR |
| `/google-forms-viewer` | `<form URL> 접속해줘` | Displays Google Form questions and responses |
| `/create-my-skill` | `스킬 만들어줘` | Interactively creates and validates a new SKILL.md |
| `/save-article` | `<article URL> 아티클 저장` | Extracts title/summary from a URL and appends to a Confluence page |

## Architecture

- **`shared/`** — Shared resources: `.env` credentials and Python scripts organized by service:
  - `scripts/jira/` — Jira API scripts (`fetch_jira_issue.py`, `summarize_jira_filter.py`)
  - `scripts/confluence/` — Confluence API scripts (`fetch_confluence_page.py`, `search_confluence_raw.py`)
  - `scripts/git-mr-review/` — GitLab MR diff fetcher
  - `scripts/google-forms-viewer/` — Google Forms fetcher
- **`.claude/`** — Claude Code platform: SKILL.md definitions, `.env` → `../shared/.env` (hardlink), `scripts/<service>/` → `shared/scripts/<service>/` (junction)
- **`.cursor/`** — Cursor platform: same structure as `.claude/`, junctions to `shared/`
- Scripts use only Python stdlib (urllib) except `google-forms-viewer` which requires the Google client library

## Adding or Modifying Skills

1. Create/update `SKILL.md` under `.claude/skills/<name>/` (or `.cursor/skills/<name>/`) with trigger, workflow steps, and output format
2. If a Python script is needed, place it in the appropriate `shared/scripts/<service>/` directory (e.g., `jira/`, `confluence/`) and create junctions from each platform's `skills/<name>/scripts/<service>/`
3. Implement `_load_dotenv()` by searching parent directories for `.env` (using `os.path.abspath(__file__)`, not `Path.resolve()`, to preserve symlink paths)
3. Ensure Windows UTF-8 compatibility if the script prints Unicode:
   ```python
   if sys.platform == "win32":
       sys.stdout.reconfigure(encoding="utf-8")
   ```

## Commit Message Convention

Format: `[scope] verb summary` (scope optional for broad changes)
Verbs: `add` (new), `update` (enhance), `fix` (bug), `remove`, `refactor`, `docs`
Language: Korean if the changed content is Korean, otherwise English. Max 72 chars per line.
