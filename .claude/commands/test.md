---
description: Run and improve the test suite for a given scope (Docker / pre-commit only)
argument-hint: <file-or-directory | feature | all>
---

# Command: Test

Run and improve the test suite for the scope in $ARGUMENTS.

## Usage

```text
/test <file-or-directory>
/test <feature>
/test all
```

## What This Command Does

1. Determines the scope (file, directory, feature, or all).
2. Runs targeted tests, then the full suite — **always via Docker / Makefile targets**.
3. Fixes failures and adds missing coverage.
4. Reports results and commits improvements via `/commit`.

## ⚠️ Execution Rule (NON-NEGOTIABLE)

Tests, lint and type-checks run through **Docker or pre-commit ONLY**. Never invoke host
`pytest`, `ruff`, `tsc`, `jest`, `vitest`, etc. directly. Use the standard Makefile targets
(`EXECUTION_STANDARD.md` §1):

- `make test` — unit tests
- `make test-cov` — tests + coverage (`coverage.xml`)
- `make lint` / `make typecheck`
- `make pre-commit` — all pre-commit hooks
- `make docker-up` / `make docker-down` — service dependencies for integration/e2e

If a target is missing, that is a standards gap — fix the Makefile, do not fall back to host tools.

## Agents Used

- **general-qa** — testing strategy and automation (primary).
- **general-code-quality-debugger** — debug failing tests.
- **general-backend-developer** / **general-frontend-developer** — API and UI test coverage.

## Assess

1. Resolve scope from $ARGUMENTS (file/dir → focus there; feature → related specs; `all` → full run).
2. Check current coverage (`make test-cov`); identify weak areas.
3. Review existing test patterns for examples and chrysa conventions (`testing-pytest` skill).

## Run

1. Targeted tests first (verbose, fail-fast) via `make test` scoped to the change.
2. Integration / e2e via `make docker-up` + the project's e2e target if contracts are affected.
3. Full suite via `make test`; watch for flakiness, timeouts, perf regressions.

## Improve

1. Fix failures (decide test-vs-implementation); commit via `/commit`.
2. Add tests for uncovered edge cases — happy **and** error paths.
3. Refactor: remove duplication, clarify descriptions, speed up slow tests.

## Validate & Report

- Re-run to catch flakiness; confirm coverage rose meaningfully (not just numerically).
- Summarize improvements; if part of a PR, update its Testing section. Commit all changes.
