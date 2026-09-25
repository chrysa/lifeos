# Decisions — lifeos (my-assistant)

> ADR index for this repo. The one committed ADR lives under `docs/adr/`; the
> rest are decisions reconstructed from manifests and config (marked as such).
> Where rationale is not written down it is tagged UNKNOWN.

## Committed ADRs

### ADR-LIFEOS-001 — LifeOS is a capability pack consumed by LOGOS, not a submodule
- **Status:** Accepted (2026-09-06). **Supersedes:** retires the `my-assistant` fork (archived 2026-09-06). (FACT)
- **Context:** `my-assistant` and `lifeos` were an accidental fork of the same product (domain `.py` byte-identical bar the fleet-synced `scripts/quality_gate.py`). Two questions: which repo is canonical, and how LifeOS relates to LOGOS (a self-hosted JARVIS-like cognitive partner). Notion fiches are the authority. (FACT, from ADR)
- **Decision:** (1) `lifeos` is the canonical repo; `my-assistant` is retired/archived. (2) LifeOS is a capability pack, a standalone repo that publishes `personal.*` capability manifests which LOGOS discovers, consumes and governs; they talk through versioned capability contracts, never shared source. (FACT)
- **Consequences (open follow-ups, FACT):** drop the "floating AI assistant / my-assistant" identity in README; define `personal.*` manifests; LifeOS must not access Notion/sources directly. Fatal-hypothesis check: if LOGOS never ships a capability host, this boundary is premature.

> Note: this ADR is filed **inside the repo it retires**. The README, CLAUDE.md,
> `pyproject.toml` description and generated context files in this same repo still
> carry the "floating AI assistant / my-assistant" identity the ADR says to drop.

## Reconstructed decisions (implicit — not written as ADRs here)

| ID | Decision | Evidence | Rationale |
| --- | --- | --- | --- |
| DEC-R-01 | Headless-first core; UI is an optional extra | `app.py`, README Status table, `[ui]` extra | Let the app always start without a display (CI, tray, servers) — INFERENCE |
| DEC-R-02 | Click for the CLI, Pydantic v2 for config | `pyproject.toml`, source | chrysa cross-cutting stack — INFERENCE |
| DEC-R-03 | hatchling build backend; ruff + mypy(strict) + pytest toolchain | `pyproject.toml` | chrysa lib-tier defaults — INFERENCE |
| DEC-R-04 | Ruff `target-version = py313` despite `requires-python>=3.14` | pyproject comment | Documented workaround: ruff format ≤0.15.15 strips multi-except parens under py314 (FACT — restore when fixed upstream) |
| DEC-R-05 | Sentry as the observability sink, no-op without DSN | `observability/__init__.py`, `.env.example` | Safe default for dev/CI without secrets — FACT |
| DEC-R-06 | Context files generated, not hand-edited (ADR D-0012 referenced) | file headers, ai-instructions.md | Single generated source of truth — FACT (D-0012 lives in shared-standards, not this repo) |

## Referenced but external decisions

- **ADR D-0012** (context-file generation) is referenced by generated headers but lives in `shared-standards`, not this repo. (FACT)
- Cross-cutting stack / branch model / testing ADRs are pointed to from CLAUDE.md's standards core; their text lives in `standards/rules/*` and the shared canon. (FACT)
