---
name: plan
description: Write an implementation plan (reports/plans/<feature>.md) from an approved spec, as the second gate of the spec→plan→implementation workflow. Trigger with /plan <feature>.
---

# /plan — Write an implementation plan

You are producing the **plan** artefact, the second mandatory gate. It requires an
**approved spec** and, once approved itself, unlocks code edits (enforced by
`.claude/hooks/enforce-spec-plan.cjs`).

## Steps

1. Resolve the feature slug (`/plan <slug>` or current git branch).
2. Read `reports/specs/<slug>.md`. **Refuse to proceed** if it is missing or its
   frontmatter `status` is not `approved` — tell the user to run `/spec` and approve
   it first.
3. Explore the codebase (prefer codegraph/graphify) to ground the plan in real files,
   symbols and call sites.
4. Write `reports/plans/<slug>.md` using the template below, with `status: draft`.
5. Tell the user explicitly: **the plan is `draft`; review it and set
   `status: approved` to unlock `/implement`.** Do NOT approve it yourself.

## Template

<!-- prettier-ignore -->
```markdown
---
name: <slug>
status: draft
spec: reports/specs/<slug>.md
created: <YYYY-MM-DD>
---

# Plan — <Human title>

## Summary
One paragraph: the implementation approach chosen and why.

## Files to touch
| File | Change |
| ---- | ------ |
| <path/to/module> | … |

## Steps
1. Ordered, concrete steps. Each maps to a small commit where possible.

## Tests
- Unit/integration tests to add or update (mock DB per project rules).
- Which acceptance criteria from the spec each test covers.

## Risks & rollback
Migration/backfill concerns, feature flags, how to revert.

## Standards checklist
- [ ] ≤40 lines/function, ≤300 lines/file, ≤5 args, complexity ≤10
- [ ] ruff-check + ruff-format clean
- [ ] Service classes for business logic; light views
```

## Rules

- Language: English.
- The plan describes HOW; it must trace back to the spec's acceptance criteria.
- Do not start editing source code from this skill — that is `/implement`.
