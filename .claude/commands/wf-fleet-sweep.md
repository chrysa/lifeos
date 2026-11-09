---
description: Read-only fleet sweep (deps, standards drift, open PRs) with a prioritised action list
argument-hint: [repo paths… | all]
---

# Command: Fleet sweep workflow (W6)

Audit the fleet without changing anything.

## Steps

1. Build the repo list: the given paths, or for `all` every sibling directory with a `.git`
   entry and a `.claude/` folder.
2. Run the Workflow tool with `scriptPath: ".claude/workflows/fleet-sweep.js"` and
   `args: {"repos": [...], "standardsRoot": "<path to shared-standards>"}`.
3. Report: systemic causes first (one template fix beats N repo fixes), then the top actions.
4. Act only with approval, in this order:
   - green dependabot `merge-candidate` PRs → merge in small batches;
   - `needs-fix` → `/wf-bugfix` per repo;
   - standards drift → `distribute-standards` (GitHub Action), never a local mass push.
5. Log the summary on the Notion fiches and Shortcut stories touched.
