---
description: Make and record a structural decision (council → ADR consistency → falsifiable ADR)
argument-hint: <question to decide>
---

# Command: Decision workflow (W5)

Decide `$ARGUMENTS` and record it.

## Steps

1. Run the `council` skill on the question: options, strongest counter-arguments, recommendation.
   Weigh each option by its **maintenance cost**, cheapest first.
2. Check consistency with existing ADRs in `docs/adr/` and the settled stack ADRs
   (`standards/rules/stack.md`). A conflict means superseding, not editing.
3. Present the recommendation; the human decides.
4. `/adr-new` with the chosen option — fatal hypothesis, kill-test (threshold + cadence + action),
   validation gate, rejected options with real reasons.
5. Link the ADR from the project's Notion fiche.
