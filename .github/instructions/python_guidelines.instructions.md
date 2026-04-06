---
applyTo: "**/*.py"
---

# Python Guidelines — my-assistant

## Version & Runtime

- Python **3.14** minimum
- `from __future__ import annotations` in every file
- Target: runs on Linux **and** Windows — no platform-specific imports in `core/` or `plugins/`

## Typing

- Strict mypy: no `Any`, no untyped defs
- PEP 585 generics: `list[str]`, `dict[str, int]` — never `List`, `Dict`
- PEP 604 unions: `str | None` — never `Optional[str]`

## HTTP (all external calls)

```python
import httpx

async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
    resp = await client.get(url, headers=headers)
    resp.raise_for_status()
```

Never use `requests`. Never use `urllib`. Explicit timeout always.

## Async patterns

- All I/O in plugins: `async def` — never blocking calls in event loop
- Use `asyncio.to_thread()` for unavoidable blocking operations
- Never `asyncio.sleep(0)` as workaround — fix the blocking code

## Config

```python
# ✅ Correct — env var interpolation
token: str = Field(default="${GITHUB_TOKEN}")

# ❌ Forbidden
token: str = "ghp_hardcoded_value"
```

## Plugins

```python
from plugins.base import BasePlugin

class SomePlugin(BasePlugin):
    async def setup(self) -> None:
        try:
            await self._init()
        except Exception as exc:
            self.logger.warning("setup failed: %s", exc)
            # NEVER re-raise — plugin failures must not crash the app

    async def teardown(self) -> None:
        ...

    def get_status(self) -> dict[str, object]:
        return {"active": self._active}
```

## Security (OWASP)

- No secrets in logs (`self.logger.warning(...)` — redact tokens)
- Validate all external API responses before use
- No hardcoded credentials — always env var interpolation
