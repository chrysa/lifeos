# Skill: Testing with pytest

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
