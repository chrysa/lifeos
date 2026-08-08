#!/usr/bin/env node
/**
 * check-no-env-files.cjs — enforce AG-005 (secrets out of git) at write time.
 *
 * Concept lifted from the Rain devkit's `check-no-env-files.sh` / Vault-seed model:
 * a project never ships a `.env`. Config is injected at runtime (env vars, a secret
 * store), never committed and never sitting decrypted in the tree.
 *
 * Two modes:
 *   PreToolUse (Bash → git commit)  — BLOCKS (exit 2) when a `.env`-class file is staged.
 *   CLI  `node check-no-env-files.cjs --ci [dir]`  — scans the tree, exits 1 on any hit
 *                                                    (wire into `make ci` / quality gate).
 *
 * Allowed, never flagged: `*.env.example`, `*.env.sample`, `*.env.template`, `*.env.dist`,
 * and anything under the allowlist file `.claude/no-env-allowlist.json` (array of globs).
 *
 * Best-effort and defensive: any internal error exits 0 (PreToolUse) so it never wedges a
 * session on malformed input — enforcement of record is the `--ci` gate.
 */
"use strict";

const { execSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const BLOCK = 2; // PreToolUse deny
const CI_FAIL = 1; // CLI gate failure

// A path is a secret-bearing env file when its basename is `.env` or starts `.env.`,
// EXCEPT the sample/example/template/dist variants which carry no real secret.
const ENV_RE = /(^|\/)\.env(\.[^/]*)?$/;
const SAFE_SUFFIX_RE = /\.(example|sample|template|dist)$/;

function isEnvSecretFile(p) {
  const base = p.split("/").pop() || p;
  if (!ENV_RE.test("/" + base)) return false;
  if (SAFE_SUFFIX_RE.test(base)) return false;
  return true;
}

function loadAllowlist(root) {
  try {
    const f = path.join(root, ".claude", "no-env-allowlist.json");
    const arr = JSON.parse(fs.readFileSync(f, "utf8"));
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function allowed(p, allowlist) {
  return allowlist.some((glob) => {
    const re = new RegExp(
      "^" + glob.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*") + "$",
    );
    return re.test(p);
  });
}

// ---- CLI / CI mode -----------------------------------------------------------
function ciScan(dir) {
  const root = path.resolve(dir || ".");
  const allowlist = loadAllowlist(root);
  const hits = [];
  const SKIP = new Set([".git", "node_modules", ".venv", "dist", "build", "__pycache__"]);
  (function walk(d) {
    let entries;
    try {
      entries = fs.readdirSync(d, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.isDirectory()) {
        if (!SKIP.has(e.name)) walk(path.join(d, e.name));
        continue;
      }
      const abs = path.join(d, e.name);
      const rel = path.relative(root, abs);
      if (isEnvSecretFile(rel) && !allowed(rel, allowlist)) hits.push(rel);
    }
  })(root);

  if (hits.length) {
    process.stderr.write(
      "AG-005 violation — committed/present .env file(s):\n" +
        hits.map((h) => "  - " + h).join("\n") +
        "\nMove secrets to the runtime injection layer (env vars / secret store). " +
        "Ship a `.env.example` instead.\n",
    );
    process.exit(CI_FAIL);
  }
  process.exit(0);
}

// ---- PreToolUse mode ---------------------------------------------------------
function readHookInput() {
  try {
    return JSON.parse(fs.readFileSync(0, "utf8"));
  } catch {
    return null;
  }
}

function isGitCommit(cmd) {
  return /\bgit\b[^\n]*\bcommit\b/.test(cmd || "");
}

function stagedEnvFiles(root) {
  try {
    const out = execSync("git diff --cached --name-only --diff-filter=ACM", {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    const allowlist = loadAllowlist(root);
    return out
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean)
      .filter((p) => isEnvSecretFile(p) && !allowed(p, allowlist));
  } catch {
    return [];
  }
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes("--ci")) {
    const dir = args.find((a) => !a.startsWith("--"));
    return ciScan(dir);
  }

  const input = readHookInput();
  if (!input) process.exit(0);
  const cmd = input?.tool_input?.command || "";
  if (!isGitCommit(cmd)) process.exit(0);

  const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const hits = stagedEnvFiles(root);
  if (!hits.length) process.exit(0);

  process.stderr.write(
    "BLOCKED (AG-005): commit stages a .env secret file:\n" +
      hits.map((h) => "  - " + h).join("\n") +
      "\nUnstage it (`git restore --staged <file>`), keep secrets out of git. " +
      "Ship `.env.example`. Bypass a false positive via .claude/no-env-allowlist.json.\n",
  );
  process.exit(BLOCK);
}

main();
