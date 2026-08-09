# lifeos

> Floating AI assistant multi-OS — **early scaffold.**
> Today this is a headless CLI core: it loads config, resolves which plugins are
> enabled, and runs a logging run-loop. The overlay UI, messaging/AI/service
> plugins, and system monitoring are planned but **not yet implemented**.

[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Status

What actually ships in this repo today:

| Piece | State |
| --- | --- |
| Click CLI (`lifeos` / `python -m lifeos`) | ✅ `--config`, `--ui/--headless`, `--enable`, `--debug`, `--version` |
| TOML config loader (Pydantic) | ✅ optional file; sensible defaults when absent |
| Plugin enable/disable flags | ✅ config flags for `discord`, `github`, `notion` (no plugin logic yet) |
| Headless application core | ✅ logs resolved config + enabled plugins, then reports ready |
| Sentry observability init | ✅ `lifeos/observability` |
| Floating overlay UI (PySide6) | ⬜ planned — `[ui]` extra declared, not implemented |
| Messaging / AI / service plugins | ⬜ planned — not implemented |
| System monitoring (psutil) | ⬜ planned — not implemented |

The `--ui` flag currently logs a warning and runs headless: the overlay build
does not exist yet.

## Quickstart

```bash
pip install -e .          # headless core
lifeos                    # runs headless (overlay not yet available)
lifeos --headless         # explicit headless
lifeos --enable discord   # force-enable a plugin flag
lifeos --config ./my.toml # point at a specific config file
```

## Configuration

Config is a TOML file (optional). Resolution order:

1. `--config <path>` CLI flag
2. `~/.config/lifeos/config.toml`

When no file is found, defaults are used and the app still runs. Only plugin
enable flags are modelled so far:

```toml
[plugins.discord]
enabled = true
```

## Layout

| Path | Role |
| --- | --- |
| `lifeos/cli.py` | Click entry point — flags and startup |
| `lifeos/app.py` | `Application` lifecycle (headless run-loop) |
| `lifeos/config/settings.py` | Pydantic TOML settings + loader |
| `lifeos/observability/` | Sentry init |
| `tests/` | Test suite (placeholder as the core grows) |

## Development

```bash
make dev          # install dev deps + pre-commit
make test         # pytest
make lint         # ruff check
make typecheck    # mypy
make run-headless # python -m lifeos --headless
```

## Stack

- **Python** 3.14+
- **Click** — CLI
- **Pydantic v2** — config validation
- **sentry-sdk** — error reporting
- Optional extras (declared, not yet wired): **PySide6** (`[ui]`), **discord.py** (`[discord]`)

## License

MIT — see [LICENSE](LICENSE).
