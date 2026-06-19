# Contributing to target

Thanks for contributing. This repo follows the chrysa
[Execution Standard](https://github.com/chrysa/shared-standards/blob/main/EXECUTION_STANDARD.md).

## Prerequisites

Install dev dependencies and pre-commit hooks:

```bash
make install
```

## Workflow

1. **Branch** from `main` using a typed prefix: `feat/`, `fix/`, `chore/`,
   `docs/`, `ci/`, `refactor/`, `test/`, `perf/`. Direct commits to `main` are
   blocked (`no-commit-to-branch`).
2. **Develop** using the `make` targets only — never call `pytest` / `ruff` /
   `mypy` directly on the host: `make test`, `make test-cov`, `make lint`,
   `make format`, `make typecheck`.
3. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): subject` (allowed types: feat, fix, docs, style, refactor, test,
   chore, perf, revert, ci). Commit messages are linted via `conventional-pre-commit`.
4. **Verify** before pushing, then open a PR against `main`.

Verification commands:

```bash
pre-commit run --all-files
make test
```

CI (pre-commit, lint, test, sonar) must pass and one approval is required before merge.

## Code standards

- All committed files (code, comments, docs, config) are in **English**.
- No hardcoded secrets — use env vars and keep `.env.example` in sync.
- New behaviour ships with tests; keep coverage at or above the project threshold.

## Reporting issues

Use the issue templates under `.github/ISSUE_TEMPLATE/`. Include reproduction
steps, expected vs actual behaviour, and environment details.
