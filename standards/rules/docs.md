<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Documentation & session state

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Notion logging**: every advancement and modification (progress, decisions, state
  changes) is logged in Notion — the single source of truth **for project state**. Run
  `@notion-sync` after any state change; on conflict about project state, Notion wins.
  This does **not** apply to the standards corpus: there the repo is the canon and Notion is
  a governance view (annexe `GOVERNANCE.md` GV-000).

- **Documentation and Notion are maintained in lockstep with the code — a change that leaves
  them stale is unfinished.** Keeping the docs and the project's Notion current is an
  **obligation of every change**, part of the same unit of work, never a later cleanup.
  Concretely, in the **same PR** as a behaviour or interface change:
  1. **The affected documentation is updated** — the repo `README.md` and the per-folder
     `README.md` (folder-readme rule), the `docs/` pages (MkDocs), the ADR for the *why*, the
     API/contract docs, and the setup/ops runbook. `README.md` always reflects the **actual
     current state** (updated at least each release); a `primer.md`/session-state file, where
     the repo carries one, is refreshed too.
  2. **Notion is updated** — every advancement, decision or state change is logged per the
     *Notion logging* rule above (Notion is the source of truth for **project state**;
     `@notion-sync` after any state change). A state change that never reaches Notion is a
     lie by omission about where the project stands.
  Stale documentation is a defect on par with a failing test: a doc that describes behaviour
  the code no longer has misleads every future reader — human or agent — and an agent that
  trusts it acts on a falsehood (this is why *the repository is legible to an agent* depends on
  it). The Definition of Done for any change therefore includes **"the docs and the Notion it
  touches are current"**; a PR that changes behaviour without touching a single doc, or a state
  change never reflected in Notion, is incomplete — reviewers reject it. The one carve-out is
  the standards corpus itself (this repo): there the repo is canon and Notion is only a
  governance view (`GV-000`).

## Session lifecycle (primer + memory + hindsight)

A repo **may** carry a session lifecycle so an AI agent keeps context across sessions. The
substance is a set of **committed files**, not a required Make target — the convention below is
what matters; any `make`/slash-command wrappers are an **optional convenience** provided where a
repo has them, not a universal socle target every Makefile must expose.

- `primer.md` (committed) — current state, what to do NOW; read **before** `CLAUDE.md`.
- `.claude/memory/session.md` — volatile session notes, **not** committed (reset each session).
- `.claude/memory/decisions.md`, `known-issues.md`, `progress.md` (append-only history) — committed.
- **Session start** — surface the primer + git context + open PRs (a `prepare` wrapper where present).
- **Session end** — update `primer.md` + `progress.md`, clear `session.md` (a `hindsight` wrapper
  where present), optional Obsidian export.

> **Not a mandated Make target.** `memory-init` / `prepare` / `hindsight` are convenience
> wrappers, not part of the canonical Makefile socle contract (*Makefile targets*), and are not
> assumed to exist in every repo. A repo governs its session state through the committed files
> above; the wrappers and their scripts are added per repo when useful.
