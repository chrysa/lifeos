---
name: implement
description: Implement a feature according to its approved spec and plan, the final stage of the spec→plan→implementation workflow. Trigger with /implement <feature>.
---

# /implement — Implement an approved feature

You are executing the **implementation** stage. Source-code edits are only permitted
when both the spec and the plan are `approved` — the `enforce-spec-plan` PreToolUse
hook will block edits otherwise, so verify the gates before you start.

## Preconditions (check first)

1. Resolve the feature slug (`/implement <slug>` or current git branch).
2. Read `reports/specs/<slug>.md` and `reports/plans/<slug>.md`. Both frontmatter
   `status` values MUST be `approved`. If either is not, STOP and tell the user which
   gate is missing — do not attempt to edit code.
3. Ensure `.claude/.active-feature` contains the slug OR the branch is
   `feature/<slug>` (etc.), so the hook resolves the same feature.

## Execution

1. Follow the plan's steps in order. Do not invent scope beyond the spec.
2. Keep changes aligned with the plan's "Files to touch"; if reality diverges
   materially, pause and update the plan (re-approval) rather than silently drifting.
3. Add/adjust the tests listed in the plan. Mock DB access in unit tests.
4. After changes: run `make ruff-check` and `make ruff-format`; run `make tests`
   for touched modules. Report results honestly.
5. Tick the spec's acceptance criteria and the plan's standards checklist as they
   are satisfied.

## Rules

- Language: English (code, comments, commits).
- Respect all standards in CLAUDE.md and `.claude/rules/*.md`.
- Never bypass the hook (no editing `.claude/.active-feature` to a fake slug just to
  unlock edits). Approval is the human's call.
