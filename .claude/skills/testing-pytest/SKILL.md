---
name: testing-pytest
description: 'Use when writing tests, modifying test files, adding new pytest fixtures, debugging test failures, migrating unittest → pytest.'
---

# Testing with pytest

## When to invoke
Auto-invoke when: writing tests, modifying test files, adding new pytest fixtures, debugging test failures, migrating unittest → pytest.

## Rules

### Framework
- **pytest ONLY** — `unittest.TestCase` is forbidden
- `pytest-mock` for all mocks: `MockerFixture`, `mocker.patch`, `mocker.AsyncMock`
- `pytest-asyncio` for async tests: `@pytest.mark.asyncio` (or `asyncio_mode = "auto"` in config)
- `pytest-cov` for coverage

### Constants
Every test module references `tests/constants.py` — never hardcode URLs, strings, or IDs:
```python
# tests/constants.py
BASE_URL = "http://testclient"
ROUTES = {
    "health": "/health",
    "completions": "/api/v1/completions",
}
def url(route_key: str) -> str:
    return f"{BASE_URL}{ROUTES[route_key]}"
```

### Mocking pattern
```python
# Always use mocker.AsyncMock for coroutines
async def test_something(mocker: MockerFixture):
    mock_service = mocker.AsyncMock(return_value={"result": "ok"})
    mocker.patch("module.path.service_fn", mock_service)
    ...
    mock_service.assert_awaited_once()
```

### Assertions
Every `assert` carries a message in f-string debug format (`{var=}`) — it names what was expected and what was received. Bare `assert x == y` is forbidden.
```python
assert count == 5, f"expected 5 items, got {count=}"
assert user.is_active, f"user should be active: {user.id=} {user.is_active=}"
```

### Fixtures — parametrizable factories
A fixture returns a `_load(**kwargs)` callable with faker/factory defaults, so a test overrides only what it cares about. House convention: function named `fixt_<name>`, exposed as `name="<name>"`.
```python
@pytest.fixture(name="user_data")
def fixt_user_data(faker):
    def _load(**kwargs):
        return {"email": kwargs.get("email", faker.email())}
    return _load
```
`scope="function"` by default; widen (`module` / `session`) only for immutable, expensive-to-build data. Never a static fixture with hardcoded values.

### Parametrize, never loop
A loop hides failures — once one case fails the later ones never run — and loses per-case isolation. Use `@pytest.mark.parametrize`:
```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_positive(value):
    assert process(value) > 0, f"{value=}"
```

### Structure & isolation
- Group related cases as **nested classes** under one class per unit (`class TestMqtt: class TestConnection: ...`) — not many module-level classes for the same unit.
- **Unit tests mock the DB and all external I/O** (no DB marker). **Integration tests** are marked explicitly (`@pytest.mark.integration`, plus `@pytest.mark.django_db` on Django) and hit the real DB.
- **No type annotations** in test files — they read as executable specs.

### Coverage — cover every path
Target 100% branch coverage on business logic and services: every `if/elif/else`, every error/exception path, every fallback and default. Assert side effects too (DB writes, emitted logs), not only return values.

### Status codes
```python
from fastapi import status
# or
from http import HTTPStatus

assert response.status_code == status.HTTP_200_OK
assert response.status_code == HTTPStatus.CREATED
```

### File structure
```
tests/
  constants.py       # single source of truth for all test strings/routes
  conftest.py        # shared fixtures (TestClient, DB session, etc.)
  test_<domain>.py   # one file per domain module
```

### Forbidden
- `import unittest` in test files
- Hardcoded route strings (`"/api/v1/completions"` inline)
- Integer status codes (use `status.HTTP_*` or `HTTPStatus.*`)
- `from unittest.mock import patch` — use `mocker.patch` instead
- Bare `assert` without a descriptive message
- Loops over test cases (use `@pytest.mark.parametrize`)
- Static fixtures with hardcoded values (use the `_load(**kwargs)` factory pattern)
- Type annotations in test files
