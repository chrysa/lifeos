#!/usr/bin/env node
/**
 * Model-specific tech debt inventory tool.
 *
 * Scans .claude/ (rules, prompts, skills, CLAUDE.md) for @[MODEL_NAME] tags
 * and produces an inventory of model-dependent rules.
 *
 * Usage:
 *   node model-debt-inventory.cjs [--dir <path>] [--json]
 *
 * Options:
 *   --dir   Root directory to scan (default: current working dir)
 *   --json  Output as JSON instead of human-readable table
 *
 * Tagging convention in rules/prompts/skills/CLAUDE.md:
 *   @[claude-opus-4]
 *   @[claude-sonnet-4]
 *   @[gpt-4o]
 *   @[gemini-2-flash]
 *   etc.
 *
 * Example:
 *   // This rule only applies when using @[claude-sonnet-4]
 *   - Keep responses under 200 words
 *
 * @tag @[claude-sonnet-4]
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ── CLI ───────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const JSON_OUTPUT = args.includes("--json");
const dirFlagIdx = args.indexOf("--dir");
const ROOT_DIR =
  dirFlagIdx >= 0 && args[dirFlagIdx + 1]
    ? path.resolve(args[dirFlagIdx + 1])
    : process.cwd();

// ── Tag pattern ────────────────────────────────────────────────────────────────
const MODEL_TAG_PATTERN = /@\[([a-zA-Z0-9._-]+)\]/g;

// ── File discovery ─────────────────────────────────────────────────────────────
function findScanTargets(rootDir) {
  const results = [];
  const INCLUDE_DIRS = [".claude", ".github/copilot-instructions"];
  const INCLUDE_FILES = ["CLAUDE.md", "copilot-instructions.md"];
  const INCLUDE_EXT = [".md", ".txt", ".json", ".cjs", ".sh", ".yml", ".yaml"];

  function walk(dir) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (INCLUDE_EXT.includes(path.extname(entry.name))) {
        results.push(full);
      }
    }
  }

  for (const d of INCLUDE_DIRS) {
    walk(path.join(rootDir, d));
  }
  for (const f of INCLUDE_FILES) {
    const full = path.join(rootDir, f);
    if (fs.existsSync(full)) results.push(full);
  }

  return [...new Set(results)];
}

// ── Tag extraction ─────────────────────────────────────────────────────────────
function extractTags(filePath, rootDir) {
  const findings = [];
  let content;
  try {
    content = fs.readFileSync(filePath, "utf8");
  } catch {
    return findings;
  }

  const lines = content.split("\n");
  lines.forEach((line, idx) => {
    const tagPattern = new RegExp(MODEL_TAG_PATTERN.source, "g");
    let match;
    while ((match = tagPattern.exec(line)) !== null) {
      findings.push({
        model: match[1],
        file: path.relative(rootDir, filePath),
        line: idx + 1,
        context: line.trim().slice(0, 120),
      });
    }
  });
  return findings;
}

// ── Main ───────────────────────────────────────────────────────────────────────
function main() {
  const files = findScanTargets(ROOT_DIR);
  const allFindings = [];

  for (const f of files) {
    allFindings.push(...extractTags(f, ROOT_DIR));
  }

  if (JSON_OUTPUT) {
    process.stdout.write(JSON.stringify(allFindings, null, 2) + "\n");
    return;
  }

  if (allFindings.length === 0) {
    process.stdout.write(
      "No @[MODEL_NAME] tags found.\n\n" +
        "To tag a rule as model-specific, add a comment like:\n" +
        "  // @[claude-sonnet-4]\n" +
        "  # @[gpt-4o]\n"
    );
    return;
  }

  // Group by model
  const byModel = {};
  for (const f of allFindings) {
    (byModel[f.model] = byModel[f.model] ?? []).push(f);
  }

  const lines = [
    "Model-Specific Tech Debt Inventory",
    "═".repeat(60),
    `Scanned: ${files.length} file(s) in ${ROOT_DIR}`,
    `Found: ${allFindings.length} tag(s) across ${Object.keys(byModel).length} model(s)`,
    "",
  ];

  for (const [model, entries] of Object.entries(byModel).sort()) {
    lines.push(`┌─ @[${model}] — ${entries.length} reference(s)`);
    for (const e of entries) {
      lines.push(`│  ${e.file}:${e.line}`);
      lines.push(`│    ${e.context}`);
    }
    lines.push("");
  }

  process.stdout.write(lines.join("\n") + "\n");
}

main();
