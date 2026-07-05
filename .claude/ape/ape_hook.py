#!/usr/bin/env python3
"""
APE thin adapter — Claude Code UserPromptSubmit hook.

Philosophy: the hook stays cheap. It does a fast local triage to decide whether
the APE spec is even worth injecting, instead of dumping the full spec on every
prompt. Heavy transformation logic lives in the spec (ape-transform-v2.md), read
by the model only when triage says it's warranted.

Wire in .claude/settings.json:
  { "hooks": { "UserPromptSubmit": [ { "hooks": [
      { "type": "command",
        "command": "python3 /path/to/ape_hook.py --spec /path/to/ape-transform-v2.md" }
  ] } ] } }

The hook reads the prompt on stdin (Claude Code passes the user prompt) and writes
context to stdout, which Claude Code injects before the turn.
"""
import sys
import re
import json
import argparse

# --- fast triage: is this prompt worth optimizing at all? ---

TRIVIAL = re.compile(
    r"^\s*(oui|ok|go|merci|non|yes|no|thanks?|/\w+|!\w+)\s*$", re.IGNORECASE
)
SKIP_MARKERS = re.compile(r"\b(sans ape|raw|n'optimise pas|no ape)\b", re.IGNORECASE)
FORCE_BLOCK = re.compile(r"!ape\b", re.IGNORECASE)

# crude "already structured" signal: mentions role/format/criteria/audience cues
STRUCTURE_CUES = re.compile(
    r"\b(agis comme|act as|pour (un|une|le|la|mon|mes)|format|"
    r"crit[eè]re|criteria|en \d+ (phrases?|mots?|lignes?)|audience|cible|"
    r"contrainte|ton |style )\b",
    re.IGNORECASE,
)


def triage(prompt: str) -> str:
    p = prompt.strip()
    if not p or TRIVIAL.match(p) or SKIP_MARKERS.search(p):
        return "SILENT"
    if FORCE_BLOCK.search(p):
        return "BLOCKING"
    # count structure cues as a proxy for slots already filled
    cues = len(set(m.group(0).lower() for m in STRUCTURE_CUES.finditer(p)))
    if cues >= 3 or len(p) < 15:
        return "SILENT"
    # long / high-stakes prompts get the blocking treatment
    if len(p) > 600:
        return "BLOCKING"
    return "SUGGESTIVE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="path to ape-transform-v2.md")
    args = ap.parse_args()

    prompt = sys.stdin.read()
    regime = triage(prompt)

    if regime == "SILENT":
        # inject nothing — zero friction on trivial/well-formed prompts
        return 0

    try:
        with open(args.spec, encoding="utf-8") as f:
            spec = f.read()
    except OSError as e:
        print(f"[APE] spec unreadable: {e}", file=sys.stderr)
        return 0  # fail open: never block the user's turn

    # tell the model the triage result so it doesn't re-run Step 0 from scratch
    print(f"<!-- APE regime (pre-triaged): {regime} -->\n")
    print(spec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
