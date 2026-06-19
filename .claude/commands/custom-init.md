---
description: Generate a comprehensive CLAUDE.md by analyzing the current project
---

# Command: Custom Init

Generate a well-structured `CLAUDE.md` for the current chrysa project through a phased,
parallel specialist analysis.

## Usage

```text
/custom-init
```

## Relationship to native `/init`

Claude Code ships a built-in `/init`. `/custom-init` reaches the same goal through an
explicit phased workflow (staged analysis, per-feature detection, versioned stack inventory,
consistent section order) and seeds the result from `@templates/CLAUDE.md`. Pick whichever
fits — they are alternatives, not a hierarchy.

## Agents Used

The main session orchestrates and dispatches each pass to the best-fit specialist via the
Task tool (each in its own context window). Use **general-purpose** only as a fallback.

- **general-solution-architect** — Phase 2 (architecture + stack).
- **general-backend-developer** — Phase 3 backend passes (auth, domain, data access, comms).
- **general-devops** — Phase 3 infrastructure + Phase 4 deployment.
- **general-qa** — Phase 4 testing.
- **general-code-quality-debugger** — Phase 4 troubleshooting.
- **general-technical-writer** — Phase 4 docs discovery + Phase 5 assembly.

Phases 0–1 run inline. Phases 2–4 dispatch in **one message** and run concurrently.
Phase 5 is sequential — it consumes 2–4's outputs.

## Phase 0 — Initialization
- Validate the cwd is a project root; check for an existing `CLAUDE.md`.
- Detect available tooling (`git`, `docker`, `make`, language toolchains).
- Respect `.gitignore`; comprehensive scan.

## Phase 1 — Project Discovery
- Detect project type from build files (`pyproject.toml`, `package.json`, `go.mod`, `*.csproj`…).
- Identify primary language/framework; map directory structure; find existing docs.

## Phase 2 — Core Sections *(general-solution-architect)*
- Overview & Quick Start (from README / package metadata; chrysa Makefile targets — `make install`, `make dev`, `make test`).
- Architecture (map layout to patterns: DDD, Clean, MVC…; layers and boundaries).
- Technology Stack (parse dependency files for exact versions; dev vs prod; infra from compose/k8s).

## Phase 3 — Feature Analysis (parallel fan-out)
One specialist subagent per pass, dispatched together:
1. **Authentication** *(backend)* — middleware, login routes, token handling.
2. **Business Domain** *(backend)* — entities, aggregates, services, use cases.
3. **Data Access** *(backend)* — ORM/repositories, migrations, connection config.
4. **Communication** *(backend)* — controllers/routes, integrations, messaging.
5. **Infrastructure** *(devops)* — compose/k8s/Terraform → service map with ports.

## Phase 4 — Additional Sections (parallel fan-out)
1. **Testing** *(qa)* — frameworks, test counts by type, **Docker/Makefile** test commands.
2. **Deployment** *(devops)* — CI/CD (`.github/workflows`), deploy scripts, env config.
3. **Troubleshooting** *(code-quality-debugger)* — `TODO`/`FIXME`/`HACK`, known issues, error patterns.
4. **Documentation** *(technical-writer)* — OpenAPI/Swagger, markdown docs, external links.

## Phase 5 — Assembly *(general-technical-writer)*
- Combine outputs; consistent markdown; order by priority; add nav links.
- Verify commands are executable (Docker/Makefile) and paths correct.
- Write `CLAUDE.md`. If one exists, back it up as `CLAUDE.md.backup` and reuse accurate content.

## Best Practices
- Keep `CLAUDE.md` accurate — stale context is worse than none.
- Reference shared files with the `@` prefix (e.g. `@templates/CLAUDE.md`) instead of duplicating.
- Document what is non-obvious, not what Claude can already read from the code.
