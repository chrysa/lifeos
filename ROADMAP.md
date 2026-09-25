# Roadmap — lifeos (my-assistant)

> Only work that is stated in the repository is listed. Items come from the
> README "Status" table (⬜ = planned), CLAUDE.md architecture, and
> ADR-LIFEOS-001 "Consequences". No dates are invented; none are given in-repo.

## Shipped today (FACT — README Status ✅ + tests)

- Click CLI (`lifeos` / `python -m lifeos`) with `--config`, `--ui/--headless`, `--enable`, `--debug`, `--version`.
- TOML config loader (Pydantic) — optional file, defaults when absent.
- Plugin enable/disable **flags** for `discord`, `github`, `notion` (flags only — no plugin logic).
- Headless application core (logs resolved config + enabled plugins, reports ready).
- Sentry observability init.

## Planned — stated but not implemented (FACT — README ⬜ / CLAUDE.md)

- Floating overlay UI (PySide6) — `[ui]` extra declared; `--ui` currently warns and runs headless.
- System tray (`QSystemTrayIcon`) + context menu.
- Plugin system: `BasePlugin` ABC (`setup`/`teardown`/`get_status`), event emitter.
- Messaging plugin (Discord webhook + bot channel monitor).
- AI plugins: OpenCode REST client (port 4096), OpenAI-compatible chat client (streaming).
- Service plugins: Notion REST v1, GitHub REST.
- System monitoring (psutil) emitting `SystemStatsEvent`.
- Chat + system-stats UI components.

## Strategic re-framing (FACT — ADR-LIFEOS-001 follow-ups)

- Retire the "floating AI assistant / my-assistant" identity in README and repo metadata.
- Define and publish `personal.*` capability manifests for LOGOS to discover/consume/govern.
- Remove any direct source/data coupling; route all data + governance through LOGOS via versioned contracts.
- Fatal-hypothesis watch: if LOGOS never ships a capability host, revisit the boundary.

## Related repositories (FACT — CLAUDE.md "Related repositories")

`chrysa/ai-aggregator` (future AI-routing backend), `chrysa/discord-bot-back`,
`chrysa/server` (Phase-7 k8s deploy `assistant.ducal.me:8000`),
`chrysa/diy-stream-deck`, `chrysa/github-actions`, `chrysa/pre-commit-tools`,
`chrysa/shared-standards`, and **LOGOS** (per ADR — the consumer/governor).

> UNKNOWN: sequencing/priority between these planned items is not recorded in-repo.
