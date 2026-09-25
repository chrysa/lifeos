# REVIEW — lifeos (documentation audit)

> Read-only documentation pass. Findings are tagged **FACT** (verifiable in the
> repo), **INFERENCE** (reasoned from evidence), **UNKNOWN**, or **PROPOSAL**.
> No source, tests, deps, CI or config were modified.

- **Repository:** `lifeos` (package `lifeos`)
- **Path:** `/home/anthony/Documents/perso/projects/chrysa/lifeos`
- **Remote:** `git@github.com:chrysa/lifeos.git`
- **Branch at audit:** `chore/claude-config-drift-hook`
- **Language / framework (FACT):** Python `>=3.14`; Click CLI; Pydantic v2 +
  pydantic-settings; sentry-sdk. Build: hatchling. Lint: ruff. Types: mypy
  (strict). Tests: pytest.

## What the repo actually is today (FACT)

A **headless CLI scaffold**. The shipping code is:

- `lifeos/cli.py` — Click entry (`--config`, `--ui/--headless`, `--enable`,
  `--debug`, `--version`).
- `lifeos/app.py` — `Application` lifecycle: logs resolved config + enabled
  plugins, warns if `--ui` requested (overlay absent), logs "LifeOS ready".
- `lifeos/config/settings.py` — Pydantic TOML loader; optional file, defaults
  when absent; models plugin `enabled` flags only (`discord`, `github`,
  `notion`).
- `lifeos/observability/__init__.py` — Sentry init; no-op without `SENTRY_DSN`.
- `tests/test_placeholder.py` — placeholder test.

There is **no** `plugins/`, `core/`, or `ui/` package on disk (FACT: `find` over
`lifeos/` shows only `cli`, `app`, `config`, `observability`, `__main__`).

## Contradictions found

1. **CLAUDE.md describes an implemented system that does not exist (FACT).**
   `CLAUDE.md` "Project Purpose" and "Architecture" list `core/assistant.py`,
   `plugins/base.py`, `plugins/system/monitor.py`,
   `plugins/messaging/discord.py`, `plugins/ai/opencode.py`,
   `plugins/ai/openai.py`, `plugins/services/notion.py`,
   `plugins/services/github.py`, `ui/overlay.py`, `ui/tray.py`,
   `ui/components/*` — none of these files are present. README.md and
   ARCHITECTURE.md correctly mark these as planned/not-yet-implemented.
   *Impact:* an agent reading only CLAUDE.md would assume a plugin runtime,
   event emitter, and env-var interpolation that are not in the code.
   *Note:* CLAUDE.md also states "Python 3.12+ minimum; target 3.14", while
   `pyproject.toml` sets `requires-python = ">=3.14"` and README says 3.14+.

2. **Product identity vs. accepted ADR-LIFEOS-001 (FACT).** README, CLAUDE.md
   and `pyproject.toml` still brand lifeos a "Floating AI assistant multi-OS".
   ADR-LIFEOS-001 (Accepted 2026-09-06) re-scopes lifeos as a **capability pack
   consumed and governed by LOGOS** — "ni assistant généraliste, ni mémoire
   personnelle, ni Policy Engine, ni client conversationnel autonome" — and
   explicitly lists a follow-up to "drop the floating AI assistant / my-assistant
   identity in README.md and define the `personal.*` manifests". That recadrage
   has not landed. This is the **lifeos ↔ LOGOS / floating-agent scope boundary**
   and is the central open question for the repo (see DECISIONS.md).

3. **`env var interpolation` claimed but not implemented (FACT).** CLAUDE.md
   "Config System" promises `${ENV_VAR}` interpolation in TOML string values.
   `lifeos/config/settings.py` performs a plain `tomllib` load + Pydantic
   validation with no `${...}` expansion. (Sentry env vars are read directly via
   `os.getenv` in `observability`, which is a different mechanism.)

4. **Config resolution order differs across docs (FACT).** CLAUDE.md lists three
   sources (`--config`, `~/.config/lifeos/config.toml`, `./config/config.toml`);
   README lists two (no `./config/config.toml`). The code
   (`load_config`) checks `--config` then `DEFAULT_CONFIG_PATH`
   (`~/.config/lifeos/config.toml`) only — README matches the code; CLAUDE.md
   over-states.

## Documentation debt (INFERENCE)

- CLAUDE.md needs recadrage to describe the *scaffold* + capability-pack
  direction, not an implemented plugin/UI runtime. (Left to owner; this pass does
  not rewrite CLAUDE.md's authored sections, only records the drift.)
- No `personal.*` capability manifest exists yet (ADR follow-up, UNKNOWN when).
- `docs/reference/github-inspiration.md` and pyproject keywords still frame the
  old "my-assistant" desktop-app identity.

## Security (FACT)

No hardcoded secrets in `lifeos/`. `.env.example` holds placeholders; `.mcp.json`
uses `${GITHUB_TOKEN}` / `${NOTION_API_KEY}` env references. `.secrets.baseline`
entries are pre-commit-hook revision hashes in `.pre-commit-config.yaml`
(detect-secrets "Hex High Entropy String"), not credentials. See SECURITY.md.

## Docs generated in this pass

`REVIEW.md`, `DECISIONS.md`, `REQUIREMENTS.md`, `SECURITY.md`. Other templates
(PRD, TRD, TESTING, OBSERVABILITY, ROADMAP, GLOSSARY, CONSTRAINTS) were **skipped**
— see each rationale in DECISIONS.md / REQUIREMENTS.md and the handback report.
Existing docs (README, ARCHITECTURE, AGENTS, ai-instructions, handover, ADR,
CHANGELOG, CONTRIBUTING) were preserved and are accurate except where noted above.
