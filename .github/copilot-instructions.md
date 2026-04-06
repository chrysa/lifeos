# my-assistant — GitHub Copilot Instructions

## Project Overview

Floating AI assistant multi-OS (Linux + Windows) — PySide6 overlay, plugin system,
multi-provider AI routing (GitHub Copilot via OpenCode, OpenAI-compatible APIs).

## Instruction files

- `.github/instructions/python_guidelines.instructions.md` — Python 3.14, patterns async, httpx
- `.github/instructions/plugin_system.instructions.md` — BasePlugin ABC, lifecycle, events
- `.github/instructions/testing.instructions.md` — pytest patterns, fixtures, mocking

## Stack

- **Language**: Python 3.14
- **UI**: PySide6 6.x (optional `[ui]` extra — app MUST start headless without it)
- **Config**: Pydantic v2 TOML loader (`config/settings.py`) — `${ENV_VAR}` interpolation
- **HTTP**: `httpx.AsyncClient` — explicit timeout 30s — no `requests`
- **AI providers**: OpenCode (port 4096), OpenAI-compatible
- **Integrations**: Notion REST API v1, GitHub REST API
- **Tests**: pytest 8 + pytest-asyncio + unittest.mock
- **Lint**: ruff + mypy strict

## Key Constraints

- Python 3.14 minimum — no platform-specific code in `core/` or `plugins/`
- PySide6 optional: `try/except ImportError` everywhere in `ui/`
- All config via TOML — no hardcoded values (except Pydantic defaults)
- No secrets in code — always `"${ENV_VAR}"` pattern
- Plugin failures **must never crash the app** — always `try/except` in `setup()` / `teardown()`
- All HTTP calls: `httpx.AsyncClient` with explicit `timeout=httpx.Timeout(30.0)`
- OWASP Top 10: validate all external inputs, no secrets in logs

## Architecture

```
cli.py          → Click entry, --ui / --headless flags
app.py          → Lifecycle, plugin registry
core/assistant.py → AI orchestration, provider routing
plugins/        → BasePlugin ABC: setup(), teardown(), get_status()
ui/overlay.py   → PySide6 frameless always-on-top
config/settings.py → Pydantic TOML loader
```

## Code Patterns

```python
# Plugin example
from plugins.base import BasePlugin, emit

class MyPlugin(BasePlugin):
    async def setup(self) -> None:
        try:
            ...
        except Exception as exc:
            self.logger.warning("Plugin setup failed: %s", exc)  # never raise

    async def teardown(self) -> None: ...
    def get_status(self) -> dict: return {"active": True}
```
