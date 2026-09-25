# SECURITY — lifeos

> Documentation-only security review of the current repo. No code was changed.
> Tags: **FACT / INFERENCE / UNKNOWN / PROPOSAL**. HIGH/CRITICAL findings, if
> any, are flagged for the owner to fix — this pass does not modify code.

## Attack surface today (FACT)

lifeos is a **headless local CLI scaffold**. There is:

- No network server, no HTTP API, no database, no file upload, no
  deserialization of untrusted input.
- The only external input is CLI flags (Click-parsed) and an optional local TOML
  config file the operator controls.
- Outbound behaviour is limited to Sentry init when `SENTRY_DSN` is set.

So the OWASP web-app surface is largely **N/A** at this stage.

## Secrets (FACT)

- No hardcoded secrets in `lifeos/` (grep for `sk-`, `ghp_`, DSN/token literals:
  none).
- `.env.example` contains placeholders only (`SENTRY_DSN`, `ENVIRONMENT`,
  `RELEASE`).
- `.mcp.json` references `${GITHUB_TOKEN}` and `${NOTION_API_KEY}` via env — no
  literal tokens. (These MCP servers are **dev-time tooling**, not app runtime.)
- `.secrets.baseline` (detect-secrets) has 4 entries, all "Hex High Entropy
  String" pointing at `.pre-commit-config.yaml` — these are **pre-commit hook
  revision hashes**, not credentials. No real secret is committed. (FACT)
- Sentry is configured with `send_default_pii=False` (FACT) — good default.

No secret values are reproduced in this document.

## Gates in place (FACT)

- `.pre-commit-config.yaml` + `.secrets.baseline` gate secret scanning locally.
- CI includes `secret-scan.yml`, `sonar.yml`, `quality-gate-check.yml`,
  `mutation-testing.yml` under `.github/workflows/`.
- Aligns with the chrysa standard "Security scanning is a gate, not an
  afterthought".

## Findings

- **No HIGH/CRITICAL findings** in the current scaffold (INFERENCE from the
  minimal, offline, server-less surface).
- **INFO / forward-looking (INFERENCE):** the *planned* plugins (Discord webhook,
  OpenAI/OpenCode HTTP clients, GitHub/Notion REST) will introduce a real network
  surface. When implemented they must honour the stated constraints: `httpx`
  with explicit timeouts, no secrets in logs, server-side validation of external
  inputs, and env-addressed endpoints. None of that code exists yet, so it is not
  auditable now.
- **Governance constraint from ADR-LIFEOS-001 (FACT):** LifeOS must **not** access
  Notion or other data sources directly — LOGOS brokers data and governance. The
  planned `plugins/services/notion.py` (described in CLAUDE.md) would conflict
  with this boundary if built as a direct client; that tension should be resolved
  before implementation. This is a design/governance flag for the owner, not a
  code vulnerability.

## Owner action items (PROPOSAL)

1. Decide the Notion/GitHub data-access model against ADR-LIFEOS-001 before
   writing service plugins (broker via LOGOS vs. direct client).
2. When network plugins land, add per-plugin input-validation and timeout tests
   and re-run this review.
