# ADR-LIFEOS-001: LifeOS is a capability pack consumed by LOGOS — a standalone repo, not a submodule

- **Status:** Accepted (2026-09-06)
- **Deciders:** owner
- **Supersedes / Superseded by:** retires the `my-assistant` fork (archived 2026-09-06)

## Context

`my-assistant` and `lifeos` were an **accidental fork** of the same product (the
domain `.py` was byte-identical bar the fleet-synced `scripts/quality_gate.py`;
scaffolding/config had drifted). Two questions had to be settled: which repo is
canonical, and how LifeOS relates to **LOGOS**.

The Notion fiches are the authority:

- **LifeOS** — *"Pack de capacités métier de LOGOS pour les opérations
  personnelles… LifeOS ne possède ni assistant généraliste, ni mémoire
  personnelle, ni Policy Engine, ni client conversationnel autonome ; il publie
  des capacités consommées et gouvernées par LOGOS."*
- **LOGOS** — the self-hosted JARVIS-like cognitive partner (Socle/Plateforme)
  that consumes and governs capabilities.

## Decision

1. **`lifeos` is the canonical repo.** `my-assistant` is retired and archived.
2. **LifeOS is a capability pack, not a git submodule of LOGOS.** It stays a
   standalone repo that **publishes `personal.*` capability manifests**, which
   LOGOS discovers, consumes and governs. The two talk through **versioned
   capability contracts**, never shared source.

## Rationale

- A git submodule would source-couple LifeOS into LOGOS, violating the chrysa
  standard *"projects talk through versioned contracts only"* and the
  capability-manifest model LOGOS already defines.
- The manifest/consumer boundary keeps ownership clean: LifeOS owns the personal
  business capabilities; LOGOS owns orchestration, memory, policy, and the
  conversational client.

## Consequences

- The repo must be **recadré**: drop the "floating AI assistant / my-assistant"
  identity in `README.md`, and define the `personal.*` manifests (follow-up).
- LifeOS must not access Notion (or other sources) directly — it exposes
  capabilities; LOGOS brokers data and governance.
- Fatal hypothesis: if LOGOS never ships a capability host, LifeOS has no
  consumer and this boundary is premature — revisit if LOGOS stalls.
