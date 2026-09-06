---
name: spec
description: Write a feature specification (reports/specs/<feature>.md) as the first gate of the spec→plan→implementation workflow. Trigger with /spec <feature>.
---

# /spec — Write a feature specification

You are producing the **specification** artefact, the first mandatory gate before
any code can be written (enforced by `.claude/hooks/enforce-spec-plan.cjs`).

## Steps

1. Determine the feature slug from the argument (`/spec <slug>`). If omitted, derive
   it from the current git branch (`feature/<slug>` → `<slug>`). Use kebab-case.
2. If `reports/specs/<slug>.md` already exists, read it and propose edits instead of
   overwriting.
3. Gather requirements by asking the user targeted questions ONLY where the intent
   is ambiguous — do not interrogate on things you can infer from the codebase.
4. Write `reports/specs/<slug>.md` using the template below, with `status: draft`.
5. Tell the user explicitly: **the spec is `draft`; review it and set
   `status: approved` in the frontmatter to unlock `/plan`.** Do NOT set it to
   approved yourself — approval is the human validation step.

## Template

<!-- prettier-ignore -->
```markdown
---
name: <slug>
status: draft
author: <git user>
created: <YYYY-MM-DD>
---

# Spec — <Human title>

## Context / problem
Why this work exists; the user-facing or system problem being solved.

## Goals
- Bullet list of what success looks like.

## Non-goals
- Explicitly out of scope.

## Functional requirements
- FR1: …
- FR2: …

## Acceptance criteria
- [ ] Measurable, testable criteria (map to tests later).

## Constraints & dependencies
Stack specifics, external services and provider integrations, and the standards
that bind this work (from CLAUDE.md / `standards/`).

## Risks / open questions
```

## Rules

- Language: English (per project conventions).
- Keep it focused: a spec describes WHAT and WHY, never HOW (that's the plan).
- One spec file per feature slug.
