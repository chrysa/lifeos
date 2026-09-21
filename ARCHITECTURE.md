# Architecture — lifeos (my-assistant)

> Grounded in the files in this repo (README.md, pyproject.toml, Makefile,
> Dockerfile.test, `lifeos/` source, config files). Where docs and manifests
> could diverge, the manifests win and the divergence is noted.

## Purpose

`lifeos` is an early scaffold for a floating, multi-OS AI assistant. As of this
repo it is a **headless CLI core only**: it loads configuration, resolves which
plugins are enabled, and runs a logging run-loop that reports "ready". The
overlay UI, messaging/AI/service plugins, and system monitoring are declared as
goals but **not yet implemented** (README "Status" table; package still marked
`Development Status :: 3 - Alpha` in `pyproject.toml`).

## Stack

- **Python** `>=3.14` (`pyproject.toml`; note `tool.ruff` targets `py313` with a
  comment explaining a `py314` ruff-format workaround).
- **Click** — CLI framework.
- **Pydantic v2** + **pydantic-settings** — TOML config validation.
- **sentry-sdk** — observability / error reporting.
- **httpx**, **psutil**, **rich**, **python-dotenv** — declared runtime deps
  (psutil-based monitoring not yet wired).
- Optional extras (declared, not implemented): **PySide6** (`[ui]`),
  **discord.py** (`[discord]`).
- Build backend: **hatchling**. Lint/format: **ruff**. Types: **mypy** (strict).
  Tests: **pytest** (+ pytest-asyncio, pytest-cov, pytest-mock).

## Layout

- `lifeos/__main__.py` — module entry (`python -m lifeos`), calls `main`.
- `lifeos/cli.py` — Click entry point; flags and startup.
- `lifeos/app.py` — `Application` lifecycle (headless run-loop).
- `lifeos/config/settings.py` — Pydantic settings + TOML loader.
- `lifeos/observability/` — Sentry init.
- `tests/` — pytest suite.
- `scripts/` — tooling incl. `quality_gate.py` (regression gates).
- `docs/`, `mkdocs.yml` — MkDocs documentation.
- `standards/`, `makefiles/`, `.github/`, `.devcontainer/` — shared standards,
  Make includes, CI, devcontainer.
- `graphify-out/`, `lifeos/` package. Repo-level config: `.pre-commit-config.yaml`,
  `.quality-gate.json`, `sonar-project.properties`, `cliff.toml`, `GitVersion.yml`.

## Entrypoints

- Console script: `lifeos = "lifeos.__main__:main"` (`pyproject.toml`).
- `python -m lifeos` — same entry via `__main__`.
- CLI flags (README): `--config`, `--ui/--headless`, `--enable`, `--debug`,
  `--version`. `--ui` currently logs a warning and runs headless (overlay build
  does not exist yet).

## Data & external deps

- **Config**: optional TOML file. Resolution order: `--config <path>`, then
  `~/.config/lifeos/config.toml`. Absent file → defaults; app still runs. Only
  plugin enable flags (`discord`, `github`, `notion`) are modelled so far.
- **No database** — N/A, not present in repo.
- **Sentry**: initialised from env (`ENVIRONMENT`, `RELEASE` in `.env.example`;
  DSN expected via env, no secret committed).
- **MCP servers** (`.mcp.json`, dev-time, not app runtime): GitHub MCP
  (`GITHUB_TOKEN`) and Notion MCP (`NOTION_API_KEY`) — both read from env
  placeholders, no hardcoded secrets.

## Build & test (real commands)

From `Makefile` (tier `lib`):

```bash
make install        # pip install -e .            (headless core)
make install-ui     # pip install -e ".[ui,discord]"
make dev            # pip install -e ".[ui,discord,dev]" + pre-commit install
make test           # pytest tests/ -v
make test-cov       # pytest with coverage
make docker-test    # docker build --target test -f Dockerfile.test && run
make lint           # ruff check lifeos tests
make format         # ruff format lifeos tests
make typecheck      # mypy lifeos tests
make build          # python -m build (wheel)
make run-headless   # python -m lifeos --headless
make ci             # lint + typecheck + test
```

Coverage gate: `--cov-fail-under=85` (`pyproject.toml [tool.pytest]`).
Container tests use `Dockerfile.test` (`python:3.14-slim`, `.[dev]`).

## Security notes

No secrets are committed: `.env.example` holds placeholders and `.mcp.json` uses
`${GITHUB_TOKEN}` / `${NOTION_API_KEY}` env references. A `.secrets.baseline`
(detect-secrets) and `.pre-commit-config.yaml` gate secret scanning.
