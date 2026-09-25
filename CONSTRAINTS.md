# Constraints — lifeos (my-assistant)

> Sourced from CLAUDE.md "Key Constraints", `pyproject.toml`, the Makefile,
> `.pre-commit-config.yaml`, CONTRIBUTING.md and the chrysa standards pointed to
> from CLAUDE.md. Tags: [PLATFORM] [LANGUAGE] [SECURITY] [PROCESS] [ARCH] [DEP].

## Runtime & platform

- [PLATFORM] Must run on **Linux and Windows**; no platform-specific code in core or plugins. (CLAUDE.md — FACT as stated intent)
- [LANGUAGE] Python floor: `pyproject.toml` requires **>=3.14**; CLAUDE.md says "3.12+ minimum, target 3.14". These disagree — treat 3.14 (the manifest) as binding. (FACT — contradiction, see REVIEW.md)
- [DEP] **PySide6** is optional (`[ui]` extra); the app must start headless without it. `--ui` currently warns and runs headless. (FACT: README, `app.py`)
- [DEP] **discord.py** is optional (`[discord]` extra); the discord plugin must skip gracefully if absent. (FACT: pyproject extras; plugin not yet present)

## Configuration & secrets

- [SECURITY] No hardcoded secrets, keys, tokens, or machine paths — always env-var interpolation (`${ENV_VAR}`) or env reads. (FACT: CLAUDE.md; `.mcp.json` and `.env.example` use placeholders)
- [ARCH] All config via TOML; no hardcoded values except Pydantic defaults. (FACT: settings.py)
- [SECURITY] OWASP Top 10 posture: validate all external inputs; no secrets in logs. (INFERENCE: stated in CLAUDE.md; little external-input surface exists yet)

## Architecture

- [ARCH] Plugin failures must never crash the application — `try/except` in `setup()`/`teardown()`. (FACT: CLAUDE.md; enforcement lands with the plugin system, still PLANNED)
- [ARCH] All HTTP calls use `httpx.AsyncClient` with an explicit timeout (default 30s). (FACT: CLAUDE.md; no HTTP code present yet)
- [ARCH] Projects talk through **versioned contracts only**; LifeOS publishes `personal.*` capability manifests to LOGOS, never shared source. (FACT: ADR-LIFEOS-001 + chrysa standard)
- [ARCH] Object-oriented, one class per file; import the item not the module; call with named arguments (chrysa backend-python rules). (FACT: standards pointers in CLAUDE.md)

## Process & tooling (chrysa standards)

- [PROCESS] Branch from `main` with a typed prefix (`feat/ fix/ chore/ docs/ ci/ refactor/ test/ perf/`); direct commits to `main` blocked. (FACT: CONTRIBUTING.md, `no-commit-to-branch`) — NOTE: CLAUDE standards core also describes a `main`/`develop` model; this repo's CONTRIBUTING branches from `main`. (see REVIEW.md)
- [PROCESS] Conventional Commits, linted by `conventional-pre-commit`. (FACT: CONTRIBUTING.md)
- [PROCESS] One PR per issue; every PR references a Shortcut story (`enforce-shortcut-link.yml`). (FACT: standards + workflow)
- [PROCESS] All committed files in **English**; this repo's `ai-instructions.md` guide is French by design. (FACT)
- [PROCESS] Security scanning is a gate in pre-commit **and** CI (detect-secrets, `secret-scan.yml`). (FACT)
- [PROCESS] Coverage must stay ≥85% (`--cov-fail-under=85`). (FACT: pyproject)

## Container policy (chrysa standard) vs. current tooling — tension

- [ARCH] chrysa standard: **everything runs in a container**; no virtualenv; deps installed in containers, not on the host; Dockerfiles multi-stage with `production` + `dev` stages. (FACT: standards pointers)
- Current state (FACT): `make install`/`dev` run `pip install -e` **on the host**; only `Dockerfile.test` exists (single `test` target, `python:3.14-slim`) and `make docker-test` runs tests in a container. There is **no** app Dockerfile, no `production`/`dev` multi-stage image, and no compose file. This repo therefore only partially meets the container standard. (see REVIEW.md)
