# standards/rules

**Role.** On-demand, per-domain detail for the transverse standards. Each `<domain>.md`
holds the full text of the rules the slim core (`CLAUDE.md` / `standards/CORE.chrysa.md`)
only points at. **Every file here except this README is GENERATED** from the canon
(`standards/STANDARDS.chrysa.md`) by `scripts/gen_agent_views.py`.

## Structure

| Path            | Purpose                                                          |
| --------------- | ---------------------------------------------------------------- |
| `<domain>.md`   | Generated full detail for one domain (e.g. `security.md`, `ci-cd.md`). |
| `README.md`     | This file (not generated).                                       |

## Should contain

- Generated `<domain>.md` files only — produced by `make gen-agent-views`.

## Should NOT contain

- Hand-authored rules — edit the canon `standards/STANDARDS.chrysa.md` and regenerate.
  A hand-edit here drifts and is caught by the `agent-views-drift` gate.
- Always-on meta-rules (ADR format, pillars, folder-README) — those live in
  `.claude/rules/`, which the repo auto-loads into every agent session. This folder is
  deliberately **not** auto-loaded, so its detail is paid for only when an agent opens it.

## Rules

- Source of truth is the canon; the domain taxonomy is `standards/rule-domains.yaml`.
- Regenerate with `make gen-agent-views`; the `agent-views-drift` pre-commit hook + CI gate
  fail if any committed file here differs from what the generator produces.
