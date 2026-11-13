#!/usr/bin/env python3
"""
APE thin adapter — Claude Code UserPromptSubmit hook.

Philosophy: the hook stays cheap. Anything it injects stays in the context for the rest of
the session, so it injects as little as possible:

  * Claude Code sends the prompt as JSON on stdin ({"prompt": ..., "session_id": ...}); plain
    text is accepted too.
  * Trivial, technical (code, paths, commands, URLs) and short follow-up prompts get nothing.
  * The first prompt that needs APE gets the compact block of the spec (between the
    `<!-- ape:inject -->` markers; the whole file if there are none). Later prompts of the same
    session get a one-line regime reminder only.
  * Any error stays silent and exits 0: the hook never blocks a turn.

Wire in .claude/settings.json:
  { "hooks": { "UserPromptSubmit": [ { "hooks": [
      { "type": "command",
        "command": "python3 /path/to/ape_hook.py --spec /path/to/ape-transform-v2.md" }
  ] } ] } }
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

TRIVIAL = re.compile(
    r"^\s*(oui|ok|okay|go|merci|non|yes|no|thanks?|stop|continu\w*|vas-?y|d'accord|parfait|/\w+|!\w+)"
    r"(\W+(ok|go|vas-?y|merci|thanks?))*\W*$",
    re.IGNORECASE,
)
SKIP_MARKERS = re.compile(r"\b(sans ape|raw|n'optimise pas|no ape)\b", re.IGNORECASE)
FORCE_BLOCK = re.compile(r"!ape\b", re.IGNORECASE)

# Technical prompts (the spec says: structure only, never worth a rewrite).
TECHNICAL = re.compile(
    r"```|`[^`\n]+`|https?://|(?:^|\s)~?/[\w.-]+/|[\w-]+/[\w.-]+\.\w{1,5}\b"
    r"|\b[\w-]+\.(?:py|js|ts|tsx|jsx|json|md|ya?ml|toml|sh|go|rs|java|sql)\b"
    r"|\b(?:git|gh|pip|npm|pnpm|make|docker|kubectl|pytest|ruff|mypy|python3?|node)\b",
    re.IGNORECASE,
)

# crude "already structured" signal: mentions role/format/criteria/audience cues
STRUCTURE_CUES = re.compile(
    r"\b(agis comme|act as|pour (un|une|le|la|mon|mes)|format|"
    r"crit[eè]re|criteria|en \d+ (phrases?|mots?|lignes?)|audience|cible|"
    r"contrainte|ton |style )\b",
    re.IGNORECASE,
)

MIN_CUES = 3
SHORT_FOLLOWUP = 200
MIN_LENGTH = 15
BLOCKING_LENGTH = 600
CORE = re.compile(r"<!-- ape:inject -->(.*?)<!-- ape:end -->", re.DOTALL)


def read_input(raw: str) -> tuple[str, str]:
    """Return (prompt, session_id) from the hook JSON, or the raw text when it is not JSON."""
    try:
        data = json.loads(raw)
    except ValueError:
        return raw, ""
    if isinstance(data, dict):
        return str(data.get("prompt") or ""), str(data.get("session_id") or "")
    return raw, ""


def marker_path(session_id: str) -> Path | None:
    if not session_id:
        return None
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"ape-{os.getuid()}" / digest


def touch_marker(marker: Path) -> None:
    """Create the marker in a private per-user directory, never following a symlink."""
    marker.parent.mkdir(mode=0o700, exist_ok=True)
    if marker.parent.is_symlink() or marker.parent.stat().st_uid != os.getuid():
        return
    fd = os.open(marker, os.O_CREAT | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    os.close(fd)


def triage(prompt: str, seen: bool) -> str:
    p = prompt.strip()
    if not p or TRIVIAL.match(p) or SKIP_MARKERS.search(p):
        return "SILENT"
    if FORCE_BLOCK.search(p):
        return "BLOCKING"
    if len(p) < MIN_LENGTH or TECHNICAL.search(p):
        return "SILENT"
    cues = len({m.group(0).lower() for m in STRUCTURE_CUES.finditer(p)})
    if cues >= MIN_CUES or (seen and len(p) < SHORT_FOLLOWUP):
        return "SILENT"
    if len(p) > BLOCKING_LENGTH:
        return "BLOCKING"
    return "SUGGESTIVE"


def compact(spec: str) -> str:
    m = CORE.search(spec)
    return m.group(1).strip() if m else spec


def run(raw: str, spec_path: str) -> str:
    prompt, session_id = read_input(raw)
    marker = marker_path(session_id)
    seen = bool(marker and marker.exists())
    regime = triage(prompt, seen)
    if regime == "SILENT":
        return ""
    if seen:
        return f"<!-- APE regime (pre-triaged): {regime}; spec already loaded this session -->"
    spec = compact(Path(spec_path).read_text(encoding="utf-8"))
    if marker:
        try:
            touch_marker(marker)
        except OSError:
            pass  # no marker: the spec may load again, which is safe
    sink = os.environ.get("APE_TRACE_SINK")
    trace = f"\nTrace sink: {sink}" if sink else ""
    return f"<!-- APE regime (pre-triaged): {regime} -->\n{spec}{trace}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="path to ape-transform-v2.md")
    args = ap.parse_args()
    try:
        out = run(sys.stdin.read(), args.spec)
    except Exception as e:  # fail open: never block the user's turn
        print(f"[APE] skipped: {e}", file=sys.stderr)
        return 0
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
