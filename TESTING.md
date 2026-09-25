# Testing — lifeos (my-assistant)

> Grounded in `pyproject.toml [tool.pytest]`, the Makefile, `Dockerfile.test`,
> `tests/`, and CONTRIBUTING.md. Commands below are copied from the repo; they
> were **not executed** by this documentation pass (docs-only).

## Framework & layout

- **pytest** (+ `pytest-asyncio`, `pytest-cov`, `pytest-mock`) — declared in the `[dev]` extra. (FACT)
- Tests live in `tests/`:
  - `tests/__init__.py`
  - `tests/test_placeholder.py` — despite the name, this is a **real** suite (FACT): it asserts `__version__`/`__author__` types, that `lifeos.main` is callable, CLI `--help`/`--version` exit 0 and echo the version, that the app runs (`run_spy.assert_called_once()`), that `--enable discord` yields `enabled_plugins() == ["discord"]`, config defaults/flags for discord/notion, and that headless mode is logged.
- Per CLAUDE.md the intended future structure is `tests/plugins/` with one unit-test module per plugin; that directory does not exist yet. (FACT)

## Commands (from Makefile / CONTRIBUTING)

```bash
make test          # pytest tests/ -v
make test-cov      # pytest -v --cov --cov-report=term-missing --cov-report=xml
make docker-test   # docker build --target test -f Dockerfile.test && docker run
make ci            # lint + typecheck + test
pre-commit run --all-files
```

- `Dockerfile.test` builds on `python:3.14-slim`, installs `.[dev]`, and runs the suite in-container. (FACT)

## Coverage gate

- `--cov=lifeos --cov-fail-under=85` in `pyproject.toml` addopts → the suite fails under 85% line coverage. Coverage is emitted as `coverage.xml` (for Sonar) and terminal. (FACT)
- `coverage.xml` and `.coverage` are committed artefacts in the tree. (FACT — see REVIEW.md; generated coverage artefacts normally do not belong in VCS.)

## Testing conventions (CLAUDE.md — intent for when plugins land)

- Mock `httpx.AsyncClient` with `pytest-mock`; no real HTTP in unit tests. (planned)
- Stub/monkeypatch `psutil` for system-monitor tests. (planned)
- Skip UI tests in CI (no display) via `pytest.mark.skipif`. (planned)

## CI

- `.github/workflows/` includes `ci.yml`, `sonar.yml`, `quality-gate-check.yml`, `mutation-testing.yml`, `secret-scan.yml` among others (FACT: listed in `llms-full.txt`). The mutation-testing and quality-gate workflows imply stricter-than-coverage gates; their exact thresholds were not read in this pass. (UNKNOWN — verify in the workflow files if needed.)
