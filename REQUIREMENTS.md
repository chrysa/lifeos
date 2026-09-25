# REQUIREMENTS — lifeos

> Traceability of requirements to evidence. A row is **IMPLEMENTED** only when a
> file in the repo verifies it. Tags: **FACT / INFERENCE / UNKNOWN / PROPOSAL**.
> Derived from README.md "Status" table, CLAUDE.md "Key Constraints", and the
> shipping source. Where a claim could not be verified in code it is marked
> PLANNED/UNKNOWN, never promoted to IMPLEMENTED.

## Product requirements (REQ-PROD)

| ID | Requirement | State | Evidence |
| --- | --- | --- | --- |
| REQ-PROD-001 | Provide a CLI entry (`lifeos` / `python -m lifeos`) with `--config`, `--ui/--headless`, `--enable`, `--debug`, `--version` | IMPLEMENTED (FACT) | `lifeos/cli.py`, `lifeos/__main__.py`, console script in `pyproject.toml` |
| REQ-PROD-002 | Load optional TOML config; run on sensible defaults when absent | IMPLEMENTED (FACT) | `lifeos/config/settings.py` `load_config` |
| REQ-PROD-003 | Model plugin enable/disable flags (`discord`, `github`, `notion`) | IMPLEMENTED — flags only, no plugin logic (FACT) | `settings.py` `PluginsConfig`; README Status table |
| REQ-PROD-004 | Run a headless application core that reports readiness | IMPLEMENTED (FACT) | `lifeos/app.py` `Application.run` |
| REQ-PROD-005 | Floating overlay UI (PySide6, always-on-top, frameless) | PLANNED — not implemented (FACT) | README Status ⬜; `--ui` warns + runs headless (`app.py`); `[ui]` extra declared in `pyproject.toml` |
| REQ-PROD-006 | Messaging / AI / service plugins (Discord, OpenCode, OpenAI, Notion, GitHub) | PLANNED — not implemented (FACT) | README Status ⬜; no `plugins/` package on disk |
| REQ-PROD-007 | System monitoring (psutil) emitting stats events | PLANNED — not implemented (FACT) | README Status ⬜; `psutil` dep declared, unused |
| REQ-PROD-008 | Publish `personal.*` capability manifests consumed by LOGOS | PLANNED — not present (FACT) | ADR-LIFEOS-001 follow-up; no manifest in repo |

## Technical requirements (REQ-TECH)

| ID | Requirement | State | Evidence |
| --- | --- | --- | --- |
| REQ-TECH-001 | Python `>=3.14` | IMPLEMENTED (FACT) | `pyproject.toml requires-python`. NB: CLAUDE.md says "3.12+ minimum" — contradiction, see REVIEW.md |
| REQ-TECH-002 | Sentry observability, no-op without `SENTRY_DSN` | IMPLEMENTED (FACT) | `lifeos/observability/__init__.py` |
| REQ-TECH-003 | No secrets in code; external servers addressed via env | IMPLEMENTED (FACT) | no secrets in `lifeos/`; `.env.example`, `.mcp.json` use env refs |
| REQ-TECH-004 | Cross-platform (Linux **and** Windows), no platform-specific code in core | INFERENCE — plausible for current core; unverified on Windows | classifiers list both OSes; core uses stdlib/Click/Pydantic only. No CI Windows job verified (UNKNOWN) |
| REQ-TECH-005 | Optional extras must not be required to start (`[ui]`, `[discord]`) | IMPLEMENTED for `[ui]` (FACT); `[discord]` untested (no plugin) | `app.py` degrades to headless; discord plugin absent |
| REQ-TECH-006 | `${ENV_VAR}` interpolation in TOML string values | NOT IMPLEMENTED (FACT) | `settings.py` does plain `tomllib` load; no expansion. CLAUDE.md claims it — see REVIEW.md #3 |
| REQ-TECH-007 | All HTTP via `httpx.AsyncClient` with explicit timeout | UNKNOWN / N/A now | `httpx` declared but no HTTP client code shipped yet |
| REQ-TECH-008 | Tests are pytest; coverage gate 85% | IMPLEMENTED (config) (FACT) | `pyproject.toml [tool.pytest]` `--cov-fail-under=85`; suite is a placeholder |
| REQ-TECH-009 | mypy strict; ruff lint/format | IMPLEMENTED (config) (FACT) | `pyproject.toml [tool.mypy] strict=true`, `[tool.ruff]` |

## Notes

- The **planned** rows (005–008, TECH-006/007) reflect goals stated in README/
  CLAUDE.md but with no shipping code; they are intentionally not IMPLEMENTED.
- ADR-LIFEOS-001 may retire several REQ-PROD rows (overlay UI, autonomous AI
  routing) into LOGOS rather than LifeOS — treat the planned product surface as
  provisional until the recadrage lands (see DECISIONS.md).
