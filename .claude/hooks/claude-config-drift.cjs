#!/usr/bin/env node
/**
 * claude-config-drift — pre-commit advisory (non-blocking).
 *
 * Warns when tracked `.claude/` shared-config files have uncommitted changes
 * (modified but not staged, or staged partially) so they can be committed
 * separately as `chore(claude): ...` to keep every workstation aligned.
 *
 * Scope: only files under `.claude/` that git already tracks. Ignored local
 * artifacts (state/, sessions/, worktrees/, settings.local.json) are never
 * reported because git does not track them.
 *
 * Always exits 0 — this never blocks a commit.
 */

"use strict";

const { execSync } = require("node:child_process");

const CLAUDE_PREFIX = ".claude/";

function gitLines(command) {
  const output = execSync(command, { encoding: "utf8" });
  return output.split("\n").filter((line) => line.length > 0);
}

function claudeConfigDrift() {
  // Porcelain v1: XY<space>path. Y = worktree status (unstaged changes).
  const statusLines = gitLines("git status --porcelain -- .claude");
  const unstaged = statusLines
    .filter((line) => {
      const worktreeStatus = line.charAt(1);
      return worktreeStatus !== " " && worktreeStatus !== "";
    })
    .map((line) => line.slice(3))
    .filter((path) => path.startsWith(CLAUDE_PREFIX));

  if (unstaged.length === 0) {
    return;
  }

  const header = "⚠️  Claude config drift: shared .claude/ files changed but not staged";
  const hint = "   Commit them separately:  git add .claude && git commit -m \"chore(claude): sync config\"";
  const files = unstaged.map((path) => `   - ${path}`).join("\n");
  process.stderr.write(`${header}\n${files}\n${hint}\n`);
}

claudeConfigDrift();
process.exit(0);
