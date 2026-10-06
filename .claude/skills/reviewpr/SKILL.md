---
description: Thoroughly review a GitHub pull request and submit structured feedback
argument-hint: <pr-number>
---

# Command: Review PR

Review the GitHub pull request in $ARGUMENTS and submit structured feedback.

## Usage

```text
/reviewpr <pr-number>
```

## What This Command Does

1. Fetches PR details, diff and CI status via `gh` (run `gh auth switch -u chrysa` first).
2. Checks the PR out locally, reviews quality, security and tests.
3. Documents findings, then submits the review with `gh pr review`.
4. Monitors author responses and re-reviews.

## Agents Used

- **general-code-quality-debugger** — systematic code review.
- **general-technical-project-lead** — security assessment + architectural review.
- **general-qa** — testing validation and edge cases.
- **general-solution-architect** — architectural decisions and patterns.

## Analyze

1. `gh pr view <n>` — details and description.
2. `gh pr diff <n>` — full changes.
3. `gh pr view <n> --json body,title,number` — linked issues; verify acceptance criteria.
4. `gh pr checks <n>` — CI/CD status.

## Review

Check out with `gh pr checkout <n>`, then assess:

1. **Correctness** — bugs, edge cases, error handling, naming, performance.
2. **Security (OWASP)** — injection, authz/authn, secret exposure, unsafe deserialization,
   SSRF. Flag any `.env`/secret leakage. (Aligns with the `review` agent OWASP pass.)
3. **Observability** — meaningful logging on error paths, metrics on critical paths, no
   sensitive data in logs.
4. **Tests** — run via **Docker / `make test`** (never host runners); confirm affected
   areas are covered.
5. **Docs** — comments clear; README/docs updated if behavior changed.

## Provide Feedback

1. Document findings with severity (blocking / suggestion) and concrete code suggestions.
2. Submit via `gh pr review`: approve if all checks pass, else request changes with specifics.

## Iterate

Monitor with `gh pr view --comments`, re-review after changes, approve once resolved.
Be constructive and specific — critique the code, not the person.
