"""Generate the standardised per-repo context files from the repo's own content.

Every chrysa repo ships a small, vendor-neutral **context set**, generated from the
repo (never hand-authored) and drift-gated exactly like the agent views. A fresh agent
or the returning owner opens these four files and knows the repo without re-reading the
code (ADR D-0012):

  * ``handover.md``       — human handover: what the repo is, its place in the ecosystem,
                            its ``shared-standards`` dependency, its settled decisions
                            (ADRs), discoverable Notion links, and current state.
  * ``context-map.json``  — machine-readable map: entry points, key dirs, profile/DDD,
                            declared contracts, dependencies. **No vendor name** in any
                            key or value — portable to any assistant.
  * ``llms-full.txt``     — technical digest generated from the real code/config: the
                            directory tree, key configuration, module docstrings.
  * ``ai-instructions.md``— vendor-neutral working instructions (FR): a thin generated
                            pointer to the repo's agent views and the standards canon,
                            never a fork of them.

This script is CANONICAL and DISTRIBUTED: ``templates/gen_context_files.py`` is the single
source of truth, synced to every repo's ``scripts/`` by the standards distribution, and
each repo runs it **on itself** (``shared-standards`` is repo #1 / the dogfood).

Run ``python -m scripts.gen_context_files`` to (re)write the four files, or
``python -m scripts.gen_context_files --check`` to fail on drift (the ``context-files-drift``
pre-commit hook + the CI gate).

**Determinism is a contract.** The output is byte-stable across runs and machines: stable
key ordering, sorted lists, and NO timestamps, dates, random values, absolute paths or host
info in any generated file. A non-deterministic byte would make the drift gate false-fire on
every run and trip the ADR kill-test immediately. Every source that may be absent degrades
gracefully to a clearly-marked ``(not available)`` — the generator never crashes on a repo
that lacks a README, a pyproject, a changelog or an ADR directory.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

# The repo this generator runs against is the parent of the scripts/ dir that holds it —
# identical resolution in shared-standards and in every consumer it is distributed to.
_ROOT = Path(__file__).resolve().parents[1]

# The four generated files, at the repo root. Order is the read/write order and is stable.
HANDOVER = "handover.md"
CONTEXT_MAP = "context-map.json"
LLMS_FULL = "llms-full.txt"
AI_INSTRUCTIONS = "ai-instructions.md"
GENERATED_FILES = (HANDOVER, CONTEXT_MAP, LLMS_FULL, AI_INSTRUCTIONS)

# Shown whenever a source is absent — a clearly-marked, greppable sentinel, never a crash.
NA = "(not available)"

# Directories never walked for the tree / key-dirs: version control, dependency and build
# vendoring, tool caches. Everything volatile lives here, so excluding it keeps the output
# byte-stable between runs.
EXCLUDE_DIRS = frozenset({
    "node_modules", ".venv", "venv", "dist", "build", "target", "coverage", "htmlcov",
    "__pycache__", ".pnpm-store", "site-packages", ".terraform", "vendor",
})
# Hidden top-level dirs are volatile caches (.mypy_cache, .pytest_cache, .gitnexus, …) —
# excluded wholesale except this allowlist of meaningful ones.
DOTDIR_ALLOWLIST = frozenset({".github", ".claude"})

# Depth of the directory tree in llms-full.txt (root = depth 0).
TREE_DEPTH = 3
# Hard caps that keep the digest bounded and stable on a large heterogeneous fleet.
MAX_MODULES = 40
MAX_NOTION_LINKS = 40
MAX_CHANGELOG_LINES = 25

# The managed standards block distribute-standards.sh injects into every consumer CLAUDE.md;
# its presence is the machine-checkable signal that a repo depends on shared-standards.
STANDARDS_MARKER = "chrysa:standards:start"

# Text files scanned for discoverable Notion links (bounded, deterministic set).
NOTION_SCAN_GLOBS = ("README.md", "CLAUDE.md", "AGENTS.md")
NOTION_SCAN_DIRS = ("docs", "standards")
NOTION_RE = re.compile(r"https://(?:www\.)?notion\.so/[^\s)\]\"'<>]+")


# ── source readers (all degrade gracefully) ────────────────────────────────────────────


def _read_text(path: Path) -> str | None:
    """Read a text file, returning None on any absence or decode error (never raises)."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _load_pyproject(root: Path) -> dict:
    """Parse ``pyproject.toml`` into a dict, or an empty dict when absent/invalid."""
    raw = _read_text(root / "pyproject.toml")
    if raw is None:
        return {}
    try:
        return tomllib.loads(raw)
    except tomllib.TOMLDecodeError:
        return {}


