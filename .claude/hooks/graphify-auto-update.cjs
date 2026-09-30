#!/usr/bin/env node
/**
 * graphify-auto-update — refresh the knowledge graph after pull / branch switch.
 *
 * Wired as a pre-commit `post-merge` + `post-checkout` hook. Runs
 * `graphify update .` detached and non-blocking (AST-only, no API cost) so a
 * `git pull` or `git checkout` returns immediately.
 *
 * No-ops silently when:
 *   - the `graphify` CLI is not on PATH,
 *   - there is no `graphify-out/` directory (repo not graphified),
 *   - post-checkout is a file checkout, not a branch switch.
 *
 * Always exits 0 — never blocks the git operation.
 */

"use strict";

const { spawn, execSync } = require("node:child_process");
const { existsSync } = require("node:fs");

function graphifyOnPath() {
  try {
    execSync("command -v graphify", { stdio: "ignore", shell: "/bin/sh" });
    return true;
  } catch {
    return false;
  }
}

function isBranchSwitch() {
  // pre-commit passes post-checkout args as: <prev_head> <new_head> <branch_flag>
  // branch_flag === "1" means a branch checkout (not a file checkout).
  const args = process.argv.slice(2);
  if (args.length < 3) {
    return true; // post-merge (no args) or unknown → proceed
  }
  return args[2] === "1";
}

function graphifyAutoUpdate() {
  if (!existsSync("graphify-out") || !graphifyOnPath() || !isBranchSwitch()) {
    return;
  }
  const child = spawn("graphify", ["update", "."], {
    detached: true,
    stdio: "ignore",
  });
  child.unref();
}

graphifyAutoUpdate();
process.exit(0);
