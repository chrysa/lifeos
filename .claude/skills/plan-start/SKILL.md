---
name: plan-start
description: Turn an objective into a step-by-step, PR-sized construction plan
argument-hint: <objective>
---

# Plan — Start

Turn the objective in $ARGUMENTS into a step-by-step construction plan that any
coding agent can execute cold. Slash command: `/plan-start <objective>`

Use for multi-PR features, migrations or refactors that span sessions. **Skip**
for tasks completable in a single PR or fewer than ~3 tool calls.

______________________________________________________________________

## Steps

1. **Research** — Pre-flight checks: `git status`, `git branch --show-current`
   (default branch is `develop`), `gh auth status`. Read the modules the objective
   touches, existing `docs/`, and any prior plan files.
2. **Design** — Break the objective into one-PR-sized steps (3–12 typical). For
   each step assign: dependency edges, parallel/serial ordering, and rollback
   strategy. Keep every step within project standards (function ≤ 40 lines,
   ≤ 5 args, complexity ≤ 10, file ≤ 300 lines).
3. **Draft** — Write a self-contained Markdown plan to `docs/plans/<slug>.md`.
   Every step must include: context brief, task list, verification commands
   (`make tests`, `make ruff-check`, `make mypy`), and exit criteria — so a fresh
   agent can execute any step without reading prior steps.
4. Present the step count and parallelism summary; hand off to `/plan-validate`.

______________________________________________________________________

## Conventions

- Each step maps to one branch (`feature/`, `fix/`, `chore/`) off `develop`,
  one PR, squash merge, no force push.
- Content in English.
