# my-assistant

Floating AI assistant multi-OS — PySide6 overlay, plugin system, multi-provider (GitHub Copilot / OpenAI-compatible).

## Features

- **Floating overlay** — Always-on-top frameless window (PySide6)
- **Headless mode** — Runs without UI as a tray application
- **Plugin architecture** — Extensible with system monitor, Discord, Notion, GitHub integrations
- **Multi-provider AI** — Routes to GitHub Copilot (via OpenCode), OpenAI-compatible APIs
- **Cross-platform** — Linux & Windows (no platform-specific code in core)

## Quick Start

```bash
pip install my-assistant[ui]
my-assistant --ui          # Launch with overlay
my-assistant --headless    # Launch as background service
```

## Configuration

All config is TOML-based — no hardcoded values:

```toml
[ai]
provider = "opencode"
endpoint = "${OPENCODE_ENDPOINT}"

[notion]
token = "${NOTION_TOKEN}"

[github]
token = "${GITHUB_TOKEN}"
```

## Architecture

| Module | Role |
|--------|------|
| `cli.py` | Click entry point |
| `app.py` | Application lifecycle |
| `core/assistant.py` | AI orchestration, provider routing |
| `plugins/` | Extensible plugin system (BasePlugin ABC) |
| `ui/overlay.py` | PySide6 floating window |
| `config/settings.py` | Pydantic TOML config loader |

## Links

- [GitHub](https://github.com/chrysa/my-assistant)
- [Notion](https://www.notion.so/my-assistant-Sp-cification-Architecture-v0-1-33859293e35e81159d10f6690fe1f14e)
