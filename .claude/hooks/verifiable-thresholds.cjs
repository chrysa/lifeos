#!/usr/bin/env node
/**
 * Verifiable Thresholds checker — PostToolUse hook (file writes).
 *
 * After Claude writes a file, checks the written content against
 * measurable quality thresholds defined in thresholds.json.
 *
 * Hook type: PostToolUse — target: Write, Edit, MultiEdit
 * Does NOT block (informative only — exit 0). Prints warnings to stderr.
 *
 * Thresholds are defined in .claude/thresholds.json (see example below).
 *
 * @tag @[claude-sonnet-4]
 *
 * Default thresholds checked:
 *   - max_function_lines: 50
 *   - max_file_lines: 500
 *   - max_cyclomatic_complexity (heuristic): 10
 *   - no_todo_fixme_in_new_code: true (warn on TODO/FIXME added in writes)
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ── Default thresholds ────────────────────────────────────────────────────────
const DEFAULT_THRESHOLDS = {
  max_function_lines: 50,
  max_file_lines: 500,
  max_cyclomatic_complexity: 10,
  no_todo_fixme_in_new_code: true,
  min_test_coverage_pct: null, // null = not checked here (CI only)
  max_lint_warnings: 0,        // informative
};

// ── Load project thresholds ───────────────────────────────────────────────────
function loadThresholds() {
  const configPath =
    process.env.THRESHOLDS_FILE ??
    path.join(process.cwd(), ".claude", "thresholds.json");
  try {
    const raw = fs.readFileSync(configPath, "utf8");
    return { ...DEFAULT_THRESHOLDS, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_THRESHOLDS;
  }
}

// ── Heuristic checks ──────────────────────────────────────────────────────────

/** Count lines in a string */
function lineCount(content) {
  return content.split("\n").length;
}

/**
 * Heuristic cyclomatic complexity: count decision points
 * (if, else if, case, while, for, forEach, catch, &&, ||, ??)
 */
function estimateComplexity(content) {
  const decisionPoints = [
    /\bif\s*\(/g,
    /\belse\s+if\s*\(/g,
    /\bcase\s+/g,
    /\bwhile\s*\(/g,
    /\bfor\s*\(/g,
    /\.forEach\s*\(/g,
    /\.map\s*\(/g,
    /\bcatch\s*\(/g,
    /&&|\|\||\?\?/g,
  ];
  let count = 1; // base complexity
  for (const pattern of decisionPoints) {
    const matches = content.match(new RegExp(pattern.source, "g"));
    if (matches) count += matches.length;
  }
  return count;
}

/**
 * Extract function bodies from JS/TS/Python (heuristic, not AST-based).
 * Returns array of { name, lineCount }
 */
function extractFunctionLengths(content, ext) {
  const results = [];
  if ([".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx"].includes(ext)) {
    // Named functions and arrow functions assigned to variables
    const funcPattern =
      /(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()/g;
    const lines = content.split("\n");
    let match;
    while ((match = funcPattern.exec(content)) !== null) {
      const name = match[1] ?? match[2] ?? "anonymous";
      // Find start line
      const before = content.slice(0, match.index);
      const startLine = before.split("\n").length;
      // Estimate function end by brace depth
      let depth = 0;
      let started = false;
      let endLine = startLine;
      for (let i = startLine - 1; i < lines.length; i++) {
        for (const ch of lines[i]) {
          if (ch === "{") { depth++; started = true; }
          if (ch === "}") depth--;
        }
        if (started && depth === 0) { endLine = i + 1; break; }
      }
      results.push({ name, lineCount: endLine - startLine + 1 });
    }
  }
  if (ext === ".py") {
    const lines = content.split("\n");
    let funcStart = -1;
    let funcName = "";
    let indent = 0;
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(/^(\s*)def\s+(\w+)/);
      if (m) {
        if (funcStart >= 0) {
          results.push({ name: funcName, lineCount: i - funcStart });
        }
        funcStart = i;
        funcName = m[2];
        indent = m[1].length;
      }
    }
    if (funcStart >= 0) {
      results.push({ name: funcName, lineCount: lines.length - funcStart });
    }
  }
  return results;
}

// ── Hook entry point ──────────────────────────────────────────────────────────
let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  let event = {};
  try {
    event = JSON.parse(raw);
  } catch {
    process.exit(0);
  }

  // Only act on write tool calls
  const toolName = event?.tool_name ?? "";
  if (!["Write", "Edit", "MultiEdit"].includes(toolName)) {
    process.exit(0);
  }

  // Get the file path that was written
  const filePath =
    event?.tool_input?.file_path ??
    event?.tool_input?.path ??
    event?.tool_result?.file_path ??
    "";

  if (!filePath || !fs.existsSync(filePath)) {
    process.exit(0);
  }

  const ext = path.extname(filePath);
  const CODE_EXTS = [".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx", ".py"];
  if (!CODE_EXTS.includes(ext)) {
    process.exit(0);
  }

  const thresholds = loadThresholds();
  const content = fs.readFileSync(filePath, "utf8");
  const warnings = [];

  // 1. File length
  const fileLines = lineCount(content);
  if (thresholds.max_file_lines && fileLines > thresholds.max_file_lines) {
    warnings.push(
      `FILE TOO LONG: ${filePath} has ${fileLines} lines (max: ${thresholds.max_file_lines})`
    );
  }

  // 2. Function lengths
  if (thresholds.max_function_lines) {
    const funcs = extractFunctionLengths(content, ext);
    for (const f of funcs) {
      if (f.lineCount > thresholds.max_function_lines) {
        warnings.push(
          `FUNCTION TOO LONG: ${f.name}() has ~${f.lineCount} lines (max: ${thresholds.max_function_lines})`
        );
      }
    }
  }

  // 3. Cyclomatic complexity heuristic
  if (thresholds.max_cyclomatic_complexity) {
    const complexity = estimateComplexity(content);
    if (complexity > thresholds.max_cyclomatic_complexity) {
      warnings.push(
        `HIGH COMPLEXITY: ${filePath} estimated complexity ~${complexity} (max: ${thresholds.max_cyclomatic_complexity})`
      );
    }
  }

  // 4. TODO/FIXME in new code
  if (thresholds.no_todo_fixme_in_new_code) {
    const todoMatches = content.match(/\b(TODO|FIXME|HACK|XXX)\b/g);
    if (todoMatches) {
      warnings.push(
        `TODO/FIXME present: ${todoMatches.length} marker(s) in ${filePath} — resolve or track in issues`
      );
    }
  }

  if (warnings.length > 0) {
    process.stderr.write(
      `[verifiable-thresholds] Warnings for ${path.basename(filePath)}:\n`
    );
    for (const w of warnings) {
      process.stderr.write(`  ⚠ ${w}\n`);
    }
  }

  process.exit(0);
});
