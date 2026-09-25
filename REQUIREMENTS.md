# Requirements — lifeos (my-assistant)

> Reverse-engineered from the repository (README.md, CLAUDE.md, ARCHITECTURE.md,
> `pyproject.toml`, `lifeos/` source, `tests/`, ADR-LIFEOS-001). Each item is
> tagged FACT (verifiable in-repo), INFERENCE (reasoned from evidence), or
> UNKNOWN. "IMPLEMENTED" is asserted only where source + a test prove it.
>
> **Identity caveat (FACT):** `docs/adr/ADR-LIFEOS-001` states `my-assistant` is a
> retired/archived accidental fork and `lifeos` is the canonical repo, and that
> the "floating AI assistant / my-assistant" identity should be dropped and the
> product recadré as a `personal.*` capability pack consumed by LOGOS. The
> product requirements below describe what the code and docs in **this** repo
> currently express; they are in tension with that ADR. See DECISIONS.md and the
> contradiction note in REVIEW.md.

## Product requirements

| ID | Requirement | Source | Status |
| --- | --- | --- | --- |
| REQ-PROD-001 | Provide a floating, multi-OS AI assistant (Linux + Windows) that can run as an overlay or headless tray app | README.md, CLAUDE.md (FACT: stated intent) | PLANNED (README Status table marks overlay/tray ⬜) |
| REQ-PROD-002 | Load configuration and resolve which plugins are enabled, then run a run-loop reporting "ready" | README.md, `lifeos/app.py` | IMPLEMENTED (FACT: `app.py`, tests assert `enabled_plugins()` + "ready"/headless logs) |
| REQ-PROD-003 | Integrate messaging (Discord), AI providers (OpenCode/OpenAI-compatible) and services (Notion, GitHub) via plugins | CLAUDE.md architecture section, pyproject keywords | PLANNED (FACT: no `plugins/` package on disk; only enable *flags* modelled) |
| REQ-PROD-004 | Monitor the host system (CPU/mem via psutil) and surface stats | CLAUDE.md, README Status table | PLANNED (FACT: psutil declared as dep, not wired) |
| REQ-PROD-005 | Ship a floating overlay UI (PySide6) and a system tray icon | CLAUDE.md, README | PLANNED (FACT: `[ui]` extra declared; `--ui` logs a warning and falls back to headless) |
| REQ-PROD-006 | (Per ADR) Recadre the product as a `personal.*` capability pack that LOGOS discovers, consumes and governs via versioned contracts | ADR-LIFEOS-001 | PLANNED / follow-up (FACT: ADR "Consequences" lists it as not-yet-done) |

## Technical requirements

| ID | Requirement | Source | Status |
| --- | --- | --- | --- |
| REQ-TECH-001 | Expose a Click CLI (`lifeos` / `python -m lifeos`) with `--config`, `--ui/--headless`, `--enable`, `--debug`, `--version` | `lifeos/cli.py`, README | IMPLEMENTED (FACT: source + CLI tests) |
| REQ-TECH-002 | Optional TOML config via Pydantic; resolution `--config` → `~/.config/lifeos/config.toml`; defaults when absent | `lifeos/config/settings.py`, README | IMPLEMENTED (FACT: `load_config` returns defaults when file missing; tests assert flags) |
| REQ-TECH-003 | `${ENV_VAR}` interpolation in TOML string values, keeping literal + warning when var missing | CLAUDE.md "Config System" | UNKNOWN / likely PLANNED (INFERENCE: not observed in the read of `settings.py`; verify in source) |
| REQ-TECH-004 | Plugin base ABC (`setup`/`teardown`/`get_status`) + event emitter; failures never crash the app | CLAUDE.md "Plugin System" | PLANNED (FACT: no `plugins/base.py` present) |
| REQ-TECH-005 | Sentry observability init, no-op when `SENTRY_DSN` unset | `lifeos/observability/__init__.py`, `.env.example` | IMPLEMENTED (FACT: source guards on DSN) |
| REQ-TECH-006 | All HTTP via `httpx.AsyncClient` with explicit timeout (default 30s) | CLAUDE.md | PLANNED (FACT: httpx declared; no HTTP client code present yet) |
| REQ-TECH-007 | Python ≥3.14 (CLAUDE floor says 3.12+); runs on Linux and Windows with no platform-specific code in core | `pyproject.toml` (`requires-python`), classifiers | PARTIAL (FACT: `requires-python>=3.14`; CLAUDE says "3.12+ minimum, target 3.14" — drift, see REVIEW) |
| REQ-TECH-008 | ≥85% test coverage enforced in CI | `pyproject.toml` `--cov-fail-under=85` | IMPLEMENTED as a gate (FACT: addopts) |
| REQ-TECH-009 | Generated context files (`handover.md`, `ai-instructions.md`, `llms-full.txt`, `context-map.json`) kept in sync via `make gen-context-files` | generated file headers, ai-instructions.md | IMPLEMENTED (FACT: files present, marked generated) |

## Non-goals / explicit boundaries (FACT, from ADR-LIFEOS-001)

- LifeOS must **not** access Notion or other sources directly — LOGOS brokers data and governance.
- LifeOS owns **no** generalist assistant, memory, or agenda of its own — those belong to LOGOS.
- LifeOS is **not** a git submodule of LOGOS; the two talk through versioned capability contracts only.
