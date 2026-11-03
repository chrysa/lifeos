---
description: Take a GitHub issue end-to-end — triage, then route to the feature or bugfix workflow
argument-hint: <issue-number>
---

# Command: Issue workflow (W3)

Resolve GitHub issue `$ARGUMENTS`.

## Steps

1. `env -u GH_TOKEN -u GITHUB_TOKEN gh issue view $ARGUMENTS` (chrysa account).
2. Triage: type (bug / feature / chore), severity, duplicates (`gh issue list --search`),
   linked Shortcut story. If no story exists, ask before creating one.
3. Route:
   - bug → `/wf-bugfix` with the issue's symptom;
   - feature → `/wf-feature <slug>`;
   - chore/docs → the `/issue` command directly.
4. The resulting PR body contains `Closes #$ARGUMENTS` and the Shortcut story id.
5. Once the PR is open, run `/wf-pr-review <pr>` on it before asking for merge.
