#!/usr/bin/env bash
# SessionStart hook: print the git state once so the agent need not spend tool calls on it.
# Written by prism-ai-lint. Output stays under ~25 lines. Never fails the session.
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
echo "branch: $(git branch --show-current 2>/dev/null || echo DETACHED)"
git status --porcelain 2>/dev/null | head -15
git log --oneline -3 2>/dev/null
exit 0
