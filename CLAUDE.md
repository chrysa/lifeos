# CLAUDE.md — lifeos

> @[claude-sonnet-4-6]

## Project Purpose

Floating AI assistant multi-OS desktop application. Monitors the system, integrates with messaging platforms (Discord), routes queries to AI providers (GitHub Copilot via OpenCode, OpenAI-compatible), and connects to external services (Notion, GitHub). Runs as a floating overlay or headless tray application on Linux and Windows.

## Architecture

- `cli.py` — Click entry point; `--ui`, `--headless`, `--enable`, `--config` flags
- `app.py` — Application lifecycle; loads config, initialises plugin registry, starts UI
- `config/settings.py` — Pydantic-based TOML config loader with `${ENV_VAR}` interpolation
- `core/assistant.py` — AI orchestration; routes prompts to the best available provider
- `plugins/base.py` — `BasePlugin` ABC: `setup()`, `teardown()`, `get_status()`, event emitter
- `plugins/system/monitor.py` — `psutil`-based async system monitor; emits `SystemStatsEvent`
- `plugins/messaging/discord.py` — Discord webhook sender + bot channel monitor (optional)
- `plugins/ai/opencode.py` — HTTP client for `opencode serve` REST API (port 4096)
- `plugins/ai/openai.py` — OpenAI-compatible chat completions client (stream support)
- `plugins/services/notion.py` — Notion REST API v1 client (search/create/update pages)
- `plugins/services/github.py` — GitHub REST API client (repos, issues, PRs, notifications)
- `ui/overlay.py` — PySide6 frameless always-on-top floating window
- `ui/tray.py` — `QSystemTrayIcon` + context menu
- `ui/components/chat.py` — Chat input/output widget with streaming display
- `ui/components/system_panel.py` — Collapsible system stats panel

## Key Constraints

- Python 3.12+ minimum; target 3.14
- Must run on Linux **and** Windows (no platform-specific code in core or plugins)
- PySide6 is optional (`[ui]` extra); app must start headless without it
- `discord.py` is optional (`[discord]` extra); discord plugin must gracefully skip if absent
- All config via TOML — no hardcoded values except defaults in Pydantic models
- No secrets in code — always use env var interpolation: `"${ENV_VAR}"`
- Plugin failures must never crash the application — always `try/except` in `setup()` / `teardown()`
- All HTTP calls use `httpx.AsyncClient` with explicit timeout (default 30s)
- OWASP Top 10 compliance: validate all external inputs, no secrets in logs

## Config System

Config is loaded (in order) from:
1. `--config <path>` CLI flag
2. `~/.config/lifeos/config.toml`
3. `./config/config.toml`

Env var interpolation: `"${ENV_VAR}"` patterns in any TOML string value are expanded via `os.environ`. If the var is missing, the literal `${ENV_VAR}` string is kept (no silent failure — warn in logs).

## Plugin System

Each plugin extends `BasePlugin`:
- `setup()` → called once on app start; must be idempotent
- `teardown()` → cleanup on app exit
- `get_status()` → `PluginStatus(running: bool, error: str | None, metadata: dict)`
- Plugins register event handlers via `self.emit(event)` / `app.on(EventType, handler)`

## Development Commands

```bash
make dev          # pip install -e ".[ui,discord,dev]" + pre-commit install
make test         # pytest
make lint         # ruff check
make format       # ruff format
make run          # python -m lifeos --ui
make run-headless # python -m lifeos --headless
```

## Testing

- Each plugin must have unit tests in `tests/plugins/`
- Use `pytest-mock` to mock `httpx.AsyncClient` — no real HTTP in unit tests
- Use `psutil` stubs or monkeypatch for system monitor tests
- UI tests are skipped in CI (no display) — use `pytest.mark.skipif(sys.platform != "linux" ...)`

## Related repositories

- `chrysa/ai-aggregator` — future backend for AI routing (Scenario C)
- `chrysa/discord-bot-back` — Discord bot (complements messaging plugin)
- `chrysa/server` — Phase 7 k8s deployment (`assistant.ducal.me:8000`)
- `chrysa/diy-stream-deck` — similar Python desktop tool pattern
- `chrysa/github-actions` — shared CI actions
- `chrysa/pre-commit-tools` — shared pre-commit hooks
- `chrysa/shared-standards` — Copilot instructions and standards

## Notion

Project tracking: [to be filled after creation]

## Compact instructions

When compacting, always preserve:
1. List of all files modified this session (with paths)
2. Current task description and next steps
3. Any uncommitted / unpushed changes
4. Open blockers and errors not yet resolved

## Skills

Shared skills from `shared-standards/.claude/skills/`:

- `ui-ux/SKILL.md` — UX/UI/ergonomics across ALL surfaces (web, CLI, VS Code, Discord, desktop, game, agent) + WCAG 2.1 AA + dark mode + i18n FR+EN (load when building any human-facing surface)


<!-- chrysa:standards:start · managed by distribute-standards.sh · DO NOT EDIT -->
# chrysa — Transverse Standards

These conventions are identical across every chrysa repo. Repo-specific rules live in the
local `CLAUDE.md`; this file is the shared baseline imported by it.

## Normative annexes

This file is the **only** artifact inlined into consumer repos. The annexes below are
**equally normative** — they detail rules stated here in short form. They are not inlined;
read them at
`https://github.com/chrysa/shared-standards/blob/main/standards/annexes/`.
Where an annexe and this file disagree, **this file wins**.

| Annexe                    | Scope                                                          |
| ------------------------- | -------------------------------------------------------------- |
| `FRONTEND.md`             | TypeScript config & rules · React layering · frontend architecture · frontend tests |
| `ARCHITECTURE-DDD.md`     | project profiles · DDD levels · layers & aggregates · Python & C#/.NET structure |
| `AGENTIC-CAPABILITIES.md` | agent actions: manifests, risk R0–R5, sandboxing, audit trail   |
| `PROJECT-DECOUPLING.md`   | inter-project contracts, forbidden linkages, degradation        |
| `CONTAINERS-K3S.md`       | reference stage shape · container responsibility · k3s workload baseline |
| `TESTING.md`              | common test levels and rules across languages                   |
| `GOVERNANCE.md`           | rule identity, maturity ladder, enforcement rollout, sources of truth |

**Source of truth:** the canon lives in this repo. Notion is a governance and decision view
of the standards corpus, not its authority (`GOVERNANCE.md` GV-000). `chrysa/standards` is
deprecated and archived — nothing is added to it, nothing reads from it.

## Cross-cutting stack (settled ADRs — do not relitigate)

| Layer            | Decision                                                        |
|------------------|----------------------------------------------------------------|
| Python           | 3.14 target (CI matrix 3.12 + 3.14)                            |
| FastAPI          | >= 0.115 + Pydantic v2                                          |
| Frontend         | React 19 + TypeScript 7 + Vite 8                                |
| UI               | shadcn/ui + Tailwind CSS                                        |
| State            | TanStack Query + Zustand                                        |
| DB               | PostgreSQL 16 + Redis 7                                         |
| ORM              | SQLAlchemy 2.0 async + Alembic                                  |
| Auth             | Cluster SSO (OIDC) → external OAuth → local (bcrypt) · MFA-capable |
| i18n             | react-i18next + fastapi-babel · FR + EN from V1                 |
| Monorepo         | Turborepo + pnpm workspaces                                     |
| Versioning       | GitVersion (semantic auto — never bump manually)               |
| Quality CI       | SonarCloud (0 hotspot · rating A)                               |
| Linting          | Ruff + Mypy (Python) · ESLint (TS)                             |
| Pre-commit       | detect-secrets + ruff + mypy + commitlint                      |
| Error handling   | withErrorHandling() → auto GitHub Issue on failure             |
| Hosting          | Kimsufi · Docker Compose (local) · Nginx · Certbot · Tailscale  |
| Monitoring       | Sentry + Uptime Kuma (self-hosted)                            |
| Agents           | Claude API (primary) · Ollama (fallback)                       |
| Orchestration    | LangGraph (stateful) · PydanticAI (structured outputs)         |
| Registry         | GHCR private `ghcr.io/chrysa/{repo}` — never public            |
| Docs             | MkDocs → GitHub Pages (`pages.yml`) · ADRs in `docs/adr/`       |
| Changelog        | git-cliff (`cliff.toml`) · Keep a Changelog                    |