def _load_package_json(root: Path) -> dict:
    """Parse ``package.json`` into a dict, or an empty dict when absent/invalid."""
    raw = _read_text(root / "package.json")
    if raw is None:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _first_h1(markdown: str | None) -> str | None:
    """Return the first ``# Title`` heading text, or None."""
    if not markdown:
        return None
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def _first_paragraph(markdown: str | None) -> str | None:
    """Return the first non-heading, non-blank prose line of a markdown doc, or None."""
    if not markdown:
        return None
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", ">", "-", "*", "|", "```", "<!--")):
            return stripped
    return None


def repo_name(root: Path, pyproject: dict, pkg: dict) -> str:
    """Repo name: pyproject/package name, else README H1, else the directory basename."""
    name = pyproject.get("project", {}).get("name") or pkg.get("name")
    if name:
        return str(name)
    heading = _first_h1(_read_text(root / "README.md"))
    return heading or root.name


def repo_description(root: Path, pyproject: dict, pkg: dict) -> str:
    """One-line description, tried in source-priority order, else the NA sentinel."""
    desc = pyproject.get("project", {}).get("description") or pkg.get("description")
    if desc:
        return str(desc).strip()
    for candidate in ("README.md", "CLAUDE.md"):
        para = _first_paragraph(_read_text(root / candidate))
        if para:
            return para
    return NA


def _iter_repos_yml_profiles(root: Path) -> dict:
    """Return the ``profiles:`` map from an in-repo repos.yml, or {} (consumers lack it)."""
    raw = _read_text(root / "repos.yml")
    if raw is None:
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return {}
    profiles = (data or {}).get("profiles", {})
    return profiles if isinstance(profiles, dict) else {}


def profiles_for(root: Path, name: str) -> list[str]:
    """Sorted list of profiles a repo is declared under in repos.yml (empty if none)."""
    profiles = _iter_repos_yml_profiles(root)
    return sorted(p for p, members in profiles.items() if name in (members or []))


def ddd_level(root: Path, pyproject: dict) -> str:
    """DDD level from a ``[tool.chrysa]`` marker, else the NA sentinel."""
    level = pyproject.get("tool", {}).get("chrysa", {}).get("ddd")
    return str(level) if level else NA


def depends_on_shared_standards(root: Path) -> bool:
    """True when the repo carries the managed standards block or the on-demand rule detail."""
    claude = _read_text(root / "CLAUDE.md")
    if claude and STANDARDS_MARKER in claude:
        return True
    return (root / "standards" / "rules").is_dir()


def _adr_status(text: str) -> str:
    """Extract the ``Status`` field from an ADR body, or the NA sentinel."""
    match = re.search(r"(?im)^[-*]?\s*\*\*status:\*\*\s*(.+)$", text)
    if match:
        return match.group(1).strip()
    return NA


def list_adrs(root: Path) -> list[dict]:
    """Every ADR under docs/adr/, sorted by filename, as {file, title, status} records."""
    adr_dir = root / "docs" / "adr"
    if not adr_dir.is_dir():
        return []
    records: list[dict] = []
    for path in sorted(adr_dir.glob("*.md"), key=lambda p: p.name):
        text = _read_text(path) or ""
        records.append({
            "file": path.name,
            "title": _first_h1(text) or path.stem,
            "status": _adr_status(text),
        })
    return records


def notion_links(root: Path) -> list[str]:
    """Unique, sorted Notion URLs discoverable in the repo's docs (bounded scan)."""
    found: set[str] = set()
    candidates = [root / name for name in NOTION_SCAN_GLOBS]
    for sub in NOTION_SCAN_DIRS:
        base = root / sub
        if base.is_dir():
            candidates.extend(sorted(base.rglob("*.md"), key=lambda p: p.as_posix()))
    for path in candidates:
        text = _read_text(path)
        if text:
            found.update(NOTION_RE.findall(text))
    return sorted(found)[:MAX_NOTION_LINKS]


def latest_changelog(root: Path) -> str:
    """The first version section of CHANGELOG.md (heading + body), or the NA sentinel."""
    text = _read_text(root / "CHANGELOG.md")
    if not text:
        return NA
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), None)
    if start is None:
        return NA
    body: list[str] = [lines[start].strip()]
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.strip():
            body.append(line.rstrip())
        if len(body) >= MAX_CHANGELOG_LINES:
            break
    return "\n".join(body)


# ── structural extractors (context-map + llms-full) ─────────────────────────────────────
#
# The repo's structure is read from the set of git-TRACKED files, not a raw filesystem
# walk. This is what makes the digest byte-identical between a developer's working tree
# (full of tool caches, graphify-out, untracked scratch files) and a fresh CI checkout —
# git already excludes everything gitignored. When git is unavailable the code degrades to
# a filtered filesystem walk so the generator still runs (it just cannot guarantee the
# CI/local parity that the tracked-file path gives).


def _tracked_files(root: Path) -> list[str] | None:
    """Sorted repo-relative posix paths git tracks, or None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    files = [p for p in result.stdout.split("\0") if p and p not in GENERATED_FILES]
    return sorted(files)


def _walk_files(root: Path) -> list[str]:
    """Filesystem fallback: repo-relative posix paths, minus vendored/volatile dirs."""
    out: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink() and _is_source_path(path, root):
            rel = path.relative_to(root).as_posix()
            if Path(rel).name not in GENERATED_FILES:
                out.append(rel)
    return sorted(out)


def repo_files(root: Path) -> list[str]:
    """The repo's files (tracked when git is available, else a filtered filesystem walk)."""
    tracked = _tracked_files(root)
    return tracked if tracked is not None else _walk_files(root)


def key_dirs(files: list[str]) -> list[str]:
    """Sorted names of the repo's meaningful top-level directories."""
    return sorted({rel.split("/", 1)[0] for rel in files if "/" in rel})


def entry_points(pyproject: dict, pkg: dict) -> list[str]:
    """Declared executable/entry names (console-scripts, package bin/main), sorted."""
    points: set[str] = set()
    points.update(pyproject.get("project", {}).get("scripts", {}).keys())
    points.update(pyproject.get("project", {}).get("gui-scripts", {}).keys())
    if isinstance(pkg.get("main"), str):
        points.add(pkg["main"])
    pkg_bin = pkg.get("bin")
    if isinstance(pkg_bin, dict):
        points.update(pkg_bin.keys())
    elif isinstance(pkg_bin, str):
        points.add(pkg_bin)
    return sorted(points)


def _dep_name(spec: str) -> str:
    """Reduce a PEP 508 / npm dependency spec to its bare package name."""
    return re.split(r"[<>=!~;\[\s]", spec, maxsplit=1)[0].strip()


def dependencies(pyproject: dict, pkg: dict) -> dict:
    """Direct dependency names, split by ecosystem, each list sorted and de-duplicated."""
    python: set[str] = set()
    project = pyproject.get("project", {})
    for spec in project.get("dependencies", []) or []:
        if isinstance(spec, str):
            python.add(_dep_name(spec))
    optional = project.get("optional-dependencies", {}) or {}
    for specs in optional.values():
        for spec in specs or []:
            if isinstance(spec, str):
                python.add(_dep_name(spec))
    node = {
        str(name)
        for key in ("dependencies", "devDependencies")
        for name in (pkg.get(key, {}) or {})
    }
    result: dict[str, list[str]] = {}
    if python:
        result["python"] = sorted(python)
    if node:
        result["node"] = sorted(node)
    return result


def contracts(root: Path) -> list[str]:
    """Declared-contract artefacts present in the repo (OpenAPI, schemas, the canon), sorted."""
    known = (
        "openapi.yaml", "openapi.yml", "openapi.json", "asyncapi.yaml",
        "schemas", "contracts", "proto", "standards",
    )
    return sorted(name for name in known if (root / name).exists())


def dir_tree(files: list[str], depth: int) -> list[str]:
    """Deterministic ``tree``-style listing to ``depth``, derived from the file list."""
    seen: set[str] = set()
    lines: list[str] = []
    for rel in files:
        parts = rel.split("/")
        for level, part in enumerate(parts):
            if level > depth:
                break
            is_dir = level < len(parts) - 1
            marker = "/" if is_dir else ""
            key = "/".join(parts[: level + 1]) + marker
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"{'  ' * level}{part}{marker}")
    return lines


def _module_docstring(text: str | None) -> str:
    """First line of a Python module's leading docstring, or an empty string."""
    if not text:
        return ""
    match = re.match(r'\s*(?:r|u)?("""|\'\'\')(.*?)\1', text, re.DOTALL)
    if not match:
        return ""
    return match.group(2).strip().splitlines()[0].strip() if match.group(2).strip() else ""


def module_headers(root: Path, files: list[str]) -> list[str]:
    """One-line summaries of the repo's Python modules (bounded, sorted by path)."""
    out: list[str] = []
    for rel in [f for f in files if f.endswith(".py")][:MAX_MODULES]:
        summary = _module_docstring(_read_text(root / rel))
        out.append(f"{rel} — {summary}" if summary else rel)
    return out


def _is_source_path(path: Path, root: Path) -> bool:
    """True when ``path`` sits outside every excluded/volatile directory."""
    for part in path.relative_to(root).parts[:-1]:
        if part in EXCLUDE_DIRS:
            return False
        if part.startswith(".") and part not in DOTDIR_ALLOWLIST:
            return False
    return True


# ── file builders (pure: return the exact bytes to write) ───────────────────────────────


def build_handover(root: Path, pyproject: dict, pkg: dict) -> str:
    """Render handover.md from the repo's own README/pyproject/ADRs/changelog/Notion."""
    name = repo_name(root, pyproject, pkg)
    profiles = profiles_for(root, name)
    profile_str = ", ".join(profiles) if profiles else NA
    adrs = list_adrs(root)
    links = notion_links(root)
    depends = "yes" if depends_on_shared_standards(root) else "no"

    out: list[str] = [
        _generated_banner("#"),
        "",
        f"# Handover — {name}",
        "",
        f"**Description.** {repo_description(root, pyproject, pkg)}",
        "",
        "## Place in the ecosystem",
        "",
        f"- **Profile(s):** {profile_str}",
        f"- **DDD level:** {ddd_level(root, pyproject)}",
        f"- **Depends on `shared-standards`:** {depends}",
        "",
        "## Settled decisions (ADRs)",
        "",
    ]
    if adrs:
        out.extend(f"- `{a['file']}` — {a['title']} ({a['status']})" for a in adrs)
    else:
        out.append(f"- {NA}")
    out += ["", "## Notion links", ""]
    if links:
        out.extend(f"- {link}" for link in links)
    else:
        out.append(f"- {NA}")
    out += ["", "## Current state (latest changelog entry)", "", "```", latest_changelog(root), "```", ""]
    return "\n".join(out)


def build_context_map(root: Path, pyproject: dict, pkg: dict, files: list[str]) -> str:
    """Render context-map.json — machine-readable, vendor-neutral, stable key order."""
    name = repo_name(root, pyproject, pkg)
    data = {
        "schema": "chrysa.context-map/1",
        "name": name,
        "description": repo_description(root, pyproject, pkg),
        "profiles": profiles_for(root, name),
        "ddd_level": ddd_level(root, pyproject),
        "depends_on_shared_standards": depends_on_shared_standards(root),
        "entry_points": entry_points(pyproject, pkg),
        "key_directories": key_dirs(files),
        "contracts": contracts(root),
        "dependencies": dependencies(pyproject, pkg),
        "adrs": [a["file"] for a in list_adrs(root)],
    }
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def build_llms_full(root: Path, pyproject: dict, pkg: dict, files: list[str]) -> str:
    """Render llms-full.txt — a technical digest built from the real tree/config/modules."""
    name = repo_name(root, pyproject, pkg)
    out: list[str] = [
        _generated_banner("#"),
        "",
        f"{name} — technical digest",
        "=" * (len(name) + 18),
        "",
        repo_description(root, pyproject, pkg),
        "",
        "## Structure",
        "",
    ]
    out.extend(dir_tree(files, TREE_DEPTH))
    out += ["", "## Key configuration", ""]
    out.extend(_config_summary(pyproject, pkg))
    out += ["", "## Modules", ""]
    modules = module_headers(root, files)
    out.extend(modules if modules else [NA])
    out.append("")
    return "\n".join(out)


def _config_summary(pyproject: dict, pkg: dict) -> list[str]:
    """Stable key: value lines for the project's declared metadata (or the NA sentinel)."""
    project = pyproject.get("project", {})
    fields = {
        "name": project.get("name") or pkg.get("name"),
        "version": project.get("version") or pkg.get("version"),
        "requires-python": project.get("requires-python"),
        "license": _license_str(project.get("license")) or pkg.get("license"),
    }
    lines = [f"{key}: {value}" for key, value in sorted(fields.items()) if value]
    return lines or [NA]


def _license_str(value: object) -> str | None:
    """Normalise the polymorphic pyproject ``license`` field to a string or None."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text = value.get("text") or value.get("file")
        return str(text) if text else None
    return None


def build_ai_instructions(root: Path) -> str:
    """Render ai-instructions.md (FR) — a thin, vendor-neutral pointer, not a fork."""
    has_agents = (root / "AGENTS.md").exists()
    has_claude = (root / "CLAUDE.md").exists()
    has_standards = (root / "standards").is_dir()
    views: list[str] = []
    if has_agents:
        views.append("`AGENTS.md`")
    if has_claude:
        views.append("`CLAUDE.md`")
    views_str = " et ".join(views) if views else "les vues d'agent du dépôt"
    canon = (
        "le dossier `standards/` (le canon chrysa, source de vérité)"
        if has_standards
        else "les standards chrysa distribués dans le dépôt"
    )
    out = [
        _generated_banner("#"),
        "",
        "# Instructions de travail (agnostique de l'outil)",
        "",
        "Ce fichier est **généré** à partir du dépôt — ne pas l'éditer à la main. Il ne",
        "remplace ni ne recopie les vues d'agent : il y **pointe**. Toute autorité vient",
        "du canon, jamais d'un outil ou d'un produit particulier.",
        "",
        "## Ordre de lecture",
        "",
        f"1. {views_str} — la vue toujours active des règles du dépôt.",
        f"2. {canon} — le détail des règles, chargé à la demande.",
        "3. `handover.md` — l'état du dépôt et sa place dans l'écosystème.",
        "4. `context-map.json` — la carte machine du dépôt (points d'entrée, dépendances).",
        "5. `llms-full.txt` — le digest technique (arborescence, configuration, modules).",
        "",
        "## Règles de travail",
        "",
        "- Respecter le canon : en cas de conflit entre une vue et le canon, le canon gagne.",
        "- Écrire en anglais dans le code et les commits ; ce guide reste en français.",
        "- Ne jamais coder en dur un secret, une clé, un jeton ou un chemin machine.",
        "- Les fichiers de contexte sont générés : régénérer, ne pas éditer à la main.",
        "",
    ]
    return "\n".join(out)


def _generated_banner(comment: str) -> str:
    """A prominent 'do not edit — generated' banner, prefixed by the file's comment token."""
    return (
        f"{comment} GENERATED by scripts/gen_context_files.py (ADR D-0012) — do not edit. "
        "Regenerate with `make gen-context-files`."
    )


# ── orchestration + drift gate ──────────────────────────────────────────────────────────


def generate(root: Path) -> dict[str, str]:
    """Every context file this generator owns, mapped to its expected byte content."""
    pyproject = _load_pyproject(root)
    pkg = _load_package_json(root)
    files = repo_files(root)
    return {
        HANDOVER: build_handover(root, pyproject, pkg),
        CONTEXT_MAP: build_context_map(root, pyproject, pkg, files),
        LLMS_FULL: build_llms_full(root, pyproject, pkg, files),
        AI_INSTRUCTIONS: build_ai_instructions(root),
    }


def write_all(root: Path) -> None:
    """Write every context file to the repo root."""
    for name, content in generate(root).items():
        (root / name).write_text(content, encoding="utf-8")


def drift(root: Path) -> list[str]:
    """Return a list of drift lines (empty when every committed context file is current)."""
    lines: list[str] = []
    for name, expected in generate(root).items():
        actual = _read_text(root / name)
        if actual is None:
            lines.append(f"missing: {name}")
        elif actual != expected:
            lines.append(f"stale: {name}")
    return lines


def main() -> int:
    """CLI entry point: regenerate, or ``--check`` for the drift gate."""
    check = "--check" in sys.argv[1:]
    if not check:
        write_all(_ROOT)
        return 0
    drifted = drift(_ROOT)
    if drifted:
        sys.stderr.write("context files have drifted from the repo:\n")
        for line in drifted:
            sys.stderr.write(f"  - {line}\n")
        sys.stderr.write(
            "run `make gen-context-files` "
            "(or `python -m scripts.gen_context_files`) and commit the result.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
