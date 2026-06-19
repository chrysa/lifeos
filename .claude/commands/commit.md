---
description: Create a well-formatted Conventional Commit with atomic-commit analysis
---

# Command: Commit

Create well-formatted commits following the chrysa Conventional Commits standard.

## Usage

```text
/commit
```

## What This Command Does

1. Runs `git status` to see which files are staged.
2. If nothing is staged, stages all modified and new files with `git add`.
3. Runs `git diff` to understand the changes.
4. Analyzes the diff for multiple logical concerns; if found, proposes splitting into
   several atomic commits and stages them separately.
5. Writes a Conventional Commit message and commits.

## Commit Convention (chrysa)

Format — see `EXECUTION_STANDARD.md` §3 (source of truth):

```text
<type>(<scope>): <description>
```

- `<type>` is one of: `feat`, `fix`, `chore`, `docs`, `ci`, `refactor`, `test`, `perf`.
- `<scope>` is optional (module or area).
- Imperative mood, present tense ("add", not "added"). Link issues in the body or footer
  (`Refs #123`, `Closes #123`).
- Keep commits **atomic** — one logical concern each.

## Hard Rules

- **NEVER** add a `Co-Authored-By: Claude` / "Generated with Claude Code" trailer.
- Do not use awattar's `New feature`/`Fix issue` types — chrysa uses the standard spec above.
- Commit messages are validated by the repo's pre-commit hooks; run `make pre-commit` (Docker)
  if unsure, never host `pre-commit` directly.

## Agents Used

- **general-code-quality-debugger** — analyze the diff and commit quality.
- **general-technical-project-lead** — decide commit structure and flag breaking changes.

## References

- Convention: `EXECUTION_STANDARD.md` §3
- PR format: `@templates/pr-template.md`
