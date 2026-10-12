#!/usr/bin/env bash
# PreCompact hook — snapshot session state before context compaction.
# Portable scaffold written by prism-ai-lint. Safe to edit or extend.
set -uo pipefail
SNAP_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/pre-compact-snapshots"
mkdir -p "$SNAP_DIR"
SNAP="$SNAP_DIR/snapshot-$(date +%Y%m%d-%H%M%S).md"
{
  echo "# Pre-compact snapshot · $(date -Iseconds)"
  echo "working_dir: $(pwd)"
  if git rev-parse --git-dir >/dev/null 2>&1; then
    echo "branch: $(git branch --show-current 2>/dev/null || echo DETACHED)"
    echo "## Uncommitted changes (preserve)"
    git status --porcelain 2>/dev/null | head -50
    echo "## Recent commits"
    git log --oneline -5 2>/dev/null
  fi
} > "$SNAP" 2>/dev/null || true
exit 0
