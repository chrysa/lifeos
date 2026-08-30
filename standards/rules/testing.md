<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Testing

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Tests: pytest only** — assert-style test functions and `pytest-mock` (`mocker`
  fixture: `mocker.patch`, `mocker.AsyncMock`) for all mocking. The stdlib **`unittest`
  framework (`unittest.TestCase`) and `unittest.mock` imports are forbidden** — no
  `import unittest`, no `from unittest.mock import …`. See the `testing-pytest` skill.

- **Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later.** The
  *pytest only* rule governs Python; it never exempted the frontend from having tests.
  Network is mocked at transport level (MSW/fakes), behaviour is asserted through the
  accessible tree, and every fixed bug ships a regression test. E2E (Playwright) covers
  critical journeys only; **its gate status is declared per repo** in the local `CLAUDE.md` —
  fleet default is non-blocking. Detail: annexe `FRONTEND.md` §4, `TESTING.md`.
