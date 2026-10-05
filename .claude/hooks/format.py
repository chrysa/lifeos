#!/usr/bin/env python3
"""PostToolUse formatter: formats the edited file with the project's own tools. Never blocks."""
import json, os, shutil, subprocess, sys

def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path or not os.path.isfile(path):
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    ext = os.path.splitext(path)[1].lower()
    local_prettier = os.path.join(root, "node_modules", ".bin", "prettier")
    cmd = None
    if ext in (".py", ".pyi") and shutil.which("ruff"):
        cmd = ["ruff", "format", "--quiet", path]
    elif ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".scss", ".json", ".vue") and os.path.exists(local_prettier):
        cmd = [local_prettier, "--write", "--log-level", "warn", path]
    elif ext in (".tf", ".tfvars") and shutil.which("terraform"):
        cmd = ["terraform", "fmt", path]
    elif ext == ".go" and shutil.which("gofmt"):
        cmd = ["gofmt", "-w", path]
    if cmd:
        try:
            subprocess.run(cmd, cwd=root, timeout=25, capture_output=True)
        except Exception:
            pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