## Non-negotiable conventions

- **Language**: English — all code, comments, docs, instructions, and config files.
- **Commits**: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`).
- **Branches**: `feature/`, `bugfix/`, `chore/`, `hotfix/`, `release/` · default branch `develop`.
- **Branch model — `main` is production, `develop` is the workspace.** Every repo runs the
  same two long-lived branches, and the mapping is literal, not decorative:
  1. **`main` = the code deployed in production.** It is a **protected branch**: no direct
     push, no force push, no branch deletion; every change arrives through a pull request.
     Reading `main` answers "what is running in prod right now" — nothing else is on it.
  2. **`develop` is the repository's default branch** (the GitHub default, what a clone
     checks out) and the integration target for all work. A repo whose default branch is
     `main` is a defect, not a variant.
  3. **Every feature/bugfix/chore PR targets `develop`.** `feature/x` → PR → `develop`.
     A feature PR opened against `main` is closed and retargeted.
  4. **The only way code reaches `main` is a pull request from `develop`** (or, for a
     production emergency, a `hotfix/` branch — which is merged back into `develop` in the
     same breath so the two never diverge). No other source branch may target `main`.
  5. **Production is triggered by a new release**, not by a merge: merging `develop` → `main`
     lands the code, and the deployment is driven by the tagged release (GitVersion tag +
     git-cliff changelog + the release workflow). No manual deploy from a laptop, no push
     that silently ships.
  Protection is configured, not assumed: `main` requires a PR, blocks force-push and
  deletion, and is machine-checked across the fleet by `scripts/audit-branch-policy.sh`.
- **Merge**: squash merge only · force push forbidden · auto-merge requires CI + owner.
- **One PR per issue**, scoped tight. Every PR references an issue (`Closes/Fixes/Refs #N`).
  Exception: label `hotfix`. The `enforce-issue-link` workflow is a blocking status check.
- **Repo provenance — every code repo depends on `project-init`.** A repository is
  **created by** the `project-init` / `chrysa-init` CLI (shared-standards) at birth **and
  kept in sync** with it thereafter: the scaffolded socle (Makefile contract, docs skeleton,
  this standards block, shared skills, CI templates) is re-applied by `distribute-standards.sh`,
  never hand-diverged. The socle is modulated by the `repos.yml` `runtime:` tier (application
  → full socle; `exempt:lib` / `exempt:native` → the relevant subset; pure `exempt:config` →
  standards block only, no application scaffold), but no code repo opts out. A repo that is
  neither scaffolded by nor kept in sync with `project-init` is a defect, not a variant.
- **Tests: pytest only** — assert-style test functions and `pytest-mock` (`mocker`
  fixture: `mocker.patch`, `mocker.AsyncMock`) for all mocking. The stdlib **`unittest`
  framework (`unittest.TestCase`) and `unittest.mock` imports are forbidden** — no
  `import unittest`, no `from unittest.mock import …`. See the `testing-pytest` skill.
- **Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later.** The
  *pytest only* rule governs Python; it never exempted the frontend from having tests.
  Network is mocked at transport level (MSW/fakes), behaviour is asserted through the
  accessible tree, and every fixed bug ships a regression test. E2E (Playwright) covers
  critical journeys only; **its gate status is declared per repo** in the local `CLAUDE.md` —
  fleet default is non-blocking. Detail: annexe `FRONTEND.md` §4, `TESTING.md`.
- **TypeScript is strict by contract.** `strict`, `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`,
  `useUnknownInCatchVariables`, `isolatedModules` are **all** enabled (plus
  `verbatimModuleSyntax` where the toolchain allows). No implicit `any`; `unknown` at
  boundaries; external data validated at **runtime** even when typed; contract types
  generated from OpenAPI/AsyncAPI, never hand-copied. One committed lockfile, frozen CI
  installs, no `latest` dependency. Detail: annexe `FRONTEND.md` §1.
- **React is a presentation layer, not the domain.** `domain/` and `application/` never
  import React; no `fetch`, browser storage, or vendor SDK in `domain/`. Components and hooks
  stay pure, props/state immutable, derived state computed rather than duplicated;
  `useEffect` synchronises with an external system and does not orchestrate business logic;
  `StrictMode` on for new apps. One API client singleton behind a service layer, one cache
  library for all server state, a root error boundary, and an explicit loading/error/empty
  triad per container. Anything outside the first meaningful paint loads lazily (split routes,
  `loading="lazy"` media, on-demand heavy components) behind a **shape-accurate placeholder**
  that reserves the final dimensions — a skeleton, not a spinner, so arrival shifts no layout.
  Detail: annexe `FRONTEND.md` §2–§3, §7.
- **Every repo declares its profile and DDD level** (`project_profile`, `ddd_level`,
  `bounded_context`, `standards_version`) — architecture is proportionate to business
  complexity, and small tools are not over-architected. Detail: annexe `ARCHITECTURE-DDD.md`.
- **Dark mode** mandatory from V1. **Accessibility** WCAG 2.1 AA — Lighthouse a11y score **≥ 90**,
  full keyboard navigation (Tab/Esc/visible focus), contrast ≥ 4.5:1 (3:1 large text), screen-reader
  tested on critical flows (signup, login, checkout).
- **UI state survives reload & focus** — human-facing surfaces persist their navigation
  and view state (active tab/section, selected sub-view, active context/filters) so a
  **manual reload keeps the current page** — the user lands exactly where they were, never
  reset to a default. Persist to `localStorage` (or the URL for shareable state), guarded
  by a validator that discards stale/removed values. Interface or state changes must
  **propagate across the app's own tabs/windows and on refocus/reload**: listen to the
  browser `storage` event and re-read on `window` `focus`, so a view opened while hidden
  never shows stale state after the user comes back. A reload that loses the user's place,
  or a change that fails to propagate on focus/reload, is a bug.
- **Notion logging**: every advancement and modification (progress, decisions, state
  changes) is logged in Notion — the single source of truth **for project state**. Run
  `@notion-sync` after any state change; on conflict about project state, Notion wins.
  This does **not** apply to the standards corpus: there the repo is the canon and Notion is
  a governance view (annexe `GOVERNANCE.md` GV-000).
- **Agent actions are governed.** Any feature where an agent *acts* (writes, calls, runs,
  changes state) needs a versioned manifest with typed I/O and a business owner, least
  privilege, a declared risk level R0–R5 with proportionate confirmation and dry-run,
  and a documented idempotency/timeout/limits/circuit-breaker/rollback envelope. Untrusted
  execution is sandboxed with network off by default; no agent auto-merges to `main`.
  Detail: annexe `AGENTIC-CAPABILITIES.md`.
- **Projects talk through versioned contracts only.** No import from a sibling repo, no path
  dependency, no submodule used as a runtime link, no access to another project's database or
  private models. Each consumer wraps the external contract in a local adapter and degrades
  cleanly when the provider is gone. Detail: annexe `PROJECT-DECOUPLING.md`.
