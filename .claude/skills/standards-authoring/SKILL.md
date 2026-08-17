---
name: standards-authoring
description: 'Use when adding, migrating, or editing a transverse standards domain in chrysa/shared-standards — creating a normative annexe, adding rules under a stable XX-nnn prefix, registering a STD-* domain in GV-015 + domains.yaml, anchoring it in the socle, and reconciling Notion. Load it before touching standards/STANDARDS.chrysa.md, standards/annexes/*, standards/domains.yaml, or GOVERNANCE.md GV-015, and before opening a standards PR.'
---

# Standards authoring — add or migrate a domain

> Codifies the D-0010 / GV-015 taxonomy and the blast-radius discipline. Governs the corpus
> in `chrysa/shared-standards`. Read `standards/annexes/GOVERNANCE.md` (GV-000, GV-001, GV-010,
> GV-015, GV-020, GV-030) first — this skill is the *procedure*, GOVERNANCE is the *law*.

## The two altitudes (D-0010 / GV-015)
- **Domain** `STD-<DOMAIN>-nnn` — the governance unit (adoption status, owner, priority). Tracked
  in Notion + `standards/domains.yaml`.
- **Rule** `XX-nnn` — one deterministic rule, `XX` a stable two-letter prefix owned by exactly
  one home (an annexe, or the socle). Ids are never reused (GV-010).
- Every domain maps to **one home + one prefix** (GV-015). A domain with a `pending` home is a
  **ghost domain** — never mark it `Adopted`.

## Blast radius — know it before you edit
- **Socle** (`standards/STANDARDS.chrysa.md`) is the ONLY inlined artifact (GV-001): editing it
  rewrites the managed block in ~68 consumer repos at the next `distribute-standards`. Keep socle
  edits to a **short reference anchor** (2–3 sentences → the annexe URL), never the full rules.
- **Annexes** (`standards/annexes/*`) are normative but **not inlined**: editing one touches no
  consumer. A rule living only in an annexe with **no socle anchor is a ghost rule** (GV-001).
- **`docs/adr/*`, `GOVERNANCE.md`, `domains.yaml`** — not inlined → blast radius nil.

## Procedure — new / migrated domain
1. **Source in English.** If migrating from the Notion decision, translate — the corpus is
   English-only. Notion is a governance view (GV-000); the repo is canon.
2. **Write the annexe** `standards/annexes/<NAME>.md` following the `TESTING.md` / `DATA-MIGRATIONS.md`
   model: authority callout (`> **Normative annexe.** Authority: STANDARDS.chrysa.md. Domain: STD-…`),
   `XX-nnn` rules, tables. **No numeric values in prose** — reference the per-repo contract (GV-030).
3. **Register the domain** in BOTH:
   - `GOVERNANCE.md` GV-015 table (a row: domain · home · prefix), and
   - `standards/domains.yaml` (id, home, prefix, status, priority).
   The `domains-drift` pre-commit gate fails if the two disagree — they are one source in two forms.
4. **Anchor in the socle** — add a row to the *Normative annexes* table AND a short reference
   anchor in the body linking the annexe by full GitHub URL. (Skip the anchor only when the home
   is an existing already-anchored annexe, e.g. adding rules to `CI-CD.md`.)
5. **No id collision** — `grep -rhoE '\bXX-[0-9]{3}\b' standards/` before choosing numbers.
6. **Gates land as `info`** (GV-020) — any new `guideline-checker` detector is `info` first,
   promoted to `warning`→`error` only once fleet debt is cleared. Never block on introduction.
7. **Reconcile Notion** — mark the domain `Adopted` + link the annexe once its home is real.

## Checklist before the PR
- [ ] Annexe reachable from the socle *Normative annexes* section (no ghost rule).
- [ ] GV-015 row + `domains.yaml` row present and agreeing (`pre-commit run domains-drift`).
- [ ] No `XX-nnn` collision, no existing id renamed.
- [ ] No numeric value duplicated in prose (GV-030).
- [ ] Socle edit? → run `bash scripts/distribute-standards.sh --dry-run <a-consumer>` and confirm
      only the standards block refreshes, no error. State the blast radius in the PR body.
- [ ] Branch `feat/standards-<domain>`, Conventional Commit, one issue, `Closes #N`, base `develop`.
- [ ] PII: the loopback doc example fingerprint shifts when line numbers move — allowlist the new
      hash in `.pii-allowlist.json` if `pii-scan` fails.

## Tooling
- `python -m scripts.check_domains_drift` — GV-015 ↔ domains.yaml gate.
- `scripts/distribute-standards.sh --dry-run <repo>` — preview consumer impact.
- Deterministic rule mechanisation → `chrysa/guideline-checker` (info-mode first).
- Env: Python **3.14**; validate hooks via `pre-commit run <id>` (provisions the 3.14 env),
  not the host interpreter.

## Related
`standards/annexes/GOVERNANCE.md` (GV-*) · ADR `docs/adr/D-0010-standards-id-taxonomy.md` ·
`project-init` standards profiles · the `adr-new` command for the decision record.
