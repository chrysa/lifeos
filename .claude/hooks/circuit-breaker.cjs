#!/usr/bin/env node
/**
 * Circuit Breaker for API calls made by local scripts.
 *
 * Hook type: Generic utility (import and call from other scripts)
 * Also usable as a PreToolUse hook for Bash tool calls that hit external APIs.
 *
 * @module circuit-breaker
 * @tag @[claude-sonnet-4]
 *
 * State file: ~/.claude/circuit-breaker-state.json
 * States: closed (normal) | open (blocked) | half-open (trial)
 *
 * Configuration (env vars):
 *   CB_FAILURE_THRESHOLD   - failures before opening (default: 3)
 *   CB_RESET_TIMEOUT_MS    - ms before half-open trial (default: 60000)
 *   CB_STATE_FILE          - path to state file
 */

"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");

// ── Configuration ─────────────────────────────────────────────────────────────
const FAILURE_THRESHOLD = parseInt(process.env.CB_FAILURE_THRESHOLD ?? "3", 10);
const RESET_TIMEOUT_MS = parseInt(
  process.env.CB_RESET_TIMEOUT_MS ?? "60000",
  10
);
const STATE_FILE =
  process.env.CB_STATE_FILE ??
  path.join(os.homedir(), ".claude", "circuit-breaker-state.json");

const VALID_STATES = ["closed", "open", "half-open"];

// ── State management ──────────────────────────────────────────────────────────
function loadState(circuit) {
  try {
    const raw = fs.readFileSync(STATE_FILE, "utf8");
    const all = JSON.parse(raw);
    return (
      all[circuit] ?? {
        state: "closed",
        failures: 0,
        lastFailureTime: null,
      }
    );
  } catch {
    return { state: "closed", failures: 0, lastFailureTime: null };
  }
}

function saveState(circuit, circuitState) {
  let all = {};
  try {
    const raw = fs.readFileSync(STATE_FILE, "utf8");
    all = JSON.parse(raw);
  } catch {
    // file missing or corrupt — start fresh
  }
  all[circuit] = circuitState;
  fs.mkdirSync(path.dirname(STATE_FILE), { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(all, null, 2), "utf8");
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Returns true if the circuit allows the call to proceed.
 * Automatically transitions open → half-open after the reset timeout.
 */
function canCall(circuit = "default") {
  const s = loadState(circuit);

  if (s.state === "closed") {
    return true;
  }

  if (s.state === "open") {
    const elapsed = Date.now() - (s.lastFailureTime ?? 0);
    if (elapsed >= RESET_TIMEOUT_MS) {
      // Transition to half-open for a trial call
      s.state = "half-open";
      saveState(circuit, s);
      process.stderr.write(
        `[circuit-breaker] ${circuit}: open → half-open (trial)\n`
      );
      return true;
    }
    process.stderr.write(
      `[circuit-breaker] ${circuit}: OPEN — call blocked (retry in ${Math.ceil((RESET_TIMEOUT_MS - elapsed) / 1000)}s)\n`
    );
    return false;
  }

  if (s.state === "half-open") {
    // Allow one trial call
    return true;
  }

  return true;
}

/**
 * Record a successful call. Resets failure count and closes the circuit.
 */
function recordSuccess(circuit = "default") {
  const s = loadState(circuit);
  const prev = s.state;
  s.state = "closed";
  s.failures = 0;
  s.lastFailureTime = null;
  saveState(circuit, s);
  if (prev !== "closed") {
    process.stderr.write(
      `[circuit-breaker] ${circuit}: ${prev} → closed (recovered)\n`
    );
  }
}

/**
 * Record a failed call. Opens the circuit after FAILURE_THRESHOLD failures.
 */
function recordFailure(circuit = "default") {
  const s = loadState(circuit);
  s.failures = (s.failures ?? 0) + 1;
  s.lastFailureTime = Date.now();

  if (s.state === "half-open" || s.failures >= FAILURE_THRESHOLD) {
    s.state = "open";
    process.stderr.write(
      `[circuit-breaker] ${circuit}: OPENED after ${s.failures} failure(s)\n`
    );
  } else {
    s.state = "closed";
    process.stderr.write(
      `[circuit-breaker] ${circuit}: failure ${s.failures}/${FAILURE_THRESHOLD}\n`
    );
  }
  saveState(circuit, s);
}

/**
 * Get current state info for a circuit.
 */
function getState(circuit = "default") {
  return loadState(circuit);
}

/**
 * Reset a circuit manually to closed state.
 */
function reset(circuit = "default") {
  saveState(circuit, { state: "closed", failures: 0, lastFailureTime: null });
  process.stderr.write(`[circuit-breaker] ${circuit}: manually reset to closed\n`);
}

// ── When used as PreToolUse hook (stdin = JSON event) ────────────────────────
if (require.main === module) {
  let raw = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => (raw += chunk));
  process.stdin.on("end", () => {
    let event = {};
    try {
      event = JSON.parse(raw);
    } catch {
      // Not a valid hook event — nothing to do
      process.exit(0);
    }

    // Only act on Bash tool calls that look like API calls
    const toolName = event?.tool_name ?? "";
    const toolInput = event?.tool_input ?? {};
    const cmd = toolInput?.command ?? toolInput?.input ?? "";

    if (toolName !== "Bash" || !cmd) {
      process.exit(0);
    }

    // Detect API-like calls (curl, fetch, wget, python requests, etc.)
    const API_PATTERN = /\b(curl|wget|fetch|requests\.|httpx\.|aiohttp\.)\b/i;
    if (!API_PATTERN.test(cmd)) {
      process.exit(0);
    }

    // Use command hash as circuit name for per-endpoint tracking
    const circuit = cmd.replace(/\s+/g, " ").slice(0, 60);

    if (!canCall(circuit)) {
      // Exit 2 blocks the tool call
      const msg = `[circuit-breaker] Blocked: circuit "${circuit}" is OPEN. Use CB_RESET_TIMEOUT_MS or call reset() to recover.`;
      process.stdout.write(
        JSON.stringify({ type: "result", output: msg }) + "\n"
      );
      process.exit(2);
    }

    process.exit(0);
  });
}

module.exports = { canCall, recordSuccess, recordFailure, getState, reset };