- **Identity goes through the cluster SSO first.** Every interactive product deployed in the
  cluster integrates the **common cluster SSO** as its primary sign-in. The priority protocol is
  **OpenID Connect over OAuth 2.x** (SAML only where an enterprise context requires it), and the
  connection hierarchy is fixed: **1. cluster SSO → 2. external OAuth provider → 3. local
  account**. A local account is a fallback, never the default; where present it uses a modern
  password hash (argon2/bcrypt) and MFA is enforceable through the SSO. This does **not** break
  *projects talk through versioned contracts only* or *portable data*: identity sits behind an
  adapter, so the product stays independently deployable against an alternative identity provider
  (or a standalone local mode) by configuration, without touching the domain.
- **No hardcoded constants** in code — neither backend (Python) nor frontend (TS).
  All constants and config values (thresholds, business rules, labels, URLs, magic
  numbers) live in **external YAML files** and are loaded at runtime. Code reads them
  through a typed loader (Pydantic Settings backend · generated typed module frontend),
  never as inline literals. Only language-level enums (e.g. `status.HTTP_*`) are exempt.
- **No literal HTTP status codes — use the constants the framework already ships.** A bare
  `200`, `404`, `422`, `500` in code or in a test is forbidden; the value comes from the
  library that defines it: Python `fastapi.status.HTTP_404_NOT_FOUND` (or
  `http.HTTPStatus.NOT_FOUND` outside FastAPI), Django `HTTPStatus`, TypeScript a typed
  status enum/const from the HTTP client layer, C# `System.Net.HttpStatusCode`. This applies
  everywhere the code names a status — route decorators (`status_code=status.HTTP_201_CREATED`),
  raised errors, client-side branching, and **assertions in tests**
  (`assert response.status_code == status.HTTP_403_FORBIDDEN`). The same rule generalises: when
  a standard library or a framework already publishes the constant/enum for a protocol value
  (HTTP methods, MIME types, headers, signal numbers, exit codes), import it — never retype the
  literal. A magic number the reader has to look up is a defect, not a shortcut.
- **No code duplication — the second occurrence is an extraction order.** Copy-pasting a
  function, a fixture, a type, a config block, or a workflow step across files or repos is
  forbidden. The rule is mechanical: the **first** occurrence is code, the **second** is a
  factoring order — the logic moves to the transverse home for its kind and both call sites
  consume it from there. The homes are fixed: shared Python code → **`chrysa-lib`** (or the
  relevant `chrysa/*` library), CI logic → **`chrysa/github-actions`**, commit gates →
  **`chrysa/pre-commit-tools`**, standards/templates → **`shared-standards`**, UI components →
  the design system. Inside one repo, duplication is extracted to a shared module in the same
  layer — never re-typed in a sibling. Rewriting the same logic in different words does not
  make it a different implementation; a near-duplicate diverges silently and costs sixty PRs
  to fix once. Mechanisation: SonarCloud duplication ratio and `jscpd`-class detectors; a
  reported duplicate block is a defect to factor, not a warning to carry. Legitimate exception:
  a deliberate copy that decouples two projects on purpose (see *projects talk through
  versioned contracts only*) — documented as such, not left implicit.
- **Semantic URLs & code** — URLs are resource-oriented and human-readable: lowercase,
  hyphenated, plural-noun collections, no verbs or actions in the path (`GET /invoices/42`,
  never `/getInvoice?id=42`); REST shapes follow the `api-design` skill. Code is
  self-describing: intention-revealing names over comments, semantic HTML elements
  (`<nav>`, `<button>`, `<main>`, `<header>`…) never a `<div>` wired as a control, and
  ARIA used only to fill gaps native semantics cannot express.
