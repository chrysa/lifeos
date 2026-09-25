# DECISIONS — lifeos

> Index of architectural decisions. Full ADRs live in `docs/adr/`. Tags:
> **FACT** (recorded in the repo), **INFERENCE**, **UNKNOWN**, **PROPOSAL**.

## Recorded ADRs

### ADR-LIFEOS-001 — LifeOS is a capability pack consumed by LOGOS (FACT)

- **Status:** Accepted (2026-09-06). Source: `docs/adr/ADR-LIFEOS-001-capability-pack-of-logos.md`.
- **Decision:** `lifeos` is the canonical repo (retires/archives the `my-assistant`
  fork). LifeOS is a **standalone capability pack, not a git submodule of LOGOS**;
  it publishes `personal.*` capability manifests that LOGOS discovers, consumes
  and governs. The two talk through **versioned capability contracts**, never
  shared source.
- **Scope boundary (FACT):** LifeOS owns personal business capabilities; LOGOS
  owns orchestration, memory, policy, and the conversational client. LifeOS has
  no generalist assistant, no personal memory, no Policy Engine, no autonomous
  conversational client. Per the ADR, LifeOS must **not** access Notion (or other
  sources) directly — LOGOS brokers data and governance.
- **Consequences (FACT, follow-ups pending):** recadrer `README.md` to drop the
  "floating AI assistant / my-assistant" identity, and define the `personal.*`
  manifests. Neither follow-up has landed (see REVIEW.md contradiction #2).
- **Fatal hypothesis (FACT, quoted):** if LOGOS never ships a capability host,
  LifeOS has no consumer and the boundary is premature — revisit if LOGOS stalls.

## Open scope question — lifeos ↔ LOGOS / floating-agent (UNKNOWN)

The current README, CLAUDE.md and `pyproject.toml` describe a self-contained
"floating AI assistant" (overlay UI, AI routing, messaging/service plugins),
which is the **superseded** identity. ADR-LIFEOS-001 moves those responsibilities
to LOGOS and reduces LifeOS to a published capability pack. Until the recadrage
lands and the `personal.*` manifests exist, the true surface of LifeOS — and
which of the planned plugins survive as capabilities vs. move to LOGOS — is
**UNKNOWN**. The mission's note about the agent-scope boundary (D-0002) maps onto
this LifeOS/LOGOS split; no `D-0002` document is present in this repo (UNKNOWN).

## Decisions visible in config but not written up as ADRs (INFERENCE)

- **ruff targets `py313`, not `py314`** — deliberate: a comment in `pyproject.toml`
  notes ruff-format ≤0.15.15 strips multi-except parens under py314; restore when
  fixed upstream. (FACT: comment present.)
- **Coverage gate `--cov-fail-under=85`** (`pyproject.toml`). (FACT.)
- **Container tests only** via `Dockerfile.test` (`python:3.14-slim`); no
  production Dockerfile or compose file in the repo. (FACT.) Whether a production
  container is planned is UNKNOWN — the capability-pack model may not need one.

## Not decided here / no evidence (UNKNOWN)

- Repo **profile** and **DDD level** are declared "(not available)" in
  `handover.md` — the standards require them but they are unset.
- Choice of plugin mechanism (the `github-inspiration.md` reference weighs
  py-gpt / pluggy / litellm) is **exploration, not a decision** — PROPOSAL only.
