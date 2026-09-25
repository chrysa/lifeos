# Glossary — lifeos (my-assistant)

> Terms as used in this repo's docs, source and ADR. FACT unless noted.

- **lifeos** — the Python package (`lifeos/`) and the product name used across README/CLAUDE.md; an early scaffold of a floating multi-OS AI assistant. Also the canonical repo name per ADR-LIFEOS-001.
- **my-assistant** — this repository's name and GitHub slug (`chrysa/my-assistant`). Per ADR-LIFEOS-001 it is a retired/archived accidental fork of `lifeos`. (identity tension — see REVIEW.md)
- **LOGOS** — a self-hosted, JARVIS-like cognitive partner (Socle/Plateforme) that, per the ADR, consumes and governs capabilities. Not in this repo.
- **Capability pack** — the ADR's target model for LifeOS: a standalone repo that publishes `personal.*` capability manifests consumed/governed by LOGOS via versioned contracts (not a submodule).
- **`personal.*` manifests** — the (planned) versioned capability contracts LifeOS would publish for LOGOS to discover. (PLANNED — not present)
- **Headless core** — the app running without the overlay UI; the only mode that works today. `--headless` (default) / `--ui` (warns, falls back).
- **Plugin** — a unit extending the (planned) `BasePlugin` ABC with `setup`/`teardown`/`get_status` and an event emitter. Today only enable **flags** exist (`discord`, `github`, `notion`).
- **Overlay UI** — planned PySide6 frameless always-on-top floating window (`[ui]` extra).
- **OpenCode** — external `opencode serve` REST API (port 4096) that a planned AI plugin would call (routes to GitHub Copilot / OpenAI-compatible providers). (PLANNED)
- **Quality gate** — `scripts/quality_gate.py` + `.quality-gate.json`; records a metrics baseline and verifies no regression in CI.
- **Context files** — generated, non-hand-edited repo digests (`handover.md`, `ai-instructions.md`, `llms-full.txt`, `context-map.json`) produced by `make gen-context-files` per ADR D-0012.
- **Canon / standards** — the chrysa transverse standards (`standards/`, `shared-standards`); "where an annexe and the canon disagree, the canon wins".
- **APE** — an agent-prompt-engineering transform under `.claude/ape/` (v2 project-scope hook). (repo tooling; not product)
- **graphify-out/** — cached output (AST/stat index) from the `graphify` knowledge-graph tooling. (generated cache)
