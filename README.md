# my-assistant

> Floating AI assistant multi-OS — system monitoring, messaging interactions, AI integrations, and external service connectivity.

[![CI](https://github.com/chrysa/my-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/my-assistant/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

`my-assistant` is a configurable floating AI assistant that runs as a desktop overlay on Linux and Windows. It aggregates data from your system, messaging platforms, AI providers, and external services (Notion, GitHub, …) into a single, always-accessible interface.

## Features

| Category | Capabilities |
|----------|-------------|
| **System** | CPU, RAM, disk, network monitoring (psutil) |
| **Messaging** | Discord channel monitoring, AI-powered reply suggestions |
| **AI** | GitHub Copilot, OpenCode server, OpenAI-compatible providers |
| **Services** | Notion (read/write pages), GitHub (repos, issues, PRs) |
| **UI** | Floating frameless overlay (PySide6), system tray, configurable hotkey |
| **Config** | TOML-based, env var interpolation, fully parameterable |

## Architecture

```
my_assistant/
├── cli.py              # Click entry point (--ui / --headless / --enable)
├── app.py              # Application lifecycle + plugin registry
├── config/
│   └── settings.py     # Pydantic settings loaded from config.toml
├── core/
│   └── assistant.py    # AI orchestration — routes queries to providers
├── plugins/
│   ├── base.py         # BasePlugin ABC — setup/teardown/status
│   ├── system/         # System monitor (psutil)
│   ├── messaging/      # Discord webhook + bot monitoring
│   ├── ai/             # AI providers (OpenCode, OpenAI-compatible)
│   └── services/       # External services (Notion, GitHub)
└── ui/
    ├── overlay.py      # PySide6 floating window (requires [ui] extra)
    ├── tray.py         # System tray icon + menu
    └── components/     # Chat widget, system panel, notifications
```

## Quickstart

```bash
# Install (headless — no UI)
pip install -e .

# Install with floating UI
pip install -e ".[ui,discord]"

# Copy and edit config
mkdir -p ~/.config/my-assistant
cp config/config.example.toml ~/.config/my-assistant/config.toml
$EDITOR ~/.config/my-assistant/config.toml

# Run
my-assistant --ui            # float overlay + tray
my-assistant --headless      # tray only (background mode)
```

## Configuration

Config file is resolved in this order:
1. `--config <path>` CLI flag
2. `~/.config/my-assistant/config.toml`
3. `./config/config.toml`

Environment variables can be injected anywhere in the config using `"${ENV_VAR_NAME}"` syntax:

```toml
[plugins.services.notion]
api_key = "${NOTION_API_KEY}"
```

See [config/config.example.toml](config/config.example.toml) for all available options.

## Plugins

Plugins are enabled/disabled individually in the config. Each plugin is independent and can be added without breaking others.

| Plugin | Extra required | Key dependencies |
|--------|---------------|-----------------|
| `system` | — | `psutil` |
| `messaging.discord` | `[discord]` | `discord.py` |
| `ai.opencode` | — | `httpx` (calls local OpenCode server) |
| `ai.openai` | — | `httpx` (OpenAI-compatible REST) |
| `services.notion` | — | `httpx` (Notion REST API) |
| `services.github` | — | `httpx` (GitHub REST API) |

## AI Providers

The `core.assistant` routes queries to the appropriate provider based on intent:

- **Code tasks** → OpenCode server (`opencode serve`, port 4096)
- **Chat / General** → configured default provider (GitHub Copilot, OpenAI, …)
- **Notion queries** → Notion plugin (native MCP or REST)

## Development

```bash
make dev          # Install all deps + pre-commit hooks
make test         # pytest
make lint         # ruff check
make format       # ruff format
```

## Stack

- **Python** 3.12+
- **PySide6** (Qt6) — floating overlay UI (optional)
- **psutil** — system monitoring
- **httpx** — async HTTP (AI providers, Notion, GitHub)
- **Pydantic v2** — config validation
- **Click** — CLI interface

## Claude Optimization

This project follows the **Notion AI Project Update System (Claude Optimized)** for efficient Claude-driven development.

📖 **Reference:** [Notion AI Project Update System](https://www.notion.so/Notion-AI-Project-Update-System-Claude-Optimized-34459293e35e8181ba53ee0212bdba3f)

**Model Strategy:**
- Haiku: simple bugs, documentation, code reviews
- Sonnet: feature dev, UI logic, system integration
- Opus: multi-service architecture decisions

Consult the reference page for context engineering, agent roles, and cost optimization strategies.

## Related projects

- [`chrysa/ai-aggregator`](https://github.com/chrysa/ai-aggregator) — AI provider gateway (future backend)
- [`chrysa/discord-bot-back`](https://github.com/chrysa/discord-bot-back) — Discord bot backend
- [`chrysa/server`](https://github.com/chrysa/server) — k8s cluster (Phase 7: hosted assistant service)
- [`chrysa/diy-stream-deck`](https://github.com/chrysa/diy-stream-deck) — hardware control

## Notion

Project tracking: [AI Project Update System](https://www.notion.so/Notion-AI-Project-Update-System-Claude-Optimized-34459293e35e8181ba53ee0212bdba3f)

## License

MIT — see [LICENSE](LICENSE)
