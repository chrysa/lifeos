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

## Workflow Commands (`/wf-*`)

Orchestrate the commands, skills and agents above. W1, W2, W4 and W6 run a deterministic
Workflow script from `.claude/workflows/`; human gates stay in the command.

| Command | Purpose | Script |
|---|---|---|
| `/wf-feature <slug>` | W1 · spec → plan → human gate → implement → verify → review | `feature.js` |
| `/wf-bugfix <symptom>` | W2 · competing root-cause hunters → red repro → fix → verify → review | `bugfix.js` |
| `/wf-issue <n>` | W3 · triage a GitHub issue and route to W1/W2 | — |
| `/wf-pr-review <n>` | W4 · parallel specialists + adversarial verify → single verdict | `pr-review.js` |
| `/wf-decision <question>` | W5 · council → ADR consistency → falsifiable ADR | — |
| `/wf-fleet-sweep [repos]` | W6 · read-only deps / standards drift / open-PR sweep | `fleet-sweep.js` |
| `/wf-release-lib <repo> <ver>` | W7 · consumer contract tests → bump → pin-update PRs | — |

## chrysa Conventions (apply to all commands)

- **Tests/lint/typecheck**: Docker or pre-commit only — never host `pytest`/`ruff`/`tsc`.
- **Commits**: Conventional Commits (`feat`/`fix`/`chore`/`docs`/`ci`/`refactor`/`test`/`perf`);
  no Claude co-author trailer. See [chrysa standards](https://github.com/chrysa/shared-standards/blob/main/standards/STANDARDS.chrysa.md).
- **GitHub**: `gh auth switch -u chrysa` before any `gh` command.
- **Branches**: `feat/<issue-id>-desc`, `fix/<issue-id>-desc`, `chore/`, `docs/`, `ci/`.

## Mechanisms

| Mechanism | Trigger | Best for |
|---|---|---|
| **Slash command** | user types `/name` | explicit, on-demand workflows |
| **Skill** | Claude matches the `description` | conventions that apply automatically (`.claude/skills/`) |
| **Subagent** | delegated by Claude or a command | heavy focused work in its own context (`.claude/agents/`) |
