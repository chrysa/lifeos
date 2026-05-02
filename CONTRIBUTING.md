# Contributing to lifeos

Thank you for your interest in contributing! This project is part of the
**chrysa** ecosystem and follows shared conventions described below.

## Prerequisites

```bash
# GitHub CLI authenticated as chrysa
gh auth status

# Python tooling
pip install pre-commit
pre-commit install

# Project dependencies
make install
```

## Branch naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<short-slug>` | `feat/add-scoring-api` |
| Bug fix | `fix/<short-slug>` | `fix/pagination-overflow` |
| Chore / CI | `chore/<short-slug>` | `chore/update-dependabot` |
| Documentation | `docs/<short-slug>` | `docs/api-reference` |
| Refactoring | `refactor/<short-slug>` | `refactor/extract-helpers` |

> Branches are enforced by `.github/workflows/enforce-feature-branch.yml`.

## Commit format

All commits **must** follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short description>

[optional body]

[optional footer: Closes #N]
```

Types: `feat` · `fix` · `chore` · `docs` · `refactor` · `test` · `perf` · `ci`

## Workflow

1. **Open an issue** (or pick an existing one). One issue = one PR.
2. Create a branch from `main` following the naming convention above.
3. Make your changes, writing tests and updating docs where needed.
4. Run pre-commit hooks locally: `pre-commit run --all-files`
5. Run the test suite: `make test`
6. Push and open a PR. Fill in the PR template completely.
7. Request review from `@chrysa`. Minimum 1 approval required to merge.
8. All CI checks must be green before merge (lint · tests · coverage · SonarCloud).
9. Merge via **squash merge** — one clean commit per PR.

## Code quality gates

| Gate | Requirement |
|------|-------------|
| Tests | All passing, count ≥ baseline |
| Coverage | ≥ baseline (never decrease) |
| Lint | 0 warnings (ruff / eslint) |
| Type check | 0 new errors (mypy / tsc) |
| SonarCloud | No new Critical/Blocker issues |
| Secret scan | Must pass (detect-secrets hook) |

## Local development

```bash
make install    # install all dependencies
make dev        # start dev server / environment
make test       # run full test suite
make lint       # run linters
make build      # production build
```

See the `Makefile` for the full list of available targets.

## Resources

- [DECISIONS.md](./DECISIONS.md) — architectural decisions (ADR mini)
- [chrysa/shared-standards](https://github.com/chrysa/shared-standards) — CI, linting, pre-commit config
- [chrysa/pre-commit-tools](https://github.com/chrysa/pre-commit-tools) — shared pre-commit hooks
- Notion project page — linked in issues and PRs

## Security

Do not open public issues for security vulnerabilities.
Use the **Security** issue template and keep exploit details private.
