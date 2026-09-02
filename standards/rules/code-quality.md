<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Code quality & anti-patterns

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **No hardcoded constants** in code — neither backend (Python) nor frontend (TS).
  All constants and config values (thresholds, business rules, labels, URLs, magic
  numbers) live in **external YAML files** and are loaded at runtime. Code reads them
  through a typed loader (Pydantic Settings backend · generated typed module frontend),
  never as inline literals. Only language-level enums (e.g. `status.HTTP_*`) are exempt.

- **No literal HTTP status codes — use the constants the framework already ships.** A bare
  `200`, `404`, `422`, `500` in code or in a test is forbidden; the value comes from the
  library that defines it: Python `fastapi.status.HTTP_404_NOT_FOUND` (or
  `http.HTTPStatus.NOT_FOUND` outside FastAPI), Django `HTTPStatus`, TypeScript a typed
  status enum/const from the HTTP client layer, C# `System.Net.HttpStatusCode`. This applies
  everywhere the code names a status — route decorators (`status_code=status.HTTP_201_CREATED`),
  raised errors, client-side branching, and **assertions in tests**
  (`assert response.status_code == status.HTTP_403_FORBIDDEN`). The same rule generalises: when
  a standard library or a framework already publishes the constant/enum for a protocol value
  (HTTP methods, MIME types, headers, signal numbers, exit codes), import it — never retype the
  literal. A magic number the reader has to look up is a defect, not a shortcut.

- **No code duplication — the second occurrence is an extraction order.** Copy-pasting a
  function, a fixture, a type, a config block, or a workflow step across files or repos is
  forbidden. The rule is mechanical: the **first** occurrence is code, the **second** is a
  factoring order — the logic moves to the transverse home for its kind and both call sites
  consume it from there. The homes are fixed: shared Python code → **`chrysa-lib`** (or the
  relevant `chrysa/*` library), CI logic → **`chrysa/github-actions`**, commit gates →
  **`chrysa/pre-commit-tools`**, standards/templates → **`shared-standards`**, UI components →
  the design system. Inside one repo, duplication is extracted to a shared module in the same
  layer — never re-typed in a sibling. Rewriting the same logic in different words does not
  make it a different implementation; a near-duplicate diverges silently and costs sixty PRs
  to fix once. Mechanisation: the code-quality analysis service's duplication ratio and `jscpd`-class detectors; a
  reported duplicate block is a defect to factor, not a warning to carry. Legitimate exception:
  a deliberate copy that decouples two projects on purpose (see *projects talk through
  versioned contracts only*) — documented as such, not left implicit.

