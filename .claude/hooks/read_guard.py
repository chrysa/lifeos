#!/usr/bin/env python3
"""PreToolUse Read guard: refuse a whole-file read of a very large file, so the agent uses offset/limit or grep.
Saves tokens; it is not a security control, so any doubt allows the read."""
import json, os, sys

LIMIT_KB = 256
SKIP = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".ipynb", ".svg")

def main() -> int:
    try:
        data = json.load(sys.stdin)
        args = data.get("tool_input") or {}
        path = args.get("file_path") or ""
        if not path or path.lower().endswith(SKIP) or args.get("offset") or args.get("limit"):
            return 0
        kb = os.path.getsize(path) // 1024
    except (ValueError, OSError, AttributeError):
        return 0
    if kb > LIMIT_KB:
        print(f"{path} is {kb} KB: read it with offset and limit, or grep for what you need.", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
