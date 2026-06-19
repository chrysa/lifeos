---
description: Resolve a GitHub issue end-to-end following GitHub Flow
argument-hint: <issue-number>
---

# Command: Issue

Analyze and resolve the GitHub issue in $ARGUMENTS following GitHub Flow and chrysa standards.

## Usage

```text
/issue <issue-number>
```

## What This Command Does

1. Reads the issue with `gh issue view` (run `gh auth switch -u chrysa` first).
2. Researches prior art (PRs, codebase, scratchpad) and writes a plan.
3. Creates a feature branch, implements in small increments, committing via `/commit`.
4. Tests via Docker / `make test` and opens a PR using the chrysa PR template.

## Agents Used

Selected by issue type: **general-fullstack-developer**, **general-backend-developer**,
**general-frontend-developer**, **general-qa**, with **general-purpose** for research.

## General

- `gh auth switch -u chrysa` before any `gh` command.
- Follow GitHub Flow: https://docs.github.com/en/get-started/using-github/github-flow
- Use `/commit` after each logical step (Conventional Commits, no Claude trailer).
- Capture context/decisions in a scratchpad so work survives across sessions.

## Workflow

Adapt to the issue type:

- **Standard** (feature): PLAN → CREATE → TEST → DEPLOY
- **Exploration** (research): Explore → Plan → Confirm → Code → Commit
- **Test-first** (bug/TDD): Test → Commit → Code → Iterate → Commit
- **Rapid prototyping** (UI/UX): Code → Screenshot → Iterate

## Plan

1. `gh issue view <n>` — understand the problem; ask clarifying questions if needed.
2. Search PRs and the codebase for prior art.
3. Break the issue into small tasks; document the plan in a scratchpad with the issue link.

## Create

1. Branch per `EXECUTION_STANDARD.md` naming: `feat/<issue-id>-short-desc`
   (`fix/`, `chore/`, `docs/`, `ci/` per type).
2. Implement in small steps; `/commit` after each.

## Test

- Run tests via **Docker / `make test`** — never host `pytest`/`ruff`/`tsc`.
- Add tests describing the expected behavior; run the full suite; fix failures before moving on.

## Deploy

Open a PR. The chrysa PR template (`@templates/pr-template.md` /
`.github/PULL_REQUEST_TEMPLATE.md`) auto-populates — fill Summary, Motivation (link the issue),
Changes, Testing, Checklist. PR title = the most significant commit message.
