---
description: Fix a bug from symptom to PR (root cause first, red repro test, fix, verify, review)
argument-hint: <symptom | failing test | sentry issue id>
---

# Command: Bugfix workflow (W2)

Fix the bug described by `$ARGUMENTS` without guessing.

## Steps

1. Create `bugfix/<slug>` from `develop`.
2. Run the Workflow tool with `scriptPath: ".claude/workflows/bugfix.js"` and
   `args: {"symptom": "<symptom>", "sentryIssue": "<id or omit>"}`.
3. If `fixed` is false, report the hypotheses and stop — do not patch symptoms.
4. Fix every blocker/major review finding, run `/security-review` on the diff.
5. `/commit` (`fix:`), open the PR linked to the GitHub issue and its Shortcut story.
   Never merge without explicit approval.

## Agents used

general-code-quality-debugger · test-runner · code-reviewer · security-auditor
