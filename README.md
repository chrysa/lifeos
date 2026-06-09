# lifeos

> Floating desktop AI assistant for Linux and Windows — a single, always-accessible overlay for system info, messaging, and AI providers.

[![CI](https://github.com/chrysa/my-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/my-assistant/actions/workflows/ci.yml)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> [!WARNING]
> **Early scaffold (v0.1.0, Alpha).** Only the CLI skeleton and Sentry error
> tracking are implemented today. The application runtime (`lifeos.app.Application`),
> the config loader (`lifeos.config.settings.load_config`), the plugin system, and
> the PySide6 overlay UI described as goals below **do not exist yet** — running the
> command currently exits with an import error. See [Status](#status) before using.

## Who it's for

A solo developer (or small team) who wants one floating overlay on the desktop to
glance at system metrics, watch messaging channels, and talk to AI providers without
switching windows. This repository is the project foundation; it is not yet usable.

## Status

What ships in this version:

- **CLI entry point** (`lifeos`) built on Click — parses `--config`, `--ui/--headless`,
  `--enable`, `--debug` and is wired to bootstrap the (not-yet-written) application.
- **Observability** — optional Sentry integration (`lifeos.observability.init_sentry`),
  a no-op unless `SENTRY_DSN` is set.
- Full project tooling: CI, Ruff, Mypy (strict), pytest (≥85% coverage gate),
  pre-commit, MkDocs, SonarCloud, git-cliff changelog.

Not yet implemented (planned): `lifeos.app.Application`, config loading from TOML,
the plugin system, the PySide6 overlay, system tray, and any AI / Notion / Discord /
GitHub integrations.

## Installation

Requires **Python 3.14+**.

```bash
# Clone and install (editable)
git clone https://github.com/chrysa/my-assistant.git
cd my-assistant
pip install -e .              # runtime (headless)
pip install -e ".[ui]"        # + PySide6 overlay extra
pip install -e ".[ui,discord,dev]"   # + Discord extra + dev tooling
```

## Usage

The CLI is the only runnable surface today. Inspect its interface:

```bash
lifeos --help
lifeos --version
```

```
Usage: lifeos [OPTIONS]

  LifeOS — floating AI assistant for Linux and Windows.

Options:
  --version            Show the version and exit.
  -c, --config FILE    Path to config.toml (default: ~/.config/lifeos/config.toml)
  --ui / --headless    Enable floating overlay UI (requires [ui] extra).  [default: ui]
  --enable PLUGIN      Force-enable plugin(s) regardless of config (e.g. --enable discord).
  --debug              Enable DEBUG logging.
  --help               Show this message and exit.
```

> Invoking `lifeos --ui` or `lifeos --headless` currently fails: the CLI imports
> `lifeos.app.Application` and `lifeos.config.settings.load_config`, which are not
> implemented yet. `--help` and `--version` work.

## Configuration

The CLI resolves its config path from `--config <path>`, falling back to
`~/.config/lifeos/config.toml`. The TOML schema and loader are not implemented yet,
so no config keys are wired in.

### Environment variables

Sentry is configured purely from the environment (see [.env.example](.env.example)):

| Variable      | Default          | Purpose                                              |
|---------------|------------------|------------------------------------------------------|
| `SENTRY_DSN`  | _(empty)_        | Sentry DSN. Empty disables error tracking entirely.  |
| `ENVIRONMENT` | `development`    | Sentry environment tag.                              |
| `RELEASE`     | `lifeos@0.1.0`   | Sentry release tag.                                  |

## Development

```bash
make dev          # install [ui,discord,dev] + pre-commit hooks
make test         # pytest (coverage gate: 85%)
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy (strict)
```

## Stack

- **Python** 3.14+
- **Click** — CLI interface
- **Pydantic v2** / **pydantic-settings** — config validation (planned)
- **httpx** — async HTTP (planned integrations)
- **psutil** — system monitoring (planned)
- **Rich** — terminal output
- **sentry-sdk** — error tracking
- **PySide6** (Qt6) — floating overlay UI (planned, optional `[ui]` extra)

## Documentation

- [docs/index.md](docs/index.md) — project docs (MkDocs Material, published via GitHub Pages)
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide
- [CHANGELOG.md](CHANGELOG.md) — auto-generated from conventional commits (git-cliff)
- [DECISIONS.md](DECISIONS.md) — architecture decisions

## License

MIT — see [LICENSE](LICENSE).
</content>
</invoke>
