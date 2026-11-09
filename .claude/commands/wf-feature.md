---
description: Deliver a feature end-to-end (spec → plan → human gate → implement → verify → review)
argument-hint: <feature-slug>
---

# Command: Feature workflow (W1)

Deliver feature `$ARGUMENTS` through the chrysa spec→plan→implement chain with two human gates.

## Steps

1. **Design** — run the Workflow tool with `scriptPath: ".claude/workflows/feature.js"` and
   `args: {"feature": "$ARGUMENTS", "mode": "design"}`.
2. **Human gate** — show the spec and plan paths plus every critic issue (blockers first).
   Iterate on the documents until the user approves. If the plan flags a structural decision,
   run `/wf-decision` first. Do NOT continue without explicit approval.
3. **Build** — on a feature branch (`feature/<slug>` from `develop`), run the same workflow with
   `"mode": "build"`.
4. **Gate** — if `green` is false, stop and report the failures. Otherwise fix every blocker/major
   finding, then run `/security-review` on the diff.
5. **Ship** — `/commit`, push, open the PR against `develop` referencing its Shortcut story
   (`sc-XXXX`). Update the project's Notion fiche. Never merge without explicit approval.

## Agents used

general-pm · general-solution-architect · general-fullstack-developer · test-runner ·
code-reviewer · security-auditor
