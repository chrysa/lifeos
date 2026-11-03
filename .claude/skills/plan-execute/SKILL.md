---
name: plan-execute
description: Execute a single validated step from a construction plan
argument-hint: <plan-file> <step-number>
---

# Plan — Execute

Execute the step given in $ARGUMENTS from a validated plan.
Slash command: `/plan-execute <plan-file> <step-number>`

______________________________________________________________________

## Steps

1. Read the target step's context brief from the plan under `docs/plans/`.
   Execute cold — rely only on the brief, not on memory of prior steps.
2. Verify dependencies for the step are complete; if not, stop and report.
3. Create the step's branch off `develop`
   (`feature/`, `fix/` or `chore/` per the step type). Never work on `develop`.
4. Implement the task list. Respect project standards
   (function ≤ 40 lines, ≤ 5 args, complexity ≤ 10, file ≤ 300 lines; business
   logic in service classes, DB logic in managers/QuerySets; one class per file).
   Consult `.claude/rules/*.md` before editing.
5. Verify with Docker Makefile targets: `make format-code`, `make ruff-check`,
   `make mypy`, `make tests`. Fix all new violations (never `# noqa` / `# type: ignore`).
6. Confirm the step's exit criteria are met.
7. Commit via `/commit` (Conventional Commits, no `Co-Authored-By`), open a PR
   (squash merge, no force push), and mark the step done in the plan file.

______________________________________________________________________

## On failure

If verification fails and cannot be resolved within the step's scope, stop, revert
using the step's rollback strategy, and report the blocker rather than expanding scope.
