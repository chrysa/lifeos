---
name: review-changes
description: Review the uncommitted diff for bugs, missing tests, security issues and violations of this repository's AGENTS.md conventions. Use when asked to review changes before a commit or PR.
allowed-tools: Bash(git diff *) Bash(git status *) Read Grep Glob
---

## Changes

!`git diff HEAD --stat`

## Instructions

1. Read the full diff (`git diff HEAD`) and the files it touches.
2. Check against AGENTS.md conventions, then: correctness, error handling, tests covering
   the change, secrets or credentials, injection, performance traps.
3. Output a list ordered by severity: `file:line - problem - suggested fix`.
   No praise, no restating the diff. If nothing is wrong, say so in one line.
