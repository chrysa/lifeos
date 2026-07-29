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
| Auth             | 4 modes: Google OAuth2 · local (bcrypt) · LDAP · VCS OAuth      |
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
  changes) is logged in Notion — the single source of truth. Run `@notion-sync` after any
  state change; in case of conflict between local docs and Notion, Notion wins.
- **No hardcoded constants** in code — neither backend (Python) nor frontend (TS).
  All constants and config values (thresholds, business rules, labels, URLs, magic
  numbers) live in **external YAML files** and are loaded at runtime. Code reads them
  through a typed loader (Pydantic Settings backend · generated typed module frontend),
  never as inline literals. Only language-level enums (e.g. `status.HTTP_*`) are exempt.
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
  not a dev image.
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
