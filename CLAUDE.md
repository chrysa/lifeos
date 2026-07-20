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

## Non-negotiable conventions

- **Language**: English — all code, comments, docs, instructions, and config files.
- **Commits**: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`).
- **Branches**: `feature/`, `bugfix/`, `chore/`, `hotfix/`, `release/` · default branch `develop`.
- **Merge**: squash merge only · force push forbidden · auto-merge requires CI + owner.
- **One PR per issue**, scoped tight. Every PR references an issue (`Closes/Fixes/Refs #N`).
  Exception: label `hotfix`. The `enforce-issue-link` workflow is a blocking status check.
- **Tests: pytest only** — assert-style test functions and `pytest-mock` (`mocker`
  fixture: `mocker.patch`, `mocker.AsyncMock`) for all mocking. The stdlib **`unittest`
  framework (`unittest.TestCase`) and `unittest.mock` imports are forbidden** — no
  `import unittest`, no `from unittest.mock import …`. See the `testing-pytest` skill.
- **Dark mode** mandatory from V1. **Accessibility** WCAG 2.1 AA.
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

## Quality gates

- Test coverage **>= 85%** by default. A repo may override upward, never below 80%.
- Lint warnings: **0**. Mypy clean. SonarCloud rating **A**, 0 security hotspot.
- Max function lines 50 · max file lines 500 · cyclomatic complexity heuristic <= 10.

## Frontend linting under TypeScript 7

TypeScript 7 (native/tsgo) is the fleet standard, but the published `typescript@7`
package no longer exposes the classic compiler JS API (`ts.Extension`, `ts.ModuleKind`).
`@typescript-eslint/typescript-estree` reads that API at import, so **any ESLint config
using `@typescript-eslint/parser` or its plugin crashes on load** — `eslint`/`make
web-lint` is dead. No released `typescript-eslint` (≤ 8.64) supports TS7.

**Interim standard until `typescript-eslint` ships TS7 support:** lint with
`@babel/eslint-parser` **v8** (ESLint-10 compatible) + `@babel/preset-typescript` — it
parses TS/TSX syntax without the TS compiler API. Keep `eslint-plugin-react-hooks`
(`rules-of-hooks` error, `exhaustive-deps` warn). This is a **deliberately degraded**
lint: type-aware `@typescript-eslint` rules are dropped, and **`tsc --noEmit` (`make
typecheck`) remains the source of truth for type errors**. Revert to the
typescript-eslint parser + recommended rules once it supports TS7.

```js
// eslint.config.js (flat)
import babelParser from "@babel/eslint-parser";
import reactHooks from "eslint-plugin-react-hooks";
export default [
  { ignores: ["dist/**", "node_modules/**", "vite.config.ts"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false, sourceType: "module", ecmaFeatures: { jsx: true },
        babelOptions: { presets: [["@babel/preset-typescript", { isTSX: true, allExtensions: true }]] },
      },
    },
    plugins: { "react-hooks": reactHooks },
    rules: { "react-hooks/rules-of-hooks": "error", "react-hooks/exhaustive-deps": "warn" },
  },
];
```

Reference implementation: `chrysa/sport-intelligence-hub#270`.

## Shared UI library contract (`@chrysa/ui`)

The shared component library is the single source of UX truth; a defect there
propagates to every consumer. The library **guarantees**, it does not suggest
(see ADR-0005):

- **Ships its own styles.** The package delivers its CSS + design tokens (dark +
  light), not just class names. A consumer importing `@chrysa/ui` with zero extra
  CSS renders WCAG 2.1 AA, `:focus-visible`, ≥44px targets, and honours
  `prefers-reduced-motion`. Kill-test: a bare consumer passes an axe-core AA scan
  with no local style overrides.
- **Owns the non-nominal states.** Every data component exposes `loading` / `empty`
  / `error`; the app never reinvents them. `BackendConnectionBanner` is provided
  **and mounted** by the shell — never shipped as dead code.
- **A11y is mandatory by type, not by discipline.** `Input` requires a label or
  `aria-label` and wires `aria-invalid`/`aria-describedby`; overlays trap focus and
  close on `Esc`; `Icon` requires `aria-label` or `aria-hidden`. A prop that lets
  a11y be omitted is a bug.

## CLI UX (every distributed command-line surface)

A CLI is a human-facing surface, held to the same "no surprises" bar as the web UI
(see ADR-0005; enforced via the `cli-developer` agent brief):

- `--version` and `--help` (with examples) on every command and sub-command.
- **stdout = data, stderr = logs/errors.** Machine output via `--json` on stdout only.
- Documented, stable **exit codes** (`0` ok · `1` findings/soft-fail · `2` usage).
- Colour only on a TTY; honour `NO_COLOR`; never ANSI in a pipe.
- Any destructive command offers a **truly non-destructive `--dry-run`** (writes
  nothing — verified by a test) and a non-interactive flag for CI.
- Error messages are actionable: what failed **and** how to fix it.

A CLI missing `--version`, or whose `--dry-run` writes, is a bug.

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
