#!/usr/bin/env node
/**
 * Frustration Detection — UserPromptSubmit hook.
 *
 * Detects frustration/debug markers or continuation requests in prompts
 * and injects context that adjusts Claude's response style.
 *
 * Hook type: UserPromptSubmit
 * Does NOT block (exit 0 always). Injects context via stdout JSON.
 *
 * @tag @[claude-sonnet-4]
 *
 * Logic:
 *   - Frustration markers → inject "be direct, short, resolution-oriented" context
 *   - Continuation markers → inject "continue without summary" context
 *   - Debug markers → inject "give root cause + minimal fix" context
 */

"use strict";

// ── Pattern definitions ────────────────────────────────────────────────────────
const FRUSTRATION_PATTERNS = [
  /\bwhy (?:isn'?t|doesn'?t|won'?t|can'?t|don'?t)\b/i,
  /\bstill (?:not|broken|failing|wrong)\b/i,
  /\b(?:again|still|yet again|once more)\b.*(?:wrong|broken|fail)/i,
  /\b(?:ugh|argh|wtf|ffs|come on|seriously)\b/i,
  /\bnothing works?\b/i,
  /\bi(?:'ve)? (?:tried|already tried)\b/i,
  /\bplease just\b/i,
  /[!]{2,}/,
];

const CONTINUATION_PATTERNS = [
  /^\s*(?:continue|keep going|go on|proceed|finish(?:ing)?|next step|and then[?]?)\s*[.!?]*\s*$/i,
  /\bfinish (?:this|it|the (?:task|work|implementation))\b/i,
  /\bdon['']?t (?:stop|summarize|repeat|recap)\b/i,
];

const DEBUG_PATTERNS = [
  /\b(?:debug|traceback|stacktrace|stack trace|error:|exception:|error message)\b/i,
  /\b(?:why is |what is causing |what caused |root cause)\b/i,
  /\b(?:failing|crashes|broken pipeline)\b/i,
];

// ── Matching helpers ──────────────────────────────────────────────────────────
function matches(text, patterns) {
  return patterns.some((p) => p.test(text));
}

// ── Context injection builders ────────────────────────────────────────────────
function frustrationContext(prompt) {
  return [
    "The user seems frustrated or stuck. Adjust your response accordingly:",
    "- Be extremely direct and concise. No preamble, no recap.",
    "- Go straight to the root cause and the minimal fix.",
    "- Do not suggest alternatives unless directly asked.",
    "- Maximum 5 sentences unless code is necessary.",
    "- If you are uncertain, say so in one sentence and give the most likely answer.",
    `Original prompt: ${prompt}`,
  ].join("\n");
}

function continuationContext(prompt) {
  return [
    "The user wants you to continue without restarting or summarizing.",
    "- Pick up exactly where you left off.",
    "- Do not recap what was already done.",
    "- Do not re-introduce the task.",
    "- Continue directly with the next action.",
    `Original prompt: ${prompt}`,
  ].join("\n");
}

function debugContext(prompt) {
  return [
    "The user is sharing a debug signal (error, traceback, failure).",
    "- Lead with the root cause in one sentence.",
    "- Then provide the minimal fix or next diagnostic step.",
    "- Do not restate the error text back to the user.",
    "- Keep the response focused and actionable.",
    `Original prompt: ${prompt}`,
  ].join("\n");
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

  const prompt = event?.prompt ?? "";

  if (!prompt) {
    process.exit(0);
  }

  let injected = null;

  if (matches(prompt, CONTINUATION_PATTERNS)) {
    injected = continuationContext(prompt);
  } else if (matches(prompt, FRUSTRATION_PATTERNS)) {
    injected = frustrationContext(prompt);
  } else if (matches(prompt, DEBUG_PATTERNS)) {
    injected = debugContext(prompt);
  }

  if (injected) {
    process.stdout.write(
      JSON.stringify({ type: "inject_prompt", prompt: injected }) + "\n"
    );
    process.stderr.write(`[frustration-detection] Context injected\n`);
  }

  process.exit(0);
});
