---
description: Multi-specialist PR review with adversarial verification and a single verdict
argument-hint: <pr-number>
---

# Command: PR review workflow (W4)

Review PR `$ARGUMENTS`.

## Steps

1. Run the Workflow tool with `scriptPath: ".claude/workflows/pr-review.js"` and
   `args: {"pr": "$ARGUMENTS"}`.
2. Present the verdict (`APPROVED` / `CHANGES_REQUESTED`), the missing-story flag and the surviving
   findings as `file:line — severity — problem — fix`.
3. Ask before posting. On approval only:
   `env -u GH_TOKEN -u GITHUB_TOKEN gh pr review $ARGUMENTS --comment|--request-changes|--approve -b "<summary>"`.
4. Never merge, never use `--admin`.

## Agents used

code-reviewer · security-auditor · general-qa · infra-reviewer (infra diffs) ·
general-frontend-developer (frontend diffs)
