<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# APIs, contracts & real-time

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **A real-time backend has channel contracts and never blocks.** The producer/consumer side of a
  real-time system is governed too: every channel carries a **name and a typed, versioned
  contract**; **subscription is decoupled from processing by a bounded buffer** so the receiver
  never blocks on I/O and a slow consumer cannot stall the transport (backlog is a metric with an
  alert); **every call to external infra is guarded** and degrades safely when the dependency is
  down (dependency health is probed on-demand and cached, not hot-polled); **delivery semantics are
  declared** and at-least-once consumers are idempotent; and the **transport is an adapter behind
  the domain's port** (WebSocket/SSE/broker chosen by config, not wired into business code). This is
  the backend twin of the reactive-frontend rule above. Detail: annexe `EVENTING.md` (`EV-nnn`).

- **APIs, SDKs & public contracts follow the `STD-API-001` contract.** A machine-readable
  contract (OpenAPI/AsyncAPI/JSON Schema) is the canonical interface; public versions are
  explicit with a backward-compatibility guarantee and a dated deprecation policy; errors are
  typed with a machine code + correlation id; collections paginate by cursor; responses are
  **hypermedia-driven (HATEOAS)** — each carries at least a `self` link plus the
  authorization-aware links for the actions and related resources reachable next, so a client
  follows links instead of templating URLs from ids; critical writes
  are idempotent; guards (timeouts, sizes, authz) live in the contract; inter-project contracts
  are tested provider **and** consumer side; SDKs track the public contract, never internal
  models; and events/webhooks are identified, versioned, signed, replay-protected, with bounded
  retry + dead-letter. Full rules and gates: annexe
  [`API-CONTRACTS.md`](https://github.com/chrysa/shared-standards/blob/main/standards/annexes/API-CONTRACTS.md)
  (`AP-nnn`) and the `api-design` skill.