- **URL-addressable frontend navigation — mandatory.** Every navigable view/route/tab/
  detail is a **real, semantic URL** (`/projects/42/settings`, not `/#` or a modal with no
  address). Navigating **must change the URL** via the router (History API `pushState`), so:
  1. the change is **recorded in browser history** — Back/Forward move between views, never
     trap or reload the app;
  2. a link is **right-clickable / middle-clickable / ⌘-clickable → open in a new tab**, which
     means it is a genuine `<a href>` (or the router's `<Link>`), **never** a `<div>`/`<button>`
     with an `onClick` that only mutates state;
  3. the URL is **deep-linkable & shareable** — pasting it in a fresh tab lands on the exact
     same view (route params + query for filters/selection/pagination), reproducible without
     prior in-app state.
  Ephemeral UI (transient toasts, open/closed of a purely local menu) may stay stateless, but
  anything a user would bookmark, share, or reload into is a route. This complements
  *UI state survives reload & focus*: persisted view-state that has an addressable identity
  belongs in the URL, not only `localStorage`.
- **Python packaging — `pyproject.toml` is the single source of truth.** `setup.py` and
  `setup.cfg` are **forbidden** for Python packaging (`setup.cfg` allowed only for non-Python
  tooling, e.g. uwsgi). Build backend is **`setuptools`** (never `hatchling`). All tool config
  (`ruff`, `mypy`, `pytest`, `coverage`) lives in `[tool.*]` — external `ruff.toml`, `mypy.ini`,
  `pytest.ini` are forbidden. Distributed libraries use a `src/` layout and follow the Public API
  Contract (`docs/PUBLIC-API-CONTRACT.md`): sorted `__all__`, relative imports in `__init__`,
  `__version__` via `importlib.metadata`, uniform `install()` entrypoint, shared types in `chrysa-lib`.
- **Python is written object-oriented, one class per file.** Behaviour is carried by classes,
  not by a bag of module-level functions sharing state through globals or long parameter
  lists: a cohesive responsibility (a service, a repository, an adapter, a use case, a value
  object) is a **class**, dependencies are injected through `__init__`, and state lives on
  the instance. **One class per module, and the module is named after it** —
  `vehicle_dispatcher.py` holds `VehicleDispatcher`, and nothing else of substance (private
  helpers of that class and its own exception types may live beside it). Method order inside
  a class is fixed: dunder → property → abstract → classmethod → staticmethod → public →
  private, alphabetical within each group. Pure functions remain legitimate where there is
  genuinely no state and no variation point — a stateless transformation, a validator, the
  functional core called by the class — and Pydantic models, dataclasses, enums and
  protocols are classes already. What is forbidden is a `utils.py` grab-bag, a module of
  loosely related procedures threading the same objects through every signature, and two
  unrelated public classes sharing one file.
- **Import the item, not the module — `from x import y; y()`.** Python imports name the
  symbol actually used (`from fastapi import status`, `from datetime import datetime`,
  `from app.services.billing import BillingService`), so call sites read `datetime.now()`
  and `BillingService(...)`, not `datetime.datetime.now()` or a chain of package prefixes.
  Bare `import x` is reserved for the cases where it is genuinely better: a module used as a
  namespace whose name carries meaning at the call site (`import numpy as np`,
  `import json`), or breaking an import cycle. **Forbidden**: wildcard `from x import *`,
  relative imports beyond a package's own `__init__` re-exports, and importing a module only
  to reach one attribute through it. Imports sit at module top level (never inside a function
  except to break a cycle, and that is commented), and are ordered/deduplicated by Ruff
  (`I` rules) — the linter owns the ordering, no hand-sorting.
- **Everything is machine-agnostic and portable — no rule, repo, or script is bound to one
  machine.** A standard, a Makefile target, a script, a hook, a compose file, or a CI job must
  behave identically on any developer machine, any runner, and the server, with nothing but a
  clone and the sanctioned host tools. Concretely, **forbidden**: absolute paths tied to a user
  or host (`/home/<user>/…`, `/Users/<name>/…`, `C:\Users\…`, a hardcoded workspace root), a
  hostname/IP/mount point of a specific box baked into code or config, an assumption that a tool
  was installed a particular way, and "works because my machine has it" reasoning. Instead:
  paths are relative to the repo root (or resolved from `$(git rev-parse --show-toplevel)` /
  the script's own directory), machine-specific values arrive through **environment variables
  with documented defaults** (`.env.example` committed, `.env` never), and anything the code
  needs is provided by the container image. The same portability applies to the standards
  corpus itself: a rule names a *mechanism* (a hook id, a Makefile target, a workflow), never a
  particular machine, user account, or local directory layout. The test is mechanical: a fresh
  clone on an unknown machine, with git + Docker + pre-commit, must reach a green
  `make ci` — if it needs a manual step that only the owner knows, that is a defect.
- **External dependencies are installed in containers, never on the host.** A project's
  runtime dependencies — language packages (pip/npm/cargo/nuget), databases, brokers, caches,
  system libraries, compilers, CLIs a service shells out to — are declared in the image
  (`Dockerfile`) or in a compose service, and installed **inside the container**. `sudo apt
  install`, `pip install` into the system interpreter, a global `npm -g`, or a locally
  installed Postgres/Redis "to make it work" are **defects**: they make the machine the
  environment, so the build is unreproducible, the version drifts per-machine, and CI and prod
  no longer run what the developer ran. A missing dependency is fixed by editing the image,
  never by installing it on a developer machine. Three sanctioned host tools only, all repo-independent
  and installed **outside** any project tree: **git**, **Docker** itself, and the commit gate
  (`pipx`/`uv install pre-commit`, which provisions its own hook envs — see *the gate is
  host-native*). Everything else runs through `docker compose run` / the `make docker-*`
  targets. Host-bound repos (`exempt:native`: desktop, hardware, editor extensions) are the
  documented exception, and only for the part genuinely bound to the host OS.
- **No virtualenv in a repo — ever.** `venv/`, `.venv/`, `env/` are **forbidden** inside a
  project tree. Python runs in the Docker image (deps baked into the image layer, or a named
  volume for editable installs). A committed or on-disk virtualenv is a bug, not a setup step.
  The only sanctioned local Python is a **uv/pipx tool env stored outside the repo** (e.g.
  `~/.local`, `$UV_CACHE_DIR`), never a folder living next to the source.
- **Tool caches & deps never touch the project tree.** `__pycache__`, `.pytest_cache`,
  `.ruff_cache`, `.mypy_cache`, `.benchmarks`, `node_modules`, and pip/npm/uv download caches
  are regenerable machine artifacts — they must be **invisible in the repo working copy**.
  Enforcement is three-layered and all three are mandatory:
  1. **`.gitignore`** carries the managed canonical block (`templates/gitignore.canonical`) so
     they are never tracked. Appended, not hand-maintained.
  2. **Docker caches live in named volumes**, and every cache-dir env var points **outside**
     the bind mount so nothing is written back into the mounted source:
     ```yaml
     # docker-compose: a container that bind-mounts the repo
     services:
       tests:
         user: "${UID:-1000}:${GID:-1000}"   # host UID — NEVER `user: root`
         environment:
           PYTHONPYCACHEPREFIX: /caches/pycache
           RUFF_CACHE_DIR: /caches/ruff
           MYPY_CACHE_DIR: /caches/mypy
           PYTEST_ADDOPTS: -p no:cacheprovider  # or PYTEST_CACHE_DIR under /caches
           npm_config_cache: /caches/npm
         volumes:
           - .:/code
           - tool-caches:/caches          # named volume, persists across runs
           - node-modules:/code/node_modules   # deps in a volume, shadowing the mount
     volumes:
       tool-caches:
       node-modules:
     ```
  3. **Any container that bind-mounts a repo runs as the host UID** (`user: "${UID}:${GID}"`),
     **never `user: root`** — root-owned artifacts written into a bind mount are unremovable
     without `sudo` and are treated as a defect. Root user is allowed only for containers with
     **no** repo bind mount (e.g. `.:/code` absent).
  Regenerable artifacts already in a repo are purged with `scripts/purge-artifacts.sh`.
- **Every tracked file and folder must earn its place — a repo holds only what is useful to it
  now.** A repository contains its own source, its tests, config that is actually loaded, docs
  that are current, and the templates it distributes — nothing else. Forbidden in the working
  tree and in git:
  1. **Superseded or archived documents** whose useful content has been folded elsewhere. Git
     history *is* the archive — a file that "governs nothing", an "undistributed annex kept for
     detail", or a `*_OLD` / `*_backup` copy is deleted, not retained "just in case". Recovering
     it is one `git show` away.
  2. **Scratch and one-off notes** — sprint notes, exported Notion/wiki pages, meeting dumps,
     session scratch. Ephemeral state lives in the tracker (Notion is the source of truth), never
     committed to the repo.
  3. **Stray assets** — diagrams, images or files unrelated to *this* repo's own product (a
     portfolio-wide diagram belongs in the portfolio repo, not a library).
  4. **Idea stubs for projects that live elsewhere** — a placeholder README for a future/other
     project is drift; the project gets its own repo when it starts.
  5. **Generated reports that are not a CI baseline** — an audit/report output is gitignored, not
     committed. Only a file diffed by CI as a drift baseline (e.g. `*.baseline`) is tracked.
  The test is mechanical: a file that governs nothing, is loaded by nothing, and is read by no
  current reader does not belong — delete it. When a deletion would leave dangling references,
  the references are repointed in the same change, never left broken. Checked in PR review; a
  file that fails the test is a defect, not clutter to tolerate.
- **Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory.** Every
  application Dockerfile uses named build stages so a single file yields both runtime and
  developer images (`docker build --target production` / `--target dev`). Minimum stages:
  a shared `base` (interpreter + OS deps), a `builder`/`deps` (compiles/installs dependencies),
  a **`production`** target (slim runtime — no dev tooling, non-root `USER`, only the built
  artifact), and a **`dev`** target (production + test/lint/debug tooling, editable install,
  live-reload). A single-stage Dockerfile, or one missing either `production` or `dev`, is a
  defect. Compose services select the target explicitly (`build.target: production|dev|tests`).
  Canonical shape + Python 3.14 example: the `dockerfile-multistage` skill.
  *Exemption — container-collection repos:* a repo whose product **is** a set of standalone
  utility/tool container images (e.g. `usefull-containers`), not one application, is exempt from the
  `production`+`dev` two-stage rule per image — each image is single-purpose. Such images still must
  not embed a reverse proxy and still run as non-root where they bind-mount host paths.
- **App containers ship the app only — the platform layer is the owner's responsibility.** An
  application image/container **never embeds a reverse proxy** (nginx/Traefik/Caddy/HAProxy as a
  TLS-terminating or routing front). The app container exposes its own port and speaks plain HTTP;
  routing, TLS, virtual hosts, and load-balancing live in the **platform layer** (the owner's
  Nginx/Traefik + Certbot on the host, or `deploy/k8s/` ingress), out of the app image. A static
  frontend may use a minimal internal web server to serve its own built assets, but it does **not**
  proxy other services. Baking a reverse proxy into an app container is a defect (couples the app to
  infra, duplicates the platform, and breaks the ownership boundary).
- **Dev stage must hot-reload.** The `dev` target/service provides live auto-reload so a source edit
  is reflected without a manual rebuild/restart: backend `uvicorn --reload` (or the framework's
  autoreload), frontend the dev server with HMR (`vite`/`npm run dev`), watched via the compose
  `develop.watch` sync or a source bind mount. A `dev` image identical to `production` (no reload) is
  not a dev image. Mechanised by the `compose-dev-hot-reload` hook
  (`chrysa/pre-commit-tools`): a compose service targeting the `dev` stage with neither a bind
  mount nor a `develop.watch` sync action is flagged at commit time.
- **`.dockerignore` mandatory & exhaustive** — at minimum `.git`, `node_modules`, `__pycache__`,
  `.env*`, `*.log`. Base images pin an explicit version or digest (never a bare `FROM …:latest`);
  no secret in build args or image layers (BuildKit secrets or runtime env only). Every application
  Dockerfile declares a `HEALTHCHECK`, and compose services set `restart: unless-stopped`.
- **Setup wizard & config panel** (deployable web apps/services — not libs, CLIs, utilities). A
  first-run **setup wizard** (CLI or web) covers DB, admin user, integrations, secrets and locale;
  it is **idempotent**, detects missing prerequisites with explicit fixes, and offers a CI skip
  (`SETUP_NON_INTERACTIVE=1`). On missing/invalid config at startup or runtime, the app **redirects
  to `/setup`** rather than crashing or showing a generic error. An admin **configuration panel**
  (auth-gated CRUD API) manages runtime config with a versioned audit trail, hot-reload where
  possible (else a `RESTART_REQUIRED` flag), and JSON export/import for backup and cross-env cloning.
- **A floating assistant where it earns its place — never as decoration.** Any human-facing
  product whose users face a **non-obvious surface** (a dense cockpit, a multi-step form or
  wizard, a query/graph/config console, an admin panel with domain jargon) ships an **in-app
  floating assistant**: a persistent, dismissible affordance that answers "what am I looking
  at / what do I do next" **in context**, without leaving the page. The value test comes
  first — a product with two screens and no jargon does not get one, and shipping an empty
  chat bubble is worse than shipping nothing. Where it is warranted, it obeys the same rules
  as the rest of the app:
  1. **Context-aware, not a generic chat box** — it receives the current route, selection and
     visible state, and its opening move is a useful suggestion about *this* screen.
  2. **Opt-in and reversible** — off by default behind a documented flag/config key
     (`ASSISTANT_ENABLED`-style), dismissible, and its position/open state persists per user
     (see *UI state survives reload & focus*). It never steals focus, never blocks the
     underlying surface, and never auto-opens on every visit.
  3. **Governed like any agent** — read-only Q&A is R0/R1; the moment it *acts* (writes, calls,
     runs, changes state) the full agentic envelope applies: versioned manifest, typed I/O,
     least privilege, risk level with proportionate confirmation and dry-run, audit trail.
     Detail: annexe `AGENTIC-CAPABILITIES.md`.
  4. **Provider-independent** — inference goes through the local port with ≥2 tested adapters
     (strategic pillar 1); no vendor SDK in the product's business code, and the assistant
     degrades to a documented help panel when no model is reachable.
  5. **Accessible and quiet** — reachable and closable by keyboard (visible focus, `Esc`
     closes), announced to assistive tech, honours `prefers-reduced-motion`, and respects the
     WCAG 2.1 AA + design-token rules like every other surface. It is lazily loaded behind a
     shape-accurate placeholder so it never delays first paint.
  6. **Scoped and honest** — it answers from the product's own data and docs, says "I don't
     know" rather than inventing, and states what it did after acting.
  A desktop/overlay assistant (the `floating-agent` pattern) follows the same rules outside the
  browser: overlay-only, dismissible, no capture of surfaces the user did not consent to.
- **The repository architecture is legible to an agent — optimised for Claude, not only for
  humans.** An AI agent reads a repo through a narrow window: it cannot skim thirty files to
  infer a convention. So the layout itself carries the answers, and a repo where an agent has
  to guess is a defect.
  1. **One entry point that says what to do now** — `CLAUDE.md` (repo-specific rules, layered
     over the inlined standards block) plus `primer.md` (current state, next action), read
     before anything else. `AGENTS.md`/`copilot-instructions.md` stay generated from the same
     source, never hand-diverged.
  2. **Every non-trivial folder carries a `README.md`** stating role, structure, what belongs
     in it and — critically — **what must not**, so a file lands in the right layer at write
     time instead of in review.
  3. **Predictable, name-addressable structure** — layers named after the architecture
     (`domain/`, `application/`, `infrastructure/`, `interfaces/`), one class per file with
     the module named after it, test file mirroring the source path. Finding *where* something
     lives is a naming derivation, never a search.
  4. **Small units by contract** — the file/function/complexity gates (500 / 50 / 10) exist so
     a unit fits in one read; the same reason bans god-objects and `utils.py` grab-bags.
  5. **Machine-readable seams** — typed signatures, Pydantic/OpenAPI contracts, YAML config
     with a typed loader, `docs/adr/` for the *why*. An agent should be able to answer "what
     breaks if I change this" from types and contracts, not from tribal memory.
  6. **Task-shaped tooling over prose** — the repeatable operations are `make` targets and
     shared skills (`.claude/skills/`), so an agent invokes a named contract instead of
     reconstructing a command line. Every documented command exists in the Makefile.
  7. **Session continuity** — decisions, known issues and progress live in `.claude/memory/`
     (see *Session lifecycle*), so the next session starts from state, not from scratch.
  The test is mechanical: drop a fresh agent in the repo with no conversation history — it
  must find the entry point, the layer to touch, the command to run and the gate to pass,
  from committed files alone.
- **Raised errors are typed** — in any language whose type system allows it. Code raises a
  **domain-specific exception class** (Python: a module `…Error(Exception)` hierarchy rooted in one
  base per bounded context; TypeScript: `class XError extends Error` with a discriminant field, or a
  typed `Result`/`Either`; C#: a derived `Exception`). **Forbidden**: raising a bare `Exception`/
  `RuntimeError`/`Error`, `throw "string"`, `throw {code: …}` object literals, or signalling failure
  by a magic return value (`None`/`-1`/`false`) where an error type is expressible. Catch sites match
  the narrowest type (`except ValidationError`, never bare `except:`/`except Exception` outside a
  top-level boundary), and every error carries a stable machine-readable code plus a message that
  says what to do. The public error taxonomy of a module is part of its contract — documented and
  versioned like its signatures. Detail: the `error-handling` skill.
- **Failures are contained, and observable.** A *local* error must not become a *global* one: a
  failing dependency, task, or request is isolated so the rest of the system keeps serving.
  Beyond the type + stable `code`, an error carries the taxonomy fields it needs to be triaged —
  `category`, `severity`, `retryable`, `scope`, a `correlation_id` threading it across services,
  and both a user-facing and an operator-facing message. Every outbound call has an explicit
  **timeout** and **bounded retries** (never an unbounded retry loop); a repeatedly-failing
  dependency is fronted by a **circuit-breaker**, and independent workloads by a **bulkhead**, so
  one saturated path cannot drown the others. Errors are emitted to the shared observability
  backend (**Mirador** or a compatible one), correlation id included, not just written to a local
  log. A surface's Definition of Done includes its error paths, not only its happy path.
- **Prefer a lookup table to a state machine.** Branching on a value — dispatch, routing, parsing,
  handler/strategy selection, enum → behaviour, status → transition — is expressed as a **hash
  table** (`dict`/`Record`/`Map`) from key to handler or value, **not** as an `if/elif` ladder, a
  `switch`/`match` cascade, or a hand-rolled state machine with a `self._state` variable. The
  mapping is data: declared once, typed (`dict[Status, Handler]`), exhaustive over the key domain
  (checked by the type system or a test), and extended by adding a row — never by editing control
  flow. This keeps cyclomatic complexity flat and makes every branch independently testable. An
  explicit state machine is legitimate only when the transitions genuinely carry state-dependent
  semantics no table can express (concurrent protocol, long-running workflow, parser with a stack);
  choosing one is a documented decision, and even then transitions themselves live in a
  transition **table**, not in nested conditionals.
- **Decompose into small, independently unit-testable methods.** A function does one thing at one
  level of abstraction; anything with its own name, branch, or rule is extracted so it can be
  called and asserted **in isolation, without I/O, without mocks of the whole world**. Concretely:
  pure business rules are separated from orchestration and from I/O (compute in a pure function,
  side effects at the edges), so a test needs no DB/HTTP/filesystem to exercise the rule; a private
  helper that is hard to test in isolation is a signal the seam is in the wrong place, not a reason
  to skip the test. This is what makes the *max function lines 50* / *complexity ≤ 10* gates
  achievable rather than gamed, and it is the mechanism behind the coverage floor: coverage reached
  only through end-to-end paths, with untestable god-functions underneath, does not satisfy this rule.
- **Basic optimisations and known anti-patterns are caught in review and in CI.** Code is written
  correct-then-obvious first — **no speculative micro-optimisation**, no premature caching, no
  hand-tuned trick without a measurement (profile before optimising; `perf` claims come with
  numbers). But the *basic* wins are non-negotiable because they are algorithmic, not clever:
  1. **Right data structure** — membership test on a `set`/`Map` (O(1)), not a linear scan of a list;
     index/dict lookup instead of a nested loop (O(n²) over a joinable key is a defect);
     a single pass instead of repeated traversals of the same collection.
  2. **No work in a loop that is loop-invariant** — hoist the constant computation, the compiled
     regex, the config read, the connection setup.
  3. **No N+1** — database queries and network/API calls are batched or eager-loaded
     (`selectinload`/`joinedload`, bulk endpoints); a query inside a `for` over rows is a defect.
     Frontend equivalent: no request per list item, no re-render per keystroke without debounce,
     no unmemoised derived state recomputed on every render.
  4. **Bounded resources** — no unbounded `SELECT *` / unpaginated list endpoint, no full-file read
     of arbitrary-size input (stream it), explicit timeouts on every outbound call, connections and
     file handles closed via context managers.
  5. **Known anti-patterns are named and rejected**: god object/function, copy-paste duplication
     (factor into `chrysa-lib` — see *no code duplication*), boolean trap parameters, primitive
     obsession over a value object, deep nesting (guard clauses instead), mutable default arguments,
     shared mutable global state, silent `except: pass` (see *typed errors*), stringly-typed domains,
     circular imports, and dead code kept "just in case" (git is the archive).
  Mechanisation: Ruff (`C901`, `PLR*`, `B`, `SIM`, `PERF`, `RUF`) + Mypy on Python, ESLint
  (`complexity`, `no-await-in-loop`, `react-hooks/exhaustive-deps`) on TS, SonarCloud rating **A**
  with 0 hotspot on both. A finding here is a defect to fix, not a warning to carry.

## Quality gates

- Test coverage **>= 85%** by default. A repo may override upward, never below 80%.
- Lint warnings: **0**. Mypy clean. SonarCloud rating **A**, 0 security hotspot.
- Max function lines 50 · max file lines 500 · cyclomatic complexity heuristic <= 10.

## Design system

Every human-facing surface is built from a shared design system — no ad-hoc style values in
components. This complements *dark mode + WCAG 2.1 AA* and the `ui-ux` skill.

- **Design tokens are the single source of style** — colours, typography, spacing, radii,
  shadows, z-index live as tokens (JSON/CSS vars) consumed by code. **No** hardcoded style
  literals in components (mirrors *no hardcoded constants*).
- **Versioned brand kit** — primary/secondary/semantic palette, **≤ 2 type families**, logo
  (variants + clear space), one icon set. Defined and versioned, not per-repo reinvented.
- **Living component library** — reusable components with documented states and variants
  (Storybook or equivalent); one canonical implementation per component.
- **Systematic spacing scale & grid** — spacing on a fixed scale (4/8 px base), shared grid
  and breakpoints; no arbitrary margins.
- **Defined type hierarchy** — explicit type scale (size, weight, line-height, tracking) with
  named roles (`display/title/body/caption`), never ad-hoc sizes.
- **Systematic interaction states & feedback** — every interactive element exposes
  hover/focus/active/disabled; every action gives visible feedback (< 100 ms); visible keyboard
  focus is mandatory.
- **Consistent UX writing** — voice-and-tone guide; error messages say what to do (no raw
  codes); action-oriented labels and CTAs; terminology aligned to the domain glossary.
- **Standardised motion** — tokenised durations and easing (e.g. 150/250 ms); animation is
  functional (state transition, feedback), never gratuitous; honours `prefers-reduced-motion`.
- **Mobile-first responsive** — mobile-first design, breakpoints from tokens, touch targets
  **≥ 44 px**, no fixed widths.
- **Design ↔ dev handoff contract** — design ships exported tokens, component specs (measures,
  states, behaviours) and edge cases; dev consumes the tokens, never redefines the values.

## Makefile targets

- **Referential**: `Forge-Stack-Workshop/base-makefile` (`Makefile.basic`, `Makefile.python`,
  `Makefile.with-sub-folder`) is the single source of truth for target names and behaviour.
- **Canonical naming** — follow base-makefile verbatim, one word where it is one word:
  `typecheck` (**never** `type-check`), `test-cov`, `format-check`, `quality-gate-verify`,
  `docker-test`, `ci`. Renaming or aliasing a canonical target is forbidden.
- **Mandatory socle** — every application repo MUST expose, with these exact names and intent:
  `help install install-dev lint format format-check typecheck test test-cov pre-commit clean
  ci quality-gate-baseline quality-gate-verify`. Non-applicative repos (pure infra/Helm/Terraform,
  config-only, docs) are exempt from the language-specific targets (`typecheck`, `test-cov`) but
  still expose `help lint pre-commit clean`.
- **Docs must match** — every `make <target>` cited in `CLAUDE.md` or `README.md` MUST exist in
  the Makefile (no `make type-check` when the target is `typecheck`).
- **Recipe style** — prefix every recipe line with `@`; add `## Description` after each target so
  it appears in `make help`.
- **Modular Makefiles — 500 lines max, split by domain.** No hand-maintained Makefile exceeds
  **500 lines** (the same file gate as code). Approaching the limit, it is split into thematic
  files under `make/` (`make/common.mk` for shared variables/functions, then `docker.mk`,
  `test.mk`, `quality.mk`, `k8s.mk`, `docs.mk`… as the repo needs), loaded explicitly from the
  root Makefile with `include` / `-include`. The **root Makefile stays an entry point and an
  orchestrator**: it exposes the main commands, loads the thematic files, and serves the global
  `make help`. A target exists **in exactly one file** — duplicates, near-identical variants and
  copy-paste between thematic files are forbidden (*no code duplication* applies to Make too).
  Inclusion is acyclic: a thematic file never includes back into its parent. Target names stay
  predictable and grouped by domain (`test-unit`, `docker-build`, `k8s-deploy`), every public
  target is documented in `make help` from its `## Description`, and any long or business-logic
  recipe moves to a **versioned, testable script** — the Makefile is a command surface, not an
  application language.

## Container-runtime policy

A project runs **only in a container** unless its nature genuinely forbids it. Convenience, "easier
on the host", or "it's just a script" are **not** exemptions — when in doubt, classify `container`.
Every repo carries a `runtime:` field in `repos.yml`, machine-checked by `audit-docker-compliance.sh`:

- `container` — runs as a service. Provides Dockerfile(s) + `docker-compose*` + `HEALTHCHECK` +
  `docker-up`/`docker-down`/`docker-test` targets.
- `exempt:lib` — distributed/imported (library, plugin, pre-commit hook, GitHub Action, CLI). Runs
  in the consumer's environment; provides a `docker-test` target (CI runs the suite in a container).
- `exempt:config` — no executable runtime (config, knowledge base, deploy manifests). Nothing to run.
- `exempt:native` — bound to a host OS, device, cloud platform, or editor (desktop integration,
  hardware, Apps Script, VS Code extension, infra/Helm). Optional `Dockerfile.test` for CI.
- `pending` — pre-code scaffold; flips to `container` at first code.

## Release & changelog config (canonical)

- **Versioning** is GitVersion (`GitVersion.yml`, flat `mode: ContinuousDeployment`) — never bump
  manually. Legacy v5 schemas (`GitHubFlow`, no top-level `mode:`) are incompatible and must be
  **replaced**, not version-bumped.
- **Changelog** is generated by git-cliff (`cliff.toml`), Keep a Changelog format.
- `GitVersion.yml` and `cliff.toml` are **canonical files** with a single source of truth in
  shared-standards (repo root + byte-identical `templates/` copy). A `repo: local` pre-commit hook
  (`gitversion-canonical-drift`, `cliff-canonical-drift`) blocks drift; `audit-canonical-conformance.sh`
  audits the fleet.
- **Docs** live in `docs/` (MkDocs), deployed to GitHub Pages via `pages.yml`. `README.md` reflects
  the actual current state and is updated on each release.
- **Registry** — application images publish to **private GHCR** (`ghcr.io/chrysa/{repo}`, tags mirror
  the git tag + `:latest`); CI authenticates with the workflow `GITHUB_TOKEN` (or least-privilege
  `packages:write`), never a plaintext PAT. Distributable libraries publish to public PyPI via
  Trusted Publishing (OIDC), never a token in plaintext.

## GitHub Actions (reuse first · custom actions centralised · thin workflows)

CI is assembled from **existing actions**, not written. A workflow is glue — checkout,
setup, invoke the repo's own gate (`pre-commit`, `make ci`) — and every line of logic it
carries is a line that lives in the wrong repo.

- **Reuse before writing — always.** The first choice is a **maintained public action**
  (`actions/checkout`, `actions/setup-python`, `actions/setup-node`, `astral-sh/setup-uv`,
  `docker/build-push-action`, `SonarSource/*`, `pypa/gh-action-pypi-publish`, …).
  Re-implementing in a `run:` block something a maintained action already does — caching,
  toolchain setup, publishing, artifact upload — is a defect. Preferring a hand-rolled
  script because "it's shorter" is not a reason.
- **The only home for chrysa-specific actions is `chrysa/github-actions`.** When no public
  action fits, the behaviour becomes a composite action / reusable workflow in that repo
  (`python-setup`, `ruff-check`, `run-tests`, `sonar-scan`, `publish-python-package`, …)
  and consumers reference it: `uses: chrysa/github-actions/<action>@<rev>`. Reusable
  workflow templates live in `shared-standards/workflows/` and are distributed, never
  hand-forked.
- **Repo-local actions are forbidden by default.** No `.github/actions/**` composite in a
  product repo, no inline bash beyond glue, no `scripts/ci-*.sh` that exists only to be
  called by a workflow. The **second occurrence of the same CI logic anywhere in the fleet
  is an extraction order**, not a copy: it moves to `chrysa/github-actions` and both repos
  consume it. A repo-local action is tolerated only as a short-lived spike, with an issue
  tracking its migration.
- **Keep the code minimal.** A job step is a `uses:` or a one-line `run:`. A `run:` block
  past ~15 lines, or any conditional/parsing/retry logic, does not belong in YAML — it
  becomes a tested entrypoint inside the action repo (Python preferred, testable), not a
  heredoc. Duplicated near-identical jobs collapse into a `strategy.matrix`; shared setup
  collapses into a composite action. Workflow YAML is not a programming language and is
  not covered by any test.
- **Pinning & permissions.** Third-party actions are pinned by **commit SHA** (with the
  version in a trailing comment); `chrysa/github-actions` and `actions/*` by tag.
  Workflows declare least-privilege `permissions:` (read by default, `packages:write` /
  `contents:write` only on the job that needs it), never a plaintext PAT where the
  workflow `GITHUB_TOKEN` or OIDC works. Dependabot keeps the `github-actions` ecosystem
  up to date.
- **Secrets are passed explicitly — `secrets: inherit` is banned.** A reusable workflow
  receives only the secrets it actually uses, named one by one under `secrets:`
  (`secrets: {SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}}`). `secrets: inherit` hands the
  callee the caller's entire secret store, so a compromised or careless step reaches
  credentials it was never meant to see, and no one can tell from the call site which
  secrets a workflow consumes. The same rule applies to steps: scope `env:` to the step
  that needs the value, never to the job or the workflow when a single step uses it. A
  workflow whose secret list is not readable at the call site is a defect.

## Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)

The enforcement engine is **[pre-commit](https://pre-commit.com/)** itself, configured
in `.pre-commit-config.yaml`. pre-commit is the authoritative runner; `make lint` /
`make pre-commit` may exist as thin convenience aliases, but a hook that only runs
through `make` is a defect — every hook MUST be runnable via `pre-commit run` directly,
and CI invokes `pre-commit`, not `make`.

- **Every git hook goes through the framework — no hand-rolled hooks.** A repo's hooks are
  declared as pre-commit hook ids in `.pre-commit-config.yaml` and installed by
  `pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push`.
  Hand-written scripts committed under `.git/hooks/` or a repo-local `hooks/` wired via
  `core.hooksPath`, alternative runners (**husky**, **lefthook**, **overcommit**, npm
  `prepare` hook installers), and checks reachable only through `make` or a bespoke
  `scripts/*.sh` are **forbidden**: a gate that is not a pre-commit hook id is not
  discoverable, not pinned, not skippable per-hook (`SKIP=`), and not runnable in CI the
  same way. A repo-specific check is a `repo: local` hook in the config (or a hook published
  by `chrysa/pre-commit-tools`), not a script bolted onto git. The single sanctioned
  exception is the host-global pre-push (`dotfiles/git-hooks-global/pre-push`), which is
  machine-level, not repo-level, and itself only invokes `pre-commit`.
- **The gate is host-native — no strong coupling to the project's containers.** pre-commit
  runs with only `pre-commit` installed on the host (via `pipx`/`uv`, outside any repo); it
  provisions each hook's isolated environment itself (`~/.cache/pre-commit`), so a commit
  needs **no project image and no running container**. Local hooks are `language: system` /
  `python` (or another native language) invoking **host** tools — **never** `docker compose
  run`, and `language: docker` / `language: docker_image` is **forbidden**. A check that
  genuinely needs the project image (Django settings, a DB, a compiled tool) **degrades gracefully on the host**:
  it probes for the tool and skips with a message when absent
  (`command -v <tool> >/dev/null 2>&1 && <run> || echo 'skipping — runs in CI/Docker'`),
  it does **not** spin up a container. Container-side enforcement is CI's job; locally the
  gate is best-effort and never blocks on the Docker daemon being up. This does not
  contradict the container-runtime policy — the *application* runs in a container; the
  *commit gate*, like git, is a host tool.
- **Two stages, two scopes — do not mix them:**
  - **commit stage** (`pre-commit run`, default): auto-fixers + fast lints —
    `ruff`, `end-of-file-fixer`, `trailing-whitespace`, `detect-secrets`/`gitleaks`,
    `conventional-pre-commit` (commit-msg), `no-commit-to-branch --branch main`.
    These **mutate** the tree, so they only ever run over the staged/committed diff.
  - **pre-push stage** (`pre-commit run --hook-stage pre-push`): only hooks tagged
    `stages: [pre-push]` (e.g. `regression-gate` from `chrysa/pre-commit-tools`), run
    **natively over the pushed commit range** (`--from-ref <remote>` `--to-ref <local>`).
    A push **verifies, it never mutates** the tree.
- **Forbidden at push time:** `make lint`, and `pre-commit run --all-files`. Running the
  full tree at push re-executes commit-stage **auto-fixers** on unrelated files, mutates
  them, exits non-zero, and **rejects the push over a pre-existing defect in a file you
  never touched**. `--all-files` belongs to CI (where a mutation surfaces as a diff) and
  to a deliberate local audit — never to the push gate.
- **The global pre-push hook** (`dotfiles/git-hooks-global/pre-push`) mirrors pre-commit's
  own installed pre-push hook: it runs the `pre-push` stage over the range only, then the
  SonarCloud quality gate. No `make`, no `--all-files`, no tree mutation.
- **The shared hook package is Docker-free by construction.** `chrysa/pre-commit-tools`
  — the hook-decentralisation package the whole fleet consumes — publishes every hook as
  `language: python` (or another native pre-commit language) with its dependencies declared
  in the hook definition. **Forbidden in that package:** `language: docker`,
  `language: docker_image`, and any `docker` / `docker compose` invocation inside a hook
  entrypoint. A published hook MUST run identically on a host where Docker is not installed
  at all; if a check cannot work without the daemon, it is a CI job, not a hook. This keeps
  the fleet gate installable with a single `pipx install pre-commit` and immune to the
  daemon being down.
- Hooks are **pinned by `rev`**; shared hooks come from `chrysa/pre-commit-tools`.
  `detect-secrets`/`gitleaks` respect the repo's secret allowlist.
- **Hook logic is centralised in `chrysa/pre-commit-tools` — `repo: local` is glue only.**
  Every gate is declared in `.pre-commit-config.yaml`, and any hook carrying real logic
  is published as a versioned hook id in `chrysa/pre-commit-tools`, consumed by `rev`.
  `repo: local` is reserved for genuinely repo-specific glue (a path check tied to this
  repo's layout) and stays a few lines; it is never a home for a check other repos could
  want. As with GitHub Actions, the **second occurrence of the same hook anywhere in the
  fleet is an extraction order**, not a copy: it moves to `chrysa/pre-commit-tools` and
  both repos consume it from there. A hook duplicated across repos cannot be fixed once,
  drifts silently, and is the reason a fleet-wide rule change costs sixty pull requests
  instead of one.

## Shared skills (load on demand from shared-standards/.claude/skills/)

- `testing-pytest` — pytest DDD + pytest-mock + constants (writing tests)
- `dockerfile-multistage` — 4-stage Python 3.14 containers (editing Dockerfile)
- `api-design` — REST standards + FastAPI patterns (designing endpoints)
- `async-patterns` — async FastAPI + SQLAlchemy async sessions (async code)
- `clean-architecture` — FastAPI module/layer structure (adding a feature)
- `error-handling` — FastAPI errors + Sentry + logging (handling errors)
- `contract-testing` — library contract / breaking-change tests (@chrysa/* releases)
- `agent-patterns` — LangGraph + PydanticAI + Claude API (building agents)
- `ui-ux` — UX/UI/ergonomics + WCAG 2.1 AA + dark mode + i18n (human-facing surfaces)

## Error handling pattern (all automations)

```text
try:    fn()
except: gh issue create --title "[chrysa] failure" --label "chrysa-error"
```

## Observability — Sentry → GitHub issues (norm)

Every status:dev repo ships a Sentry project, and **a new Sentry issue automatically opens a
GitHub issue** via Sentry's native GitHub integration. No relay, no PAT in the repo — the
integration owns the link, so a Sentry issue maps to exactly one GitHub issue (no duplicates).

Mechanism: a per-project Sentry **issue alert rule** with
condition `FirstSeenEventCondition` (a new issue is created) and action
`GitHubCreateTicketAction` targeting `chrysa/<repo>`, labels `sentry`, `bug`.
Provision it across all projects with
`shared-standards/scripts/sentry-github-issues.sh` (idempotent, `--dry-run` first).

Per-project activation checklist:

1. Org GitHub integration installed once in Sentry (Settings → Integrations → GitHub) with
   access to the chrysa repos.
2. The repo has a Sentry project whose slug matches the repo name.
3. The auto-issue alert rule exists (run the provisioning script, or add it in
   Alerts → Create Alert → Issues → action "Create a GitHub issue").
4. The GitHub repo has a `sentry` label (CI label sync provides it).

## Session lifecycle (primer + memory + hindsight)

Every repo ships a session lifecycle so an AI agent keeps context across sessions. Bootstrap with
`make memory-init`; scripts live in `shared-standards/scripts/`.

- `primer.md` (committed) — current state, what to do NOW; read **before** `CLAUDE.md`.
- `.claude/memory/session.md` — volatile session notes, **not** committed (reset each session).
- `.claude/memory/decisions.md`, `known-issues.md`, `progress.md` (append-only history) — committed.
- **Session start**: `make prepare` (`/prepare`) — shows primer + git context + open PRs.
- **Session end**: `make hindsight` (`/hindsight`) — updates `primer.md` + `progress.md`, clears
  `session.md`, optional Obsidian export (`OBSIDIAN=<path>`).

## Governance — strategic pillars & ADR format

Five non-negotiables hold across every chrysa project, whatever the stack. Breaking one
requires an ADR with a kill-test, not a shrug.

1. **LLM-provider independence** — no vendor SDK in business code; inference goes through a
   local port with **≥2 real, tested adapters** (e.g. Claude + a local model). A prompt that
   only works on one vendor is a bug, not a feature.
2. **GAFAM independence** — every managed-cloud dependency has a documented self-hosted exit
   path; the cloud SDK stays confined to an adapter (`BlobStore`, not `S3Client`).
3. **Portable personalisation data** — all user/personal data is exportable to an open format
   (JSON/SQLite) by a documented command; `export → import → export` is idempotent (tested).
   A stored-but-unexportable field needs an ADR.
4. **k8s config in-project** — manifests live in `deploy/k8s/` of the repo; nothing exists
   only inside a running cluster.
5. **Adaptation layer** — no third-party lib/API/service is imported by the domain directly;
   it goes through an adapter whose port is written in the domain's language, not the vendor's.

**ADR format (refutable).** Any structural decision — new external dependency, LLM/cloud
provider choice, breaking public-API change, data-model change, or a pillar exception — gets
one ADR under `docs/adr/` (series named in the local `CLAUDE.md`). Beyond the classic fields,
every chrysa ADR carries three that make it falsifiable:

- **Fatal hypothesis** — the single, falsifiable belief whose falsity invalidates the decision.
  One only; about the real world (cost, latency, a third party), not an internal intention.
- **Kill-test** — the observable, dated signal that proves it wrong: what to measure, which
  threshold, when checked, what happens on breach. Mechanised as a test where possible.
- **Validation gate** — the pre-agreed condition that unlocks the next step, written *before*
  building.

`Killed` is a valid ADR status: the kill-test fired and the hypothesis was false. A corpus with
no `Killed` entry has kill-tests that are too lax. Scaffold a new record with `/adr-new`.
<!-- chrysa:standards:end -->
