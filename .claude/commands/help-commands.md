---
description: Show all available custom commands and how to use them
---

# Command: Help Commands

List the chrysa custom slash commands and how to use them.

## Usage

```text
/help-commands
```

## Available Commands

| Command | Purpose | Agents |
|---|---|---|
| `/custom-init` | Generate a structured `CLAUDE.md` via phased parallel analysis | solution-architect, backend, devops, qa, code-quality-debugger, technical-writer |
| `/commit` | Create a Conventional Commit with atomic-commit analysis | code-quality-debugger, technical-project-lead |
| `/issue <n>` | Resolve a GitHub issue end-to-end (GitHub Flow) | fullstack, backend, frontend, qa |
| `/reviewpr <n>` | Review a PR (correctness, OWASP, observability, tests) | code-quality-debugger, technical-project-lead, qa, solution-architect |
| `/test <scope>` | Run/improve tests — **Docker / Makefile only** | qa, code-quality-debugger, backend, frontend |
| `/help-commands` | This help | — |

## chrysa Conventions (apply to all commands)

- **Tests/lint/typecheck**: Docker or pre-commit only — never host `pytest`/`ruff`/`tsc`.
- **Commits**: Conventional Commits (`feat`/`fix`/`chore`/`docs`/`ci`/`refactor`/`test`/`perf`);
  no Claude co-author trailer. See `EXECUTION_STANDARD.md` §3.
- **GitHub**: `gh auth switch -u chrysa` before any `gh` command.
- **Branches**: `feat/<issue-id>-desc`, `fix/<issue-id>-desc`, `chore/`, `docs/`, `ci/`.

## Mechanisms

| Mechanism | Trigger | Best for |
|---|---|---|
| **Slash command** | user types `/name` | explicit, on-demand workflows |
| **Skill** | Claude matches the `description` | conventions that apply automatically (`.claude/skills/`) |
| **Subagent** | delegated by Claude or a command | heavy focused work in its own context (`.claude/agents/`) |
