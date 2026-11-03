---
name: plan-validate
description: Adversarially review a construction plan before execution
argument-hint: <plan-file>
---

# Plan — Validate

Adversarially review the plan file in $ARGUMENTS before any step is executed.
Slash command: `/plan-validate <plan-file>`

______________________________________________________________________

## Steps

1. Read the plan under `docs/plans/`.
2. Delegate an adversarial review to a strongest-model sub-agent against the
   checklist below. Fix all critical findings before finalizing.
3. Mark the plan as validated (or request a revision of `/plan-start`).

______________________________________________________________________

## Review checklist

- **Self-containment** — can a fresh agent execute each step without reading
  prior steps? Is every context brief complete?
- **Sizing** — is each step one-PR-sized? Split steps that mix concerns.
- **Dependencies** — is the ordering correct? Are parallel steps truly independent?
- **Verification** — does every step list concrete exit criteria and Docker
  Makefile checks (`make tests`, `make ruff-check`, `make mypy`)?
- **Standards** — do planned changes respect project thresholds (function
  ≤ 40 lines, ≤ 5 args, complexity ≤ 10, coverage ≥ 85%) and DDD-per-app layout?
- **Rollback** — does each step define a rollback strategy?
- **Anti-patterns** — no step commits to `develop` directly, no force push, no
  `Co-Authored-By` trailers, no host tooling (Docker/Makefile only).

______________________________________________________________________

## Output

Findings grouped by severity (blocking / suggestion) with the step number and a
concrete fix. Approve only when no blocking findings remain.
