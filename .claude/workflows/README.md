# workflows

**Role.** Deterministic Claude Code Workflow scripts that orchestrate the shared agents, skills and
commands. Distributed to `<repo>/.claude/workflows/` by `scripts/distribute-standards.sh` (step 4)
and launched by the `/wf-*` commands in `../commands/`.

## Structure

| Path | Purpose |
| --- | --- |
| `feature.js` | W1 · `mode=design` (spec + plan + 3 critics) / `mode=build` (implement + verify loop + review) |
| `bugfix.js` | W2 · 3 root-cause hunters → adjudicated repro test → fix → verify → review |
| `pr-review.js` | W4 · scoped specialist reviewers → dedup → 2 refuters per blocker/major → verdict |
| `fleet-sweep.js` | W6 · read-only per-repo audit pipeline → fleet synthesis |

## Should contain

- Workflow scripts only (plain JavaScript, `export const meta` first) — one per workflow that
  benefits from fan-out or verification loops.

## Should NOT contain

- Human gates, commits, pushes, merges or `gh` mutations — those live in the calling command
  (`../commands/wf-*.md`) so a human approves them.
- Linear "run skill A then B" procedures — write a command instead (W3, W5, W7).

## Rules

- Agents are referenced by the names shipped in `../agents/`; a missing agent type falls back to
  the default subagent (`runAgent`) so the script works in every repo.
- Scripts are managed copies: edit them here, never in a consumer repo.
- Tests and lint run in containers (`make test`, `make lint`), never on the host.
