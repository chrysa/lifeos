<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# SCM — branches, commits & pull requests

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Commits**: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`).

- **Branches**: `feature/`, `bugfix/`, `chore/`, `hotfix/`, `release/` · default branch `develop`.

- **Branch model — `main` is production, `develop` is the workspace.** Every repo runs the
  same two long-lived branches, and the mapping is literal, not decorative:
  1. **`main` = the code deployed in production.** It is a **protected branch**: no direct
     push, no force push, no branch deletion; every change arrives through a pull request.
     Reading `main` answers "what is running in prod right now" — nothing else is on it.
  2. **`develop` is the repository's default branch** (the GitHub default, what a clone
     checks out) and the integration target for all work. A repo whose default branch is
     `main` is a defect, not a variant.
  3. **Every feature/bugfix/chore PR targets `develop`.** `feature/x` → PR → `develop`.
     A feature PR opened against `main` is closed and retargeted.
  4. **The only way code reaches `main` is a pull request from `develop`** (or, for a
     production emergency, a `hotfix/` branch — which is merged back into `develop` in the
     same breath so the two never diverge). No other source branch may target `main`.
     **The promotion PR is merged with a merge commit, never squashed** — squashing rewrites
     it as a new commit, so `main` and `develop` diverge at every release and the next
     promotion opens with conflicts. *Squash merge only* governs feature PRs into `develop`;
     the release promotion is the documented exception.
  5. **Production is triggered by a new release**, not by a merge: merging `develop` → `main`
     lands the code, and the deployment is driven by the tagged release (GitVersion tag +
     git-cliff changelog + the release workflow). No manual deploy from a laptop, no push
     that silently ships.
  Protection is configured, not assumed: `main` requires a PR, blocks force-push and
  deletion, and is machine-checked across the fleet by `scripts/audit-branch-policy.sh`.

- **Merge**: squash merge only (exception: the `develop` → `main` release promotion, merged
  with a merge commit) · force push forbidden · auto-merge requires CI + owner.

- **One PR per issue**, scoped tight. Every PR references an issue (`Closes/Fixes/Refs #N`).
  Exception: label `hotfix`. The `enforce-issue-link` workflow is a blocking status check.

- **Issues and PRs are type-driven.** Every issue declares exactly one **type** from a fixed
  taxonomy (bug · feature · enhancement · chore · docs · ci · security · research · epic),
  carried as a canonical label and backed by a committed per-type issue form; every PR's type is
  its Conventional Commit type, and its body carries the fields that type needs (a `fix` shows the
  root cause + a regression test, a `feat` its acceptance criteria + a UI proof, a `refactor` a
  no-behaviour-change attestation, a `perf` a before/after measurement). Templates and labels are
  socle-distributed, not per-repo inventions, and the shape is machine-checked (info-first). A
  free-text issue or a one-line PR is a defect. Detail: annexe `SCM.md` (`SC-nnn`).
