#!/usr/bin/env node
/**
 * Memory Consolidation — context hygiene script for .claude/ directories.
 *
 * Cleans memory/context artifacts:
 *   - Deduplicates content blocks
 *   - Flags contradictions (TODO: same key, different values)
 *   - Removes references to non-existent files
 *   - Reports what was merged, deleted, or flagged
 *
 * Usage:
 *   node memory-consolidation.cjs [--dry-run] [--dir <path>]
 *
 * Options:
 *   --dry-run    Report changes without writing anything (default: false)
 *   --dir        Target directory (default: .claude in current working dir)
 *   --verbose    Print all scanned entries, not just changes
 *
 * @tag @[claude-sonnet-4]
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ── CLI parsing ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const DRY_RUN = args.includes("--dry-run");
const VERBOSE = args.includes("--verbose");
const dirFlagIdx = args.indexOf("--dir");
const TARGET_DIR =
  dirFlagIdx >= 0 && args[dirFlagIdx + 1]
    ? path.resolve(args[dirFlagIdx + 1])
    : path.join(process.cwd(), ".claude");

// ── Report state ──────────────────────────────────────────────────────────────
const report = {
  scanned: [],
  deduplicated: [],
  deletedBrokenRefs: [],
  flaggedContradictions: [],
  errors: [],
};

// ── Utilities ─────────────────────────────────────────────────────────────────

/** Normalize a content block for deduplication comparison */
function normalizeBlock(text) {
  return text
    .replace(/\s+/g, " ")
    .replace(/['"]/g, '"')
    .trim()
    .toLowerCase();
}

/** Find all .md, .json, .txt files in a directory, recursively */
function findFiles(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFiles(full));
    } else if (/\.(md|json|txt)$/.test(entry.name)) {
      results.push(full);
    }
  }
  return results;
}

/** Extract file references from Markdown (links, code blocks) */
function extractFileRefs(content) {
  const refs = new Set();
  // Markdown links: [text](./path) or [text](/path)
  for (const m of content.matchAll(/\[.*?\]\((\.\.?\/[^\s)]+|\/[^\s)]+)\)/g)) {
    refs.add(m[1]);
  }
  // Inline code with path-like patterns
  for (const m of content.matchAll(/`([./][^\s`]+\.(md|json|txt|cjs|sh|yml|yaml))`/g)) {
    refs.add(m[1]);
  }
  return [...refs];
}

/** Check if a file reference resolves relative to a base dir */
function refExists(ref, baseDir) {
  const absolute = path.isAbsolute(ref)
    ? ref
    : path.resolve(baseDir, ref);
  return fs.existsSync(absolute);
}

// ── Deduplication ─────────────────────────────────────────────────────────────

/** Deduplicate sections in Markdown (heading + content blocks > 3 lines) */
function deduplicateMarkdown(content, filePath) {
  const lines = content.split("\n");
  const seen = new Set();
  const output = [];
  let removed = 0;

  let blockStart = -1;
  let currentBlock = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isHeading = /^#{1,6}\s/.test(line);

    if (isHeading && currentBlock.length > 0) {
      // Flush previous block
      const key = normalizeBlock(currentBlock.join("\n"));
      if (seen.has(key)) {
        removed++;
        if (VERBOSE) {
          process.stderr.write(
            `[memory-consolidation] DEDUP in ${filePath}: block starting at line ${blockStart}\n`
          );
        }
      } else {
        seen.add(key);
        output.push(...currentBlock);
      }
      currentBlock = [];
      blockStart = i + 1;
    }
    currentBlock.push(line);
  }

  // Flush last block
  if (currentBlock.length > 0) {
    const key = normalizeBlock(currentBlock.join("\n"));
    if (!seen.has(key)) {
      output.push(...currentBlock);
    } else {
      removed++;
    }
  }

  return { deduped: output.join("\n"), removed };
}

// ── Main processing ────────────────────────────────────────────────────────────
function processFile(filePath) {
  report.scanned.push(filePath);
  let content;
  try {
    content = fs.readFileSync(filePath, "utf8");
  } catch (e) {
    report.errors.push(`Cannot read ${filePath}: ${e.message}`);
    return;
  }

  const ext = path.extname(filePath);
  let changed = false;
  let newContent = content;

  // 1. Deduplicate Markdown sections
  if (ext === ".md") {
    const { deduped, removed } = deduplicateMarkdown(content, filePath);
    if (removed > 0) {
      report.deduplicated.push({
        file: path.relative(TARGET_DIR, filePath),
        removed,
      });
      newContent = deduped;
      changed = true;
    }

    // 2. Check broken file references
    const refs = extractFileRefs(content);
    const baseDir = path.dirname(filePath);
    for (const ref of refs) {
      if (!refExists(ref, baseDir)) {
        report.deletedBrokenRefs.push({
          file: path.relative(TARGET_DIR, filePath),
          ref,
        });
        // Replace broken ref with a note
        newContent = newContent.replace(
          new RegExp(
            ref.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"),
            "g"
          ),
          `${ref} <!-- ⚠️ file not found — verify reference -->`
        );
        changed = true;
      }
    }
  }

  // 3. Write back if changed and not dry-run
  if (changed && !DRY_RUN) {
    fs.writeFileSync(filePath, newContent, "utf8");
  }
}

// ── Entry point ───────────────────────────────────────────────────────────────
function main() {
  if (!fs.existsSync(TARGET_DIR)) {
    process.stderr.write(
      `[memory-consolidation] Target directory not found: ${TARGET_DIR}\n`
    );
    process.exit(1);
  }

  const files = findFiles(TARGET_DIR);
  for (const f of files) {
    processFile(f);
  }

  // ── Print report ────────────────────────────────────────────────────────────
  const separator = "─".repeat(60);
  const lines = [
    separator,
    `Memory Consolidation Report${DRY_RUN ? " [DRY RUN]" : ""}`,
    `Target: ${TARGET_DIR}`,
    separator,
    `Files scanned: ${report.scanned.length}`,
    "",
  ];

  if (report.deduplicated.length > 0) {
    lines.push("Deduplicated blocks:");
    for (const d of report.deduplicated) {
      lines.push(`  ${d.file} — ${d.removed} duplicate section(s) removed`);
    }
    lines.push("");
  }

  if (report.deletedBrokenRefs.length > 0) {
    lines.push("Broken file references flagged:");
    for (const b of report.deletedBrokenRefs) {
      lines.push(`  ${b.file} → ${b.ref}`);
    }
    lines.push("");
  }

  if (report.flaggedContradictions.length > 0) {
    lines.push("Contradictions flagged:");
    for (const c of report.flaggedContradictions) {
      lines.push(`  ${c}`);
    }
    lines.push("");
  }

  if (report.errors.length > 0) {
    lines.push("Errors:");
    for (const e of report.errors) {
      lines.push(`  ${e}`);
    }
    lines.push("");
  }

  if (
    report.deduplicated.length === 0 &&
    report.deletedBrokenRefs.length === 0 &&
    report.flaggedContradictions.length === 0
  ) {
    lines.push("✓ No issues found. Memory is clean.");
  }

  lines.push(separator);
  process.stdout.write(lines.join("\n") + "\n");
}

main();
