---
description: Scaffold a new ADR in the chrysa refutable format (fatal hypothesis, kill-test, gate)
argument-hint: <short decision title>
---

# Command: ADR New

Scaffold a new Architecture Decision Record for **$ARGUMENTS**, following the
chrysa ADR format. Read `.claude/rules/adr.md` first — it is the standard.

## Usage

```text
/adr-new <short decision title>
```

## Steps

1. **Legitimacy check.** An ADR is mandatory only for: a new external dependency,
   an LLM/cloud provider choice, a breaking public-API change, a data-model
   change, or an exception to a strategic pillar (`.claude/rules/pillars.md`). No
   trigger hit → say so and write nothing. An ADR for a refactor or a naming
   choice is noise that dilutes the real ones.

2. **Number & file.** Next number = highest existing + 1, four digits, never
   reused. Path: `docs/adr/<SERIES>-<NNNN>-<kebab-slug>.md`, where `<SERIES>` is
   the repo's ADR series (see its `CLAUDE.md`). File written in English.

3. **The three fields that carry the format.**
   - *Fatal hypothesis* — the single falsifiable belief whose falsity kills the
     decision. One only; about the real world, not an internal intention.
   - *Kill-test* — the observable, dated signal proving it wrong: what to measure,
     which threshold, when checked, action on breach. Mechanise it as a test, or
     state why it cannot be.
   - *Validation gate* — the pre-agreed condition that unlocks the next step,
     written before implementation.

4. **Options considered.** Each rejected option gets a real reason — no strawman.

5. **Consequences.** Accepted costs · gains · debt created (and when paid) ·
   blast radius (what changes if this ADR is Killed).

6. **Status = `Proposed`.** Never self-promote an ADR to `Accepted` — that is the
   author's call. Touch no other file (no code, no external writes).

7. **Report** the file path, plus the fatal hypothesis and kill-test in one
   sentence each — that is what the decider rules on.
