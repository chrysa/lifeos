<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Backend Python

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Python packaging — `pyproject.toml` is the single source of truth.** `setup.py` and
  `setup.cfg` are **forbidden** for Python packaging (`setup.cfg` allowed only for non-Python
  tooling, e.g. uwsgi). Build backend is **`setuptools`** (never `hatchling`). All tool config
  (`ruff`, `mypy`, `pytest`, `coverage`) lives in `[tool.*]` — external `ruff.toml`, `mypy.ini`,
  `pytest.ini` are forbidden. Distributed libraries use a `src/` layout and follow the Public API
  Contract (`docs/PUBLIC-API-CONTRACT.md`): sorted `__all__`, relative imports in `__init__`,
  `__version__` via `importlib.metadata`, uniform `install()` entrypoint, shared types in `chrysa-lib`.

- **Python is written object-oriented, one class per file.** Behaviour is carried by classes,
  not by a bag of module-level functions sharing state through globals or long parameter
  lists: a cohesive responsibility (a service, a repository, an adapter, a use case, a value
  object) is a **class**, dependencies are injected through `__init__`, and state lives on
  the instance. **One class per module, and the module is named after it** —
  `vehicle_dispatcher.py` holds `VehicleDispatcher`, and nothing else of substance (private
  helpers of that class and its own exception types may live beside it). Method order inside
  a class is fixed: dunder → property → abstract → classmethod → staticmethod → public →
  private, alphabetical within each group. Pure functions remain legitimate where there is
  genuinely no state and no variation point — a stateless transformation, a validator, the
  functional core called by the class — and Pydantic models, dataclasses, enums and
  protocols are classes already. What is forbidden is a `utils.py` grab-bag, a module of
  loosely related procedures threading the same objects through every signature, and two
  unrelated public classes sharing one file.

- **Import the item, not the module — `from x import y; y()`.** Python imports name the
  symbol actually used (`from fastapi import status`, `from datetime import datetime`,
  `from app.services.billing import BillingService`), so call sites read `datetime.now()`
  and `BillingService(...)`, not `datetime.datetime.now()` or a chain of package prefixes.
  Bare `import x` is reserved for the cases where it is genuinely better: a module used as a
  namespace whose name carries meaning at the call site (`import numpy as np`,
  `import json`), or breaking an import cycle. **Forbidden**: wildcard `from x import *`,
  relative imports beyond a package's own `__init__` re-exports, and importing a module only
  to reach one attribute through it. Imports sit at module top level (never inside a function
  except to break a cycle, and that is commented), and are ordered/deduplicated by Ruff
  (`I` rules) — the linter owns the ordering, no hand-sorting.

- **Functions and methods are called with named arguments — positional call sites are the
  exception, not the rule.** A call reads `create_user(name="Ada", role=Role.ADMIN,
  active=True)`, never `create_user("Ada", Role.ADMIN, True)`: the argument names are part of
  what the reader needs, and a bare positional value (especially a bool, a number, or a `None`)
  is a *boolean trap* / magic value the reader has to jump to the signature to decode. So:
  1. **Definitions force it where it matters.** Any function/method taking more than one
     parameter, or **any** boolean/optional/`None`-defaulted parameter, declares them
     **keyword-only** with a bare `*` (`def build(*, source: Source, strict: bool = False)`),
     so callers *must* name them and arguments cannot be silently reordered. Adding a parameter
     then never shifts an existing positional meaning.
  2. **Call sites name their arguments.** Even when a signature still allows positional passing,
     call sites pass by keyword. The narrow, allowed exceptions where positional is clearer:
     a single obvious argument (`len(items)`, `Path(raw)`, `str(value)`), the receiver of a
     dunder, and genuine `*args`/`**kwargs` pass-through.
  3. **Not a substitute for value objects.** Naming four primitives at the call site is better
     than four bare positionals, but a signature that needs many named primitives is still
     *primitive obsession* — the fix is a value object / Pydantic model, then one named argument
     carries it.
  Mechanisation: Ruff `FBT001`/`FBT002` (boolean-positional) already flag the worst case; the
  keyword-only `*` in definitions is the enforcement mechanism the reviewer checks. A public
  API added with a multi-parameter positional signature is a defect.
