<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Architecture, decoupling & portability

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Repo provenance — every code repo depends on `project-init`.** A repository is
  **created by** the `project-init` / `chrysa-init` CLI (shared-standards) at birth **and
  kept in sync** with it thereafter: the scaffolded socle (Makefile contract, docs skeleton,
  this standards block, shared skills, CI templates) is re-applied by `distribute-standards.sh`,
  never hand-diverged. The socle is modulated by the `repos.yml` `runtime:` tier (application
  → full socle; `exempt:lib` / `exempt:native` → the relevant subset; pure `exempt:config` →
  standards block only, no application scaffold), but no code repo opts out. A repo that is
  neither scaffolded by nor kept in sync with `project-init` is a defect, not a variant.

- **Every repo declares its profile and DDD level** (`project_profile`, `ddd_level`,
  `bounded_context`, `standards_version`) — architecture is proportionate to business
  complexity, and small tools are not over-architected. Detail: annexe `ARCHITECTURE-DDD.md`.

- **Projects talk through versioned contracts only.** No import from a sibling repo, no path
  dependency, no submodule used as a runtime link, no access to another project's database or
  private models. Each consumer wraps the external contract in a local adapter and degrades
  cleanly when the provider is gone. Detail: annexe `PROJECT-DECOUPLING.md`.

- **Everything is machine-agnostic and portable — no rule, repo, or script is bound to one
  machine.** A standard, a Makefile target, a script, a hook, a compose file, or a CI job must
  behave identically on any developer machine, any runner, and the server, with nothing but a
  clone and the sanctioned host tools. Concretely, **forbidden**: absolute paths tied to a user
  or host (`/home/<user>/…`, `/Users/<name>/…`, `C:\Users\…`, a hardcoded workspace root), a
  hostname/IP/mount point of a specific box baked into code or config, an assumption that a tool
  was installed a particular way, and "works because my machine has it" reasoning. Instead:
  paths are relative to the repo root (or resolved from `$(git rev-parse --show-toplevel)` /
  the script's own directory), machine-specific values arrive through **environment variables
  with documented defaults** (`.env.example` committed, `.env` never), and anything the code
  needs is provided by the container image. The same portability applies to the standards
  corpus itself: a rule names a *mechanism* (a hook id, a Makefile target, a workflow), never a
  particular machine, user account, or local directory layout. The test is mechanical: a fresh
  clone on an unknown machine, with git + Docker + pre-commit, must reach a green
  `make ci` — if it needs a manual step that only the owner knows, that is a defect.

- **Every external server the service talks to is addressed through the environment — never
  hardcoded.** The location and credentials of anything the service does not itself own — a
  database, cache, broker, object store, another chrysa service's API, a third-party endpoint, an
  SSO/OIDC issuer, an LLM or inference host — arrive as **environment variables** (host, port, URL,
  DSN, region, secret), read once through the typed config loader (Pydantic Settings on the
  backend, the generated typed env module on the frontend), with a committed `.env.example`
  documenting every key and safe local defaults. A hostname, IP, port, or connection string of an
  external server written as a literal in code, a compose file, or a manifest is a defect: it pins
  the build to one environment and breaks *build once, promote the artefact* — the same image can
  no longer travel from local to CI to prod, because its endpoints are baked in. This is the
  transport-level twin of *no hardcoded constants* and of the *adaptation layer*: the endpoint is
  configuration, the client wrapping it is an adapter, and between two chrysa projects the endpoint
  still resolves to a versioned contract, not a private address (*projects talk through versioned
  contracts only*). Secrets travel by env or a secrets manager, never committed (see the `.env`
  rules) — the variable holds the value, the repo holds only the documented key.

- **Every tracked file and folder must earn its place — a repo holds only what is useful to it
  now.** A repository contains its own source, its tests, config that is actually loaded, docs
  that are current, and the templates it distributes — nothing else. Forbidden in the working
  tree and in git:
  1. **Superseded or archived documents** whose useful content has been folded elsewhere. Git
     history *is* the archive — a file that "governs nothing", an "undistributed annex kept for
     detail", or a `*_OLD` / `*_backup` copy is deleted, not retained "just in case". Recovering
     it is one `git show` away.
  2. **Scratch and one-off notes** — sprint notes, exported Notion/wiki pages, meeting dumps,
     session scratch. Ephemeral state lives in the tracker (Notion is the source of truth), never
     committed to the repo.
  3. **Stray assets** — diagrams, images or files unrelated to *this* repo's own product (a
     portfolio-wide diagram belongs in the portfolio repo, not a library).
  4. **Idea stubs for projects that live elsewhere** — a placeholder README for a future/other
     project is drift; the project gets its own repo when it starts.
  5. **Generated reports that are not a CI baseline** — an audit/report output is gitignored, not
     committed. Only a file diffed by CI as a drift baseline (e.g. `*.baseline`) is tracked.
  The test is mechanical: a file that governs nothing, is loaded by nothing, and is read by no
  current reader does not belong — delete it. When a deletion would leave dangling references,
  the references are repointed in the same change, never left broken. Checked in PR review; a
  file that fails the test is a defect, not clutter to tolerate.

