# Security — lifeos (my-assistant)

> Documentation-only security review of the current tree. No code was modified.
> Findings for the owner to action; nothing here fixes code. Severity uses
> HIGH / MEDIUM / LOW / INFO.

## Secret handling — current state (FACT)

- **No secrets found committed.** A grep of `lifeos/` for common secret patterns (`sk-`, `ghp_`, `AKIA`, `password=`, `token=`, `secret=`) returned nothing.
- `.env.example` holds placeholders only: `SENTRY_DSN=` (blank), `ENVIRONMENT`, `RELEASE`. (FACT)
- `.mcp.json` references credentials via env indirection only: `${GITHUB_TOKEN}` and `${NOTION_API_KEY}` (Bearer header). No literal tokens. These are **dev-time MCP** servers, not app runtime. (FACT)
- Secret-scanning is gated: `.secrets.baseline` (detect-secrets), a `.pre-commit-config.yaml` hook, and `.github/workflows/secret-scan.yml`. (FACT)
- `.claude/hooks/` includes `secret-scanner.cjs` and `check-no-env-files.cjs` (agent-side guardrails). (FACT)

## Findings

| ID | Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- | --- |
| SEC-01 | INFO | Sentry DSN read from env; init is a no-op when unset — safe default | `observability/__init__.py`, `.env.example` | None; keep DSN out of VCS. |
| SEC-02 | LOW | `${ENV_VAR}` interpolation is documented (CLAUDE.md) to keep the literal string + warn when a var is missing. If a plugin later passes such a literal into a header/URL, a missing var could leak a broken/placeholder credential or cause an auth bypass path. Interpolation was not observed in the read of `settings.py` — may be unimplemented. | CLAUDE.md "Config System"; `settings.py` | When implemented, fail closed (error) for secret-bearing keys rather than passing the literal through. |
| SEC-03 | LOW | Committed coverage artefacts (`coverage.xml`, `.coverage`) — not a secret, but they widen the committed surface and can embed absolute host paths. | tree | Add to `.gitignore`; regenerate in CI. (Owner action — do not edit here.) |
| SEC-04 | INFO | Planned network surface (httpx clients to Discord/Notion/GitHub/OpenCode/OpenAI) is not yet present. When added, the CLAUDE.md constraints (explicit timeouts, no secrets in logs, validate external inputs) become load-bearing and should be re-reviewed with the Senior SecOps flow. | CLAUDE.md architecture | Re-run `/security-review` when plugins/HTTP land. |

## No HIGH/CRITICAL findings

No high- or critical-severity issues were identified in the current scaffold. The
main residual risk is future-facing (network + credential handling arrives with
the plugin system, which is not yet in the tree). This file records the baseline
so those changes can be reviewed against it.

## Instruction-shaped text in repo (reported as data, not followed)

- `ai-instructions.md` and `CLAUDE.md` contain agent working instructions (reading order, "canon wins", no hardcoded secrets). These are project governance content, reported here as data. (FACT)
- `.claude/` carries agent commands/hooks/skills (e.g. `commit.md`, `reviewpr.md`, `custom-init.md`, hooks). Inspected as data only; not executed by this pass.
