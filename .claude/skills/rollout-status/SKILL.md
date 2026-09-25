---
name: rollout-status
description: "Reports per-repo adoption status of a standards/hook/graphify rollout across a list of target repos: hooks present, version pinned, settings.json shape matches. Read-only status check, not a rollout executor."
when_to_use: "rollout status, which repos have the hook, check adoption, campaign status, has this repo been rolled out, drift check across repos"
metadata:
  version: "1.0.0"
---

# Rollout Status: Adoption Check Across Consumer Repos

Reads a target-repo list and reports per-repo adoption status for a given
rollout item (a hook file, a skill, a `settings.json` shape, a graphify
config). Replaces the ad-hoc one-off scripts each campaign currently
improvises. Read-only — never modifies a target repo.

## Inputs

- **Target list**: a file (one repo path per line) or an explicit list of
  local paths / `owner/repo` slugs.
- **Item to check**: the file(s) that should exist per repo, and optionally
  the canonical version to compare against (defaults to this hub's copy at
  the same relative path).

If no target list is given, ask for one — don't guess which repos are in
scope.

## Procedure

1. For each target repo, resolve a readable path:
   - Local clone: use the path directly.
   - Not cloned: `git show <remote>:<path>` or `gh api repos/<slug>/contents/<path>`
     read-only, if the caller allows a network read.
   - Unreachable: mark `unknown`, don't block the rest of the batch.
2. Check presence: does the item file exist at the expected path?
3. If present and a canonical reference is available, diff it (see the
   `standards-drift-auditor` subagent for deep drift analysis — this skill
   only needs a quick same/differs verdict, not a full classification).
4. Check version pinning where relevant (e.g. a hook file's header comment,
   a package.json/`.mcp.json` version field) — flag unpinned or mismatched
   versions.
5. Check `settings.json` shape: required keys present (e.g. `hooks`, a
   given hook's matcher/command), no structural mismatch vs. the canonical
   settings shape.

## Output

One row per repo:

```
repo                          | item              | status      | note
padam-av                      | secret-scanner.cjs| present/ok  | version matches
padam-av-supervision-interface| secret-scanner.cjs| missing     | no .claude/hooks dir
some-other-repo                | secret-scanner.cjs| unknown     | not cloned, no gh access
```

End with a count summary: N ok, N missing, N stale, N unknown.

## Boundaries

- Never edit a target repo, never commit, never open a PR from this skill —
  status only. Use the standard rollout workflow (worktree + PR) separately
  to actually apply fixes.
- For a full line-level drift diff (not just presence/version), delegate to
  the `standards-drift-auditor` subagent instead of reimplementing diffing
  here.
