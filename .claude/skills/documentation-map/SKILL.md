---
name: documentation-map
description: "Procedure: Documentation map. Use when this procedure is needed."
---

Root docs (reverse-engineered 2026-09-25, docs-only pass):

- `README.md` — quickstart + honest status table
- `ARCHITECTURE.md` — stack, layout, entrypoints (pre-existing, accurate)
- `REQUIREMENTS.md` — REQ-PROD / REQ-TECH matrix (IMPLEMENTED vs PLANNED)
- `CONSTRAINTS.md` — platform/language/security/process/arch constraints, tagged
- `DECISIONS.md` — ADR index (ADR-LIFEOS-001 + reconstructed decisions)
- `TESTING.md` — pytest layout, coverage gate, commands
- `SECURITY.md` — secret-handling baseline + findings (no HIGH/CRITICAL)
- `OBSERVABILITY.md` — logging + Sentry
- `ROADMAP.md` — shipped vs planned (repo-stated only)
- `GLOSSARY.md` — terms (lifeos, LOGOS, capability pack…)
- `REVIEW.md` — contradictions, doc debt, lifeos/LOGOS overlap
- `docs/adr/ADR-LIFEOS-001-*` — canonical/capability-pack decision

Key open tension (see REVIEW.md): ADR-LIFEOS-001 retires this `my-assistant`
identity in favour of the canonical `lifeos` repo + LOGOS capability-pack model,
but README/CLAUDE/pyproject still describe the old "floating assistant" product.


<!-- chrysa:standards:start · managed by distribute-standards.sh · DO NOT EDIT -->
# chrysa — Transverse Standards (core)

> The **slim always-on core**. The canonical, tool-agnostic source of truth is `standards/STANDARDS.chrysa.md`; the normative annexes live under `standards/annexes/`. Each rule below is a one-line pointer — its full text lives in the per-domain file named beside the heading (`standards/rules/<domain>.md`), read on demand.

**Where an annexe and the canon disagree, the canon wins.**

### Governance, language & compliance · `standards/rules/governance.md`
- Normative annexes
- Language
- Compliance targets
- Governance — strategic pillars & ADR format

### Cross-cutting stack · `standards/rules/stack.md`
- Cross-cutting stack (settled ADRs — do not relitigate)

### SCM — branches, commits & pull requests · `standards/rules/scm.md`
- Commits
- Branches
- Branch model — `main` is production, `develop` is the workspace
- Merge
- One PR per issue
- Every PR references a Shortcut story
- Issues and PRs are type-driven

### Architecture, decoupling & portability · `standards/rules/architecture.md`
- Repo provenance — every code repo depends on `project-init`
- Every repo declares its profile and DDD level
- Projects talk through versioned contracts only
- Everything is machine-agnostic and portable — no rule, repo, or script is bound to one machine
- Every external server the service talks to is addressed through the environment — never hardcoded
- Every tracked file and folder must earn its place — a repo holds only what is useful to it now
- The repository architecture is legible to an agent — optimised for Claude, not only for humans
- Deferred work is a governed job, not a fire-and-forget

### Testing · `standards/rules/testing.md`
- Tests: pytest only
- Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later

### Frontend & web semantics · `standards/rules/frontend.md`
- TypeScript is strict by contract
- The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden
- React is a presentation layer, not the domain
- The frontend says when the backend is unreachable or unstable
- The frontend is reactive and real-time by default
- UI state survives reload & focus
- Everything is semantic — the markup, the data, and the URLs
- URL-addressable frontend navigation — mandatory

### APIs, contracts & real-time · `standards/rules/api.md`
- A real-time backend has channel contracts and never blocks
- APIs, SDKs & public contracts follow the `STD-API-001` contract

### Accessibility · `standards/rules/accessibility.md`
- Dark mode
- Every site is usable by the majority of disabilities — not only the screen-reader case

### Documentation & session state · `standards/rules/docs.md`
- Notion logging
- Documentation and Notion are maintained in lockstep with the code — a change that leaves them stale is unfinished
- Every repo ships generated context files
- Session lifecycle (primer + memory + hindsight)

### AI agents & features · `standards/rules/agents.md`
- Agent actions are governed
- An AI feature is evaluated, not just shipped
- An agent writes only where the owner owns

### Security, identity & sessions · `standards/rules/security.md`
- Per-person data implies a user account — no exceptions dressed up as simplicity
- Identity goes through the cluster SSO first
- Rights are resolved against the common directory (LDAP), never re-declared per service
- A session is secured and it expires
- Every form is a hostile input surface — validate on the server, always
- Security scanning is a gate, not an afterthought — it runs in pre-commit and in CI

### Code quality & anti-patterns · `standards/rules/code-quality.md`
- No hardcoded constants
- No literal HTTP status codes — use the constants the framework already ships
- No code duplication — the second occurrence is an extraction order
- Raised errors are typed
- Failures are contained, and observable
- Prefer a lookup table to a state machine
- Decompose into small, independently unit-testable methods
- Code is read far more often than it is written — optimise for the reader, and standardise the form
- Avoid lambdas and anonymous constructs — a named function is the default
- Basic optimisations and known anti-patterns are caught in review and in CI
- A cache is a correctness contract, not a sprinkle of speed
- Quality gates
- Error handling pattern (all automations)

### Backend Python · `standards/rules/backend-python.md`
- Python packaging — `pyproject.toml` is the single source of truth
- Python is written object-oriented, one class per file
- Import the item, not the module — `from x import y; y()`
- Functions and methods are called with named arguments — positional call sites are the exception, not the rule

### Data, persistence & migrations · `standards/rules/data.md`
- Data, persistence & migrations follow the `STD-DATA-001` contract

### Observability & operations · `standards/rules/observability.md`
- Observability & production readiness follow the `STD-OPS-001` contract
- The container is versioned separately from the application it hosts, and an admin can see what is actually deployed
- Observability — error-tracking → GitHub issues (norm)

### Containers & compose · `standards/rules/containers.md`
- Everything runs in a container — the only exception is the slice of a repo genuinely bound to the host OS
- External dependencies are installed in containers, never on the host
- No virtualenv in a repo — ever
- Tool caches & deps never touch the project tree
- Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory
- App containers ship the app only — the platform layer is the owner's responsibility
- Only a publicly useful port is published — everything else stays on the container network
- A compose file is minimal — declare only what the stack needs, default the rest
- Dev stage must hot-reload
- Local dev runs the code in-container, live, in debug mode — never the production server
- Default to dev mode when starting an app locally — any other mode only when explicitly asked
- `.dockerignore` mandatory & exhaustive
- Container-runtime policy

### Product surfaces · `standards/rules/product.md`
- Setup wizard & config panel
- A game is DRM-free and fully playable solo offline
- Every product that is operated ships a management backoffice
- If a user can supply a file, the product accepts an upload
- A floating assistant where it earns its place — never as decoration

### Design system · `standards/rules/design.md`
- Design system

### Developer loop & tooling · `standards/rules/dev-loop.md`
- Makefile targets
- Shared skills (load on demand from shared-standards/.claude/skills/)

### CI/CD, pre-commit & release · `standards/rules/ci-cd.md`
- Release & changelog config (canonical)
- GitHub Actions (reuse first · custom actions centralised · thin workflows)
- Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)

### Local AI orchestration & local-first · `standards/rules/ai-orchestration.md`
- AI orchestration & local-first
<!-- chrysa:standards:end -->
