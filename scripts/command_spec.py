#!/usr/bin/env python3
"""Command specification for the quality gate runner."""

from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    """An ordered fallback chain of argv vectors, run without a shell.

    Each alternative is executed in order until one exits 0. This replaces the
    previous ``shell=True`` single-string form: shell operators such as ``||``
    are no longer interpreted by a shell — fallbacks are expressed as multiple
    argv vectors instead. ``swallow_exit`` mirrors a trailing ``|| true``: the
    gate is then driven by its parsed metric rather than the tool's exit code.
    """

    alternatives: tuple[tuple[str, ...], ...]
    swallow_exit: bool = False
    # Per-alternative manifest guard, aligned by index. ``None`` means always
    # applicable. An alternative whose manifest is absent is skipped rather than
    # run: npm audit in a repo with no package.json finds nothing and reports it
    # as zero vulnerabilities, which answers a Python question by asking npm.
    requires: tuple[str | None, ...] = ()

    @classmethod
    def parse(cls, raw: object, *, swallow_exit: bool = False) -> CommandSpec:
        """Build a spec from a config override.

        Accepted forms:
        - ``"make lint"`` → one argv vector (split with shlex, never a shell).
        - ``["make", "lint"]`` → one argv vector.
        - ``[["pip-audit"], ["npm", "audit"]]`` → an ordered fallback chain.
        - ``[{"cmd": ["npm", "audit"], "requires": "package.json"}]`` → the same,
          each alternative guarded by a manifest that must exist for it to apply.
        """
        if isinstance(raw, str):
            return cls((tuple(shlex.split(raw)),), swallow_exit=swallow_exit)
        if isinstance(raw, list):
            if raw and all(isinstance(item, str) for item in raw):
                return cls((tuple(raw),), swallow_exit=swallow_exit)
            chain: list[tuple[str, ...]] = []
            guards: list[str | None] = []
            for alt in raw:
                if isinstance(alt, dict):
                    argv = alt.get("cmd")
                    if not isinstance(argv, (list, tuple)):
                        raise ValueError(f"Alternative needs a 'cmd' list: {alt!r}")
                    chain.append(tuple(str(part) for part in argv))
                    guard = alt.get("requires")
                    guards.append(str(guard) if guard is not None else None)
                    continue
                if not isinstance(alt, (list, tuple)):
                    raise ValueError(f"Unsupported command specification: {raw!r}")
                chain.append(tuple(str(part) for part in alt))
                guards.append(None)
            return cls(tuple(chain), swallow_exit=swallow_exit, requires=tuple(guards))
        raise ValueError(f"Unsupported command specification: {raw!r}")

    def guard_for(self, index: int) -> str | None:
        """The manifest guarding alternative ``index``, if it declares one."""
        return self.requires[index] if index < len(self.requires) else None

    def display(self) -> str:
        rendered = " || ".join(shlex.join(alt) for alt in self.alternatives)
        return f"{rendered} || true" if self.swallow_exit else rendered
