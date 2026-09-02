<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Governance, language & compliance

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

## Normative annexes

This file is the **only** artifact inlined into consumer repos. The annexes below are
**equally normative** — they detail rules stated here in short form. They are not inlined;
read them at
`https://github.com/chrysa/shared-standards/blob/main/standards/annexes/`.
Where an annexe and this file disagree, **this file wins**.

| Annexe                    | Scope                                                          |
| ------------------------- | -------------------------------------------------------------- |
| `FRONTEND.md`             | TypeScript config & rules · React layering · frontend architecture · frontend tests |
| `ARCHITECTURE-DDD.md`     | project profiles · DDD levels · layers & aggregates · Python & C#/.NET structure |
| `AGENTIC-CAPABILITIES.md` | agent actions: manifests, risk R0–R5, sandboxing, audit trail   |
| `PROJECT-DECOUPLING.md`   | inter-project contracts, forbidden linkages, degradation        |
| `CONTAINERS-K3S.md`       | reference stage shape · container responsibility · k3s workload baseline |
| `DATA-MIGRATIONS.md`      | data ownership & classification · versioned schemas · safe migrations · rollback · retention/export |
| `OBSERVABILITY-OPS.md`    | probes · OpenTelemetry (replaceable backend) · alerts+runbooks · SLI/SLO · resource envelope · `/version` · production-ready gate |
| `API-CONTRACTS.md`        | machine-readable contract · versioning & deprecation · typed errors · cursor pagination · hypermedia/HATEOAS links · idempotency · contract tests · events/webhooks |
| `TESTING.md`              | common test levels and rules across languages                   |
| `CI-CD.md`                | pipeline architecture · action pinning · least privilege · cost · what the gate proves |
| `SCM.md`                  | type-driven issues & pull requests · taxonomy & labels · per-type templates · shape gates |
| `EVENTING.md`             | real-time channels · typed channel contracts · non-blocking bounded buffers · fail-safe external access · delivery semantics · transport-as-adapter |
| `TOOLING-ECOSYSTEM.md`    | one truth per tool (Shortcut/Sentry/GitHub/Notion/Slack) · native-before-custom integrations · `sc-<id>` cross-tool thread · canonical journeys · anti-patterns |
| `GOVERNANCE.md`           | rule identity, maturity ladder, enforcement rollout, sources of truth |
| `STACK.chrysa.md`         | chrysa's concrete settled stack — the named products/versions implementing the canon's agnostic categories (deliberately NOT tool-agnostic) |

**Source of truth:** the canon lives in this repo. Notion is a governance and decision view
of the standards corpus, not its authority (`GOVERNANCE.md` GV-000). `chrysa/standards` is
deprecated and archived — nothing is added to it, nothing reads from it.

- **Language**: English — all code, comments, docs, instructions, and config files.

## Compliance targets

The fleet is held to two external compliance frameworks. Neither is a separate corpus — each
is operationalised by rules already in this canon; declaring the target names the obligation
those rules must satisfy, and certification is a governance program on top, not a code change.

- **GDPR / RGPD — by construction.** Every product that touches personal data records its
  lawful basis and purpose, minimises and time-bounds what it stores, keeps PII out of logs
  and test data, and supports export / rectification / erasure by a documented command. This
  is *per-person data implies a user account* and *portable personalisation data* applied to a
  legal obligation. Detail: annexe `GOVERNANCE.md` GV-040.
- **ISO/IEC 27001 — the security baseline.** Information security is a governed, documented
  ISMS, not ad-hoc practice. Access control, cryptography, logging and audit, operations and
  change control, supplier security, and incident management each map onto an existing canon
  rule (cluster SSO & session security, secrets handling, observability & audit trail, CI
  gates & protected `main`, project decoupling & supply-chain pinning, typed/contained errors),
  so conformance is reached by satisfying those — not a parallel checklist. The organizational
  artefacts ISO 27001 also demands (ISMS scope, risk assessment & treatment, Statement of
  Applicability, internal audit) are a versioned governance backlog under `docs/`. Detail:
  annexe `GOVERNANCE.md` GV-041.

## Governance — strategic pillars & ADR format

Five non-negotiables hold across every chrysa project, whatever the stack. Breaking one
requires an ADR with a kill-test, not a shrug.

1. **LLM-provider independence** — no vendor SDK in business code; inference goes through a
   local port with **≥2 real, tested adapters** (e.g. Claude + a local model). A prompt that
   only works on one vendor is a bug, not a feature. **"Local model" means a model running on
   the machine or self-hosted** — an interpreter/weights the owner runs (Ollama, llama.cpp, a
   vLLM/TGI server on chrysa infrastructure), never a third-party hosted API dressed up as
   "local". The independence is only proven when one of the tested adapters needs no external
   provider to answer. **Every LLM call — internal or external — goes through the `chrysa-LLM`
   gateway**, never a vendor SDK or raw provider endpoint called directly from a product's
   business code. `chrysa-LLM` *is* the local port of this pillar made concrete across the
   fleet: it owns provider selection and the ≥2 tested adapters, and it is the one place where
   routing, fallback, prompt/model/version pinning, evaluation, cost and token budgets, caching,
   rate limiting and observability live (satisfying the *AI feature is evaluated* and *agent
   actions are governed* obligations once, not per repo). A product calls it as a **versioned
   contract** through a thin local adapter (*projects talk through versioned contracts only*)
   and degrades to a documented no-AI / fallback mode when it is unreachable — it never reaches
   a model by any other path. A direct call to Claude, OpenAI, Ollama, or any inference endpoint
   that bypasses `chrysa-LLM` is a defect, not a shortcut; the single documented exception is
   `chrysa-LLM` itself, which owns the real adapters. Products built *on top of* the gateway —
   e.g. `ai-aggregator`, a showcase/front consuming `chrysa-LLM` — are consumers of this
   contract, not alternative gateways: they route through `chrysa-LLM` like everything else and
   never re-implement provider access. This is the transport-level application of *no code
   duplication* and *external servers addressed through the environment*: the gateway's endpoint
   arrives by env, and the adapters exist once, there.
2. **GAFAM independence** — every managed-cloud dependency has a documented self-hosted exit
   path; the cloud SDK stays confined to an adapter (`BlobStore`, not `S3Client`).
3. **Portable personalisation data** — all user/personal data is exportable to an open format
   (JSON/SQLite) by a documented command; `export → import → export` is idempotent (tested).
   A stored-but-unexportable field needs an ADR.
4. **k8s config in-project** — manifests live in `deploy/k8s/` of the repo; nothing exists
   only inside a running cluster.
5. **Adaptation layer** — no third-party lib/API/service is imported by the domain directly;
   it goes through an adapter whose port is written in the domain's language, not the vendor's.

**ADR format (refutable).** Any structural decision — new external dependency, LLM/cloud
provider choice, breaking public-API change, data-model change, or a pillar exception — gets
one ADR under `docs/adr/` (series named in the local `CLAUDE.md`). Beyond the classic fields,
every chrysa ADR carries three that make it falsifiable:

- **Fatal hypothesis** — the single, falsifiable belief whose falsity invalidates the decision.
  One only; about the real world (cost, latency, a third party), not an internal intention.
- **Kill-test** — the observable, dated signal that proves it wrong: what to measure, which
  threshold, when checked, what happens on breach. Mechanised as a test where possible.
- **Validation gate** — the pre-agreed condition that unlocks the next step, written *before*
  building.

`Killed` is a valid ADR status: the kill-test fired and the hypothesis was false. A corpus with
no `Killed` entry has kill-tests that are too lax. Scaffold a new record with `/adr-new`.
