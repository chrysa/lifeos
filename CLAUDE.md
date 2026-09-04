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
# chrysa — Transverse Standards (core)

> The **slim always-on core**. The canonical, tool-agnostic source of truth is `standards/STANDARDS.chrysa.md`; the normative annexes live under `standards/annexes/`. Each rule below is a one-line pointer — its full text lives in the per-domain file named beside the heading (`standards/rules/<domain>.md`), read on demand.

**Where an annexe and the canon disagree, the canon wins.**

### Governance, language & compliance · `standards/rules/governance.md`
- Normative annexes
- Language
- Compliance targets
- Governance — strategic pillars & ADR format

### Cross-cutting stack · `standards/rules/stack.md`
- Cross-cutting stack (settled ADRs — do not relitigate)

### SCM — branches, commits & pull requests · `standards/rules/scm.md`
- Commits
- Branches
- Branch model — `main` is production, `develop` is the workspace
- Merge
- One PR per issue
- Issues and PRs are type-driven

### Architecture, decoupling & portability · `standards/rules/architecture.md`
- Repo provenance — every code repo depends on `project-init`
- Every repo declares its profile and DDD level
- Projects talk through versioned contracts only
- Everything is machine-agnostic and portable — no rule, repo, or script is bound to one machine
- Every external server the service talks to is addressed through the environment — never hardcoded
- Every tracked file and folder must earn its place — a repo holds only what is useful to it now
- The repository architecture is legible to an agent — optimised for Claude, not only for humans
- Deferred work is a governed job, not a fire-and-forget

### Testing · `standards/rules/testing.md`
- Tests: pytest only
- Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later

### Frontend & web semantics · `standards/rules/frontend.md`
- TypeScript is strict by contract
- The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden
- React is a presentation layer, not the domain
- The frontend says when the backend is unreachable or unstable
- The frontend is reactive and real-time by default
- UI state survives reload & focus
- Everything is semantic — the markup, the data, and the URLs
- URL-addressable frontend navigation — mandatory

### APIs, contracts & real-time · `standards/rules/api.md`
- A real-time backend has channel contracts and never blocks
- APIs, SDKs & public contracts follow the `STD-API-001` contract

### Accessibility · `standards/rules/accessibility.md`
- Dark mode
- Every site is usable by the majority of disabilities — not only the screen-reader case

### Documentation & session state · `standards/rules/docs.md`
- Notion logging
- Documentation and Notion are maintained in lockstep with the code — a change that leaves them stale is unfinished
- Session lifecycle (primer + memory + hindsight)

### AI agents & features · `standards/rules/agents.md`
- Agent actions are governed
- An AI feature is evaluated, not just shipped
- An agent writes only where the owner owns

### Security, identity & sessions · `standards/rules/security.md`
- Per-person data implies a user account — no exceptions dressed up as simplicity
- Identity goes through the cluster SSO first
- A session is secured and it expires
- Every form is a hostile input surface — validate on the server, always
- Security scanning is a gate, not an afterthought — it runs in pre-commit and in CI

### Code quality & anti-patterns · `standards/rules/code-quality.md`
- No hardcoded constants
- No literal HTTP status codes — use the constants the framework already ships
- No code duplication — the second occurrence is an extraction order
- Raised errors are typed
- Failures are contained, and observable
- Prefer a lookup table to a state machine
- Decompose into small, independently unit-testable methods
- Code is read far more often than it is written — optimise for the reader, and standardise the form
- Avoid lambdas and anonymous constructs — a named function is the default
- Basic optimisations and known anti-patterns are caught in review and in CI
- A cache is a correctness contract, not a sprinkle of speed
- Quality gates
- Error handling pattern (all automations)

### Backend Python · `standards/rules/backend-python.md`
- Python packaging — `pyproject.toml` is the single source of truth
- Python is written object-oriented, one class per file
- Import the item, not the module — `from x import y; y()`
- Functions and methods are called with named arguments — positional call sites are the exception, not the rule

### Data, persistence & migrations · `standards/rules/data.md`
- Data, persistence & migrations follow the `STD-DATA-001` contract

### Observability & operations · `standards/rules/observability.md`
- Observability & production readiness follow the `STD-OPS-001` contract
- The container is versioned separately from the application it hosts, and an admin can see what is actually deployed
- Observability — error-tracking → GitHub issues (norm)

### Containers & compose · `standards/rules/containers.md`
- Everything runs in a container — the only exception is the slice of a repo genuinely bound to the host OS
- External dependencies are installed in containers, never on the host
- No virtualenv in a repo — ever
- Tool caches & deps never touch the project tree
- Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory
- App containers ship the app only — the platform layer is the owner's responsibility
- Only a publicly useful port is published — everything else stays on the container network
- A compose file is minimal — declare only what the stack needs, default the rest
- Dev stage must hot-reload
- Local dev runs the code in-container, live, in debug mode — never the production server
- Default to dev mode when starting an app locally — any other mode only when explicitly asked
- `.dockerignore` mandatory & exhaustive
- Container-runtime policy

### Product surfaces · `standards/rules/product.md`
- Setup wizard & config panel
- A game is DRM-free and fully playable solo offline
- Every product that is operated ships a management backoffice
- If a user can supply a file, the product accepts an upload
- A floating assistant where it earns its place — never as decoration

### Design system · `standards/rules/design.md`
- Design system

### Developer loop & tooling · `standards/rules/dev-loop.md`
- Makefile targets
- Shared skills (load on demand from shared-standards/.claude/skills/)

### CI/CD, pre-commit & release · `standards/rules/ci-cd.md`
- Release & changelog config (canonical)
- GitHub Actions (reuse first · custom actions centralised · thin workflows)
- Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)
<!-- chrysa:standards:end -->