- **The repository architecture is legible to an agent — optimised for Claude, not only for
  humans.** An AI agent reads a repo through a narrow window: it cannot skim thirty files to
  infer a convention. So the layout itself carries the answers, and a repo where an agent has
  to guess is a defect.
  1. **One entry point that says what to do now** — `CLAUDE.md` (repo-specific rules, layered
     over the inlined standards block) plus `primer.md` (current state, next action), read
     before anything else. `AGENTS.md`/`copilot-instructions.md` stay generated from the same
     source, never hand-diverged.
  2. **Every non-trivial folder carries a `README.md`** stating role, structure, what belongs
     in it and — critically — **what must not**, so a file lands in the right layer at write
     time instead of in review.
  3. **Predictable, name-addressable structure** — layers named after the architecture
     (`domain/`, `application/`, `infrastructure/`, `interfaces/`), one class per file with
     the module named after it, test file mirroring the source path. Finding *where* something
     lives is a naming derivation, never a search.
  4. **Small units by contract** — the file/function/complexity gates (500 / 50 / 10) exist so
     a unit fits in one read; the same reason bans god-objects and `utils.py` grab-bags.
  5. **Machine-readable seams** — typed signatures, Pydantic/OpenAPI contracts, YAML config
     with a typed loader, `docs/adr/` for the *why*. An agent should be able to answer "what
     breaks if I change this" from types and contracts, not from tribal memory.
  6. **Task-shaped tooling over prose** — the repeatable operations are `make` targets and
     shared skills (`.claude/skills/`), so an agent invokes a named contract instead of
     reconstructing a command line. Every documented command exists in the Makefile.
  7. **Session continuity** — decisions, known issues and progress live in `.claude/memory/`
     (see *Session lifecycle*), so the next session starts from state, not from scratch.
  The test is mechanical: drop a fresh agent in the repo with no conversation history — it
  must find the entry point, the layer to touch, the command to run and the gate to pass,
  from committed files alone.

- **Deferred work is a governed job, not a fire-and-forget.** Any work pushed to a background
  queue / worker / scheduler is, by contract: **idempotent** (safe to run twice — a redelivered or
  retried job produces no double effect, mirroring `EV-030`); **bounded** — an explicit **timeout**,
  a **bounded retry** with backoff, and a **dead-letter / failure sink** so a poison job neither
  retries forever nor vanishes; and **observable** — a failed or stuck job **surfaces** (a metric,
  an alert, an admin-visible state), it is never swallowed silently. A **scheduled** task has a
  named **owner** and a runbook like any incident source (`OP-020`). No **business capability is
  reachable only through a job with no manual/admin trigger** — an operator must be able to inspect,
  retry, and cancel it from the backoffice (*every product ships a management backoffice*). Jobs are
  deferred *work*; a real-time *stream* is `EVENTING.md` — related, not the same. The queue/broker
  is reached through an adapter (pillar 5), its endpoint from the environment.
