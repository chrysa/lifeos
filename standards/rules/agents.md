<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# AI agents & features

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Agent actions are governed.** Any feature where an agent *acts* (writes, calls, runs,
  changes state) needs a versioned manifest with typed I/O and a business owner, least
  privilege, a declared risk level R0–R5 with proportionate confirmation and dry-run,
  and a documented idempotency/timeout/limits/circuit-breaker/rollback envelope. Untrusted
  execution is sandboxed with network off by default; no agent auto-merges to `main`.
  Detail: annexe `AGENTIC-CAPABILITIES.md`.

- **An AI feature is evaluated, not just shipped.** An agent *acting* is governed above; an
  AI feature's *output quality* is a separate obligation. Prompts, models, parameters and
  tools are **versioned**; every critical AI task carries an **evaluation dataset** and
  non-regression tests measuring quality, hallucinations, refusals, latency and cost; each
  answer records the model, its version, the prompt and the sources it used, so it can be
  reproduced and audited; and the product degrades to a **fallback model or a no-AI mode**,
  with human validation proportionate to the risk and an explicit policy for what data is
  sent to a model. A feature whose quality is asserted by feel rather than measured is a
  defect. Detail: annexe `AGENTIC-CAPABILITIES.md` AG-012–AG-015.

- **An agent writes only where the owner owns.** An AI agent may open issues, pull requests,
  comments, branches and releases **only on repositories the owner owns** — the `chrysa`
  account and the organisations under the owner's control. On any third-party repository
  (an upstream project, a dependency, a fork's source, a client's repo) an agent **does not
  file an issue, does not comment, does not open a PR**: it drafts the content locally and
  hands it to the owner, who decides whether and how to send it. This is not a permissions
  detail — an issue is a **public act under a human's name**, and a wrong or noisy one costs
  reputation in a community the agent cannot read. The same limit applies to any outward
  channel an agent could reach (email, chat, social, package registries): drafting is free,
  publishing outside the owner's own perimeter is the owner's call. Inside the perimeter,
  the normal rules still hold — one issue per real problem, no duplicate of an open one, and
  every PR references its issue.
