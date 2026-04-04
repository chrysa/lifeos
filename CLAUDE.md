# CLAUDE.md — my-assistant

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
2. `~/.config/my-assistant/config.toml`
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
make run          # python -m my_assistant --ui
make run-headless # python -m my_assistant --headless
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
