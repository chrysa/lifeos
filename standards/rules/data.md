<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Data, persistence & migrations

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Data, persistence & migrations follow the `STD-DATA-001` contract.** Every data category
  declares its owner, system of record and classification; schemas and events are versioned and
  migrations are reproducible, ordered, tested, and safe (`expand → migrate → contract`, snapshot
  before destructive change, a rollback or documented restore per migration); backups are
  restore-tested, and data is exportable to an open format with no vendor lock-in. Full rules and
  gates: annexe [`DATA-MIGRATIONS.md`](https://github.com/chrysa/shared-standards/blob/main/standards/annexes/DATA-MIGRATIONS.md)
  (`DA-nnn`).
