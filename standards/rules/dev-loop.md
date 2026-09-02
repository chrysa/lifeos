<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Developer loop & tooling

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

## Makefile targets

- **Referential**: `Forge-Stack-Workshop/base-makefile` (`Makefile.basic`, `Makefile.python`,
  `Makefile.with-sub-folder`) is the single source of truth for target names and behaviour.
- **Canonical naming** — follow base-makefile verbatim, one word where it is one word:
  `typecheck` (**never** `type-check`), `test-cov`, `format-check`, `quality-gate-verify`,
  `docker-test`, `ci`. Renaming or aliasing a canonical target is forbidden.
- **Mandatory socle** — every application repo MUST expose, with these exact names and intent:
  `help install install-dev lint format format-check typecheck test test-cov pre-commit clean
  ci quality-gate-baseline quality-gate-verify`. Non-applicative repos (pure infra/Helm/Terraform,
  config-only, docs) are exempt from the language-specific targets (`typecheck`, `test-cov`) but
  still expose `help lint pre-commit clean`.
- **Docs must match** — every `make <target>` cited in `CLAUDE.md` or `README.md` MUST exist in
  the Makefile (no `make type-check` when the target is `typecheck`).
- **Recipe style** — prefix every recipe line with `@`; add `## Description` after each target so
  it appears in `make help`.
- **Modular Makefiles — 500 lines max, split by domain.** No hand-maintained Makefile exceeds
  **500 lines** (the same file gate as code). Approaching the limit, it is split into thematic
  files under `make/` (`make/common.mk` for shared variables/functions, then `docker.mk`,
  `test.mk`, `quality.mk`, `k8s.mk`, `docs.mk`… as the repo needs), loaded explicitly from the
  root Makefile with `include` / `-include`. The **root Makefile stays an entry point and an
  orchestrator**: it exposes the main commands, loads the thematic files, and serves the global
  `make help`. A target exists **in exactly one file** — duplicates, near-identical variants and
  copy-paste between thematic files are forbidden (*no code duplication* applies to Make too).
  Inclusion is acyclic: a thematic file never includes back into its parent. Target names stay
  predictable and grouped by domain (`test-unit`, `docker-build`, `k8s-deploy`), every public
  target is documented in `make help` from its `## Description`, and any long or business-logic
  recipe moves to a **versioned, testable script** — the Makefile is a command surface, not an
  application language.

## Shared skills (load on demand from shared-standards/.claude/skills/)

- `testing-pytest` — pytest DDD + pytest-mock + constants (writing tests)
- `dockerfile-multistage` — 4-stage Python 3.14 containers (editing Dockerfile)
- `api-design` — REST standards + FastAPI patterns (designing endpoints)
- `async-patterns` — async FastAPI + SQLAlchemy async sessions (async code)
- `clean-architecture` — FastAPI module/layer structure (adding a feature)
- `error-handling` — FastAPI errors + the error-tracking service + logging (handling errors)
- `contract-testing` — library contract / breaking-change tests (@chrysa/* releases)
- `agent-patterns` — the agent-orchestration library + the structured-output library + Claude API (building agents)
- `ui-ux` — UX/UI/ergonomics + WCAG 2.1 AA + dark mode + i18n (human-facing surfaces)
- `accessibility` — per-disability-category contract + testable DoD (any surface, incl. public micro-sites)
