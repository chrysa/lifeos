# Observability — lifeos (my-assistant)

> Grounded in `lifeos/observability/__init__.py`, `.env.example`, `pyproject.toml`
> and CLAUDE.md.

## Logging (FACT)

- Standard-library `logging` configured in `lifeos/cli.py`:
  - Level `DEBUG` when `--debug`, else `INFO`.
  - Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`.
- The app logs resolved config, enabled plugins, headless/overlay mode, and a
  final "LifeOS ready" line (`app.py`). Tests assert the headless message is emitted.

## Error tracking — Sentry (FACT)

- `lifeos/observability/__init__.py` initialises `sentry-sdk` with the
  `LoggingIntegration` (breadcrumbs at INFO, events at ERROR).
- **No-op when `SENTRY_DSN` is unset** — safe for dev/CI without secrets.
- Environment context comes from `.env.example`: `ENVIRONMENT` (default
  `development`) and `RELEASE` (`lifeos@0.1.0`).

## Metrics / tracing (UNKNOWN → none in tree)

- No metrics exporter, tracing, or health-endpoint code is present. The system
  monitor (psutil) that would emit `SystemStatsEvent` is PLANNED, not implemented. (FACT)

## Standards alignment

- The chrysa `standards/rules/observability.md` pointer (CLAUDE.md) mandates
  error-tracking → GitHub issues as a norm and container-vs-app versioning
  visibility. Sentry is wired; the GitHub-issue routing and deployment-visibility
  pieces are not observable in this repo's runtime code. (INFERENCE — those may be
  handled by shared CI/actions, not app code.)

## Quality/regression gates as operational signals (FACT)

- `scripts/quality_gate.py` (`make quality-gate-baseline` / `quality-gate-verify`)
  records baseline metrics and verifies no regression — an operability signal in CI.
- `.quality-gate.json` stores the gate config; `coverage.xml` feeds Sonar
  (`sonar-project.properties`, `sonar.yml`).