- **Raised errors are typed** — in any language whose type system allows it. Code raises a
  **domain-specific exception class** (Python: a module `…Error(Exception)` hierarchy rooted in one
  base per bounded context; TypeScript: `class XError extends Error` with a discriminant field, or a
  typed `Result`/`Either`; C#: a derived `Exception`). **Forbidden**: raising a bare `Exception`/
  `RuntimeError`/`Error`, `throw "string"`, `throw {code: …}` object literals, or signalling failure
  by a magic return value (`None`/`-1`/`false`) where an error type is expressible. Catch sites match
  the narrowest type (`except ValidationError`, never bare `except:`/`except Exception` outside a
  top-level boundary), and every error carries a stable machine-readable code plus a message that
  says what to do. The public error taxonomy of a module is part of its contract — documented and
  versioned like its signatures. Detail: the `error-handling` skill.

- **Failures are contained, and observable.** A *local* error must not become a *global* one: a
  failing dependency, task, or request is isolated so the rest of the system keeps serving.
  Beyond the type + stable `code`, an error carries the taxonomy fields it needs to be triaged —
  `category`, `severity`, `retryable`, `scope`, a `correlation_id` threading it across services,
  and both a user-facing and an operator-facing message. Every outbound call has an explicit
  **timeout** and **bounded retries** (never an unbounded retry loop); a repeatedly-failing
  dependency is fronted by a **circuit-breaker**, and independent workloads by a **bulkhead**, so
  one saturated path cannot drown the others. Errors are emitted to the shared observability
  backend (**Mirador** or a compatible one), correlation id included, not just written to a local
  log. A surface's Definition of Done includes its error paths, not only its happy path.

- **Prefer a lookup table to a state machine.** Branching on a value — dispatch, routing, parsing,
  handler/strategy selection, enum → behaviour, status → transition — is expressed as a **hash
  table** (`dict`/`Record`/`Map`) from key to handler or value, **not** as an `if/elif` ladder, a
  `switch`/`match` cascade, or a hand-rolled state machine with a `self._state` variable. The
  mapping is data: declared once, typed (`dict[Status, Handler]`), exhaustive over the key domain
  (checked by the type system or a test), and extended by adding a row — never by editing control
  flow. This keeps cyclomatic complexity flat and makes every branch independently testable. An
  explicit state machine is legitimate only when the transitions genuinely carry state-dependent
  semantics no table can express (concurrent protocol, long-running workflow, parser with a stack);
  choosing one is a documented decision, and even then transitions themselves live in a
  transition **table**, not in nested conditionals.

- **Decompose into small, independently unit-testable methods.** A function does one thing at one
  level of abstraction; anything with its own name, branch, or rule is extracted so it can be
  called and asserted **in isolation, without I/O, without mocks of the whole world**. Concretely:
  pure business rules are separated from orchestration and from I/O (compute in a pure function,
  side effects at the edges), so a test needs no DB/HTTP/filesystem to exercise the rule; a private
  helper that is hard to test in isolation is a signal the seam is in the wrong place, not a reason
  to skip the test. This is what makes the *max function lines 50* / *complexity ≤ 10* gates
  achievable rather than gamed, and it is the mechanism behind the coverage floor: coverage reached
  only through end-to-end paths, with untestable god-functions underneath, does not satisfy this rule.

- **Code is read far more often than it is written — optimise for the reader, and standardise
  the form.** Two properties, and both are reviewable:
  1. **Readable.** A reader — human or agent — understands *what* a unit does from its name and
     signature, and *why* from the surrounding names, without reconstructing it line by line.
     Concretely: intention-revealing names (`is_dispatchable`, not `check`, `flag`, `tmp`, `data`,
     `d`, `x`), no abbreviation that is not domain vocabulary, guard clauses instead of nested
     `if`s, one idea per line, explicit over clever. A comment explains a *why* that the code
     cannot carry; a comment that restates the code is noise, and a comment that compensates for
     an unreadable line is the wrong fix — rename or extract instead.
  2. **Standardised.** The same intent is written the same way everywhere: the formatter and the
     linter own the form (Ruff format + Ruff lint on Python, ESLint + Prettier on TS), and their
     verdict is not negotiated in review. Style is never a review topic — the tool already
     decided. Two files solving the same problem in two different shapes is a defect even when
     both work.

- **Avoid lambdas and anonymous constructs — a named function is the default.** An anonymous
  function has no name, so it cannot be described, called from a test, or found in a traceback:
  the stack frame reads `<lambda>` and the reviewer reads a puzzle. Rules:
  - **Python: a `lambda` is only ever an inline key/predicate that fits on the line it is used
    on** (`sorted(items, key=lambda i: i.rank)`). Assigning a lambda to a name is forbidden —
    `f = lambda x: …` is a `def` written badly (Ruff `E731`). Anything with a branch, a call
    chain, or its own rule becomes a `def` with a name, and prefer `operator.attrgetter`/
    `itemgetter` where they say it more plainly.
  - **TypeScript/JS: arrows stay as short callbacks** (`map`/`filter`/`reduce`, one-to-three-line
    predicates) or as a component's inline handler when it merely forwards. A handler carrying
    logic is a named function, hoisted out of the render path.
  - **Forbidden in every language**: an anonymous function longer than ~3 lines, a nested named
    function over 5 lines (extract it to the top level), a lambda used to defer or fake a
    dependency where an injected object belongs, and clever one-liners — a nested comprehension
    with two `for`s and a condition, a chained ternary — that trade a reader's minute for a
    writer's second.
  The test is mechanical: if you cannot give the expression a name that fits in three words, it
  is doing too much to stay anonymous. Mechanisation: Ruff (`E731`, `C901`, `PLR0912`, `SIM`),
  ESLint (`func-style: declaration`, `max-nested-callbacks: 2`, `complexity`).

- **Basic optimisations and known anti-patterns are caught in review and in CI.** Code is written
  correct-then-obvious first — **no speculative micro-optimisation**, no premature caching, no
  hand-tuned trick without a measurement (profile before optimising; `perf` claims come with
  numbers). But the *basic* wins are non-negotiable because they are algorithmic, not clever:
  1. **Right data structure** — membership test on a `set`/`Map` (O(1)), not a linear scan of a list;
     index/dict lookup instead of a nested loop (O(n²) over a joinable key is a defect);
     a single pass instead of repeated traversals of the same collection.
  2. **No work in a loop that is loop-invariant** — hoist the constant computation, the compiled
     regex, the config read, the connection setup.
  3. **No N+1, and query the store efficiently** — database queries and network/API calls are
     batched or eager-loaded (`selectinload`/`joinedload`, bulk endpoints); a query inside a `for`
     over rows is a defect. In the same spirit: an **existence check** uses a dedicated exists-query,
     never a full fetch then a length; **writes are batched** (bulk create/update) instead of a loop
     of single-row writes; only the **columns/fields actually used** are selected (projection, not
     `SELECT *` into an object graph); and **aggregation runs in the store**, not a Python/JS loop
     summing rows the app just pulled over the wire. Frontend equivalent: no request per list item,
     no re-render per keystroke without debounce, no unmemoised derived state recomputed on every
     render.
  4. **Bounded resources** — no unbounded `SELECT *` / unpaginated list endpoint, no full-file read
     of arbitrary-size input (stream it), explicit timeouts on every outbound call, connections and
     file handles closed via context managers. Every column used to **filter or sort a large table
     is indexed** — an unindexed predicate on a growing table is a latent full scan.
  5. **Known anti-patterns are named and rejected**: god object/function, copy-paste duplication
     (factor into `chrysa-lib` — see *no code duplication*), boolean trap parameters, primitive
     obsession over a value object, deep nesting (guard clauses instead), mutable default arguments,
     shared mutable global state, silent `except: pass` (see *typed errors*), stringly-typed domains,
     circular imports, and dead code kept "just in case" (git is the archive).
  Mechanisation: Ruff (`C901`, `PLR*`, `B`, `SIM`, `PERF`, `RUF`) + Mypy on Python, ESLint
  (`complexity`, `no-await-in-loop`, `react-hooks/exhaustive-deps`) on TS, the code-quality
  analysis service rating **A** with 0 hotspot on both. A finding here is a defect to fix, not a warning to carry.
  The armed Ruff selection is the canonical set distributed by `scripts/pyproject-ruff-merge.py`
  and merged into each repo's `[tool.ruff.lint] select` — the script is the source of truth for
  which codes are on. Two rules that the `PLR*`/`RUF` shorthand above would otherwise imply are
  **deliberately excluded**, and stay excluded until a decision says otherwise:
  - `PLR2004` (magic-value-comparison) — 2519 findings across the 65 repos. Hardcoded constants
    are a chantier with its own remediation (extract to an enum or external config), not a flag
    to flip; arming it would turn every gate red at once.
  - `RUF001` (ambiguous-unicode-character-string) — 493 findings concentrated on 4 repos, all of
    them French user-facing copy using typographic characters (apostrophes, non-breaking spaces).
    The rule is right about the codepoints and wrong about the intent. A repo that wants it may
    arm it locally together with `lint.allowed-confusables`.

- **A cache is a correctness contract, not a sprinkle of speed.** The moment a value is cached,
  three questions must have answers, or the cache is a bug: **how it expires**, **how it is
  invalidated**, and **what it may not hold**. Concretely: caching is **read-through / cache-aside**
  behind the data-access layer, never scattered `get`/`set` calls in business code; every entry has
  a **TTL taken from the per-repo contract** (*no hardcoded constants* — a literal `3600` in a
  decorator is the defect), and the store is **bounded** (a max size / eviction policy — an
  unbounded cache is a memory leak with latency). A **write invalidates or updates** the entries it
  affects in the same path (a read-your-writes guarantee — a stale cache after a mutation is the
  same defect as FE-080's stale screen), and a cache miss under load is **stampede-protected**
  (single-flight / lock / jittered TTL) so an expiry does not turn one slow query into a thousand.
  What is **never cached** is as governed as what is: an **authorization decision** is not cached
  across principals, and **personal/secret data** is cached only within its classification
  (`DA-001`, `GV-040`) with an owner. Cache keys are namespaced and versioned so a shape change
  cannot serve a poisoned old value. A cache nobody can explain the invalidation of is removed.

## Quality gates

- Test coverage **>= 85%** by default. A repo may override upward, never below 80%.
- Lint warnings: **0**. Mypy clean. Code-quality analysis service rating **A**, 0 security hotspot.
- Max function lines 50 · max file lines 500 · cyclomatic complexity heuristic <= 10.
- **Performance and cost budgets are declared per profile and enforced.** Frontend bundle,
  Docker image size, startup time, memory, CPU, latency, throughput, storage and log volume
  each carry a budget; AI paths additionally budget tokens, cost, latency, concurrency and
  cache. CI measures them and **blocks significant regressions** (info → warning → error); an
  overrun carries a justification, an impact measurement and a reduction plan — never a silent
  pass. Detail: annexe `CI-CD.md` CI-053.

## Error handling pattern (all automations)

```text
try:    fn()
except: gh issue create --title "[chrysa] failure" --label "chrysa-error"
```
