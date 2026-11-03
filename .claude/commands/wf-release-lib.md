---
description: Release a shared library safely (consumer contract tests → bump → consumer pin PRs)
argument-hint: <library repo> <new version>
---

# Command: Library release workflow (W7)

Release `$ARGUMENTS` (typically chrysa-lib) without breaking consumers.

## Steps

1. Find consumers: `gitnexus` impact analysis on the public API, plus a search of sibling repos
   for the dependency pin.
2. Run the `contract-testing` skill against every consumer. Any red contract → stop and report.
3. Bump the version, update `CHANGELOG.md`, open the release PR (`develop` → `main`) and wait for
   approval.
4. After the release is published, open one pin-update PR per consumer (each referencing its
   Shortcut story), then run `/wf-pr-review` on each.
