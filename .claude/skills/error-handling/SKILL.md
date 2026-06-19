# Skill: Error handling — structured errors, correlation IDs, Sentry

## When to invoke
Auto-invoke when: adding error handling to a FastAPI endpoint, setting up logging, integrating Sentry, reviewing error responses for consistency, designing exception hierarchies.

## 1. Correlation ID — mandatory on every service

Every FastAPI app MUST include `CorrelationIDMiddleware`. See `chrysa/ai-aggregator/api/middleware/correlation.py` as the reference implementation.

```python
# api/main.py
from api.middleware.correlation import CorrelationIDMiddleware
app.add_middleware(CorrelationIDMiddleware)
```

Every log record MUST include the correlation ID when inside a request context:
```python
import logging
logger = logging.getLogger(__name__)

@router.post("/completions")
async def create_completion(request: Request, body: CompletionRequest) -> CompletionResponse:
    logger.info(
        "completion request received",
        extra={"request_id": request.state.request_id, "prompt_len": len(body.prompt)},
    )
```

## 2. Exception hierarchy

Define domain exceptions in `api/domain/exceptions.py`, not inline in routers:

```python
# api/domain/exceptions.py
class DomainError(Exception):
    """Base for all domain errors."""

class NotFoundError(DomainError):
    """Entity not found."""

class ConflictError(DomainError):
    """Entity already exists / uniqueness violation."""

class ValidationError(DomainError):
    """Input failed domain-level validation (distinct from Pydantic)."""
```

Map to HTTP status codes in a single exception handler, not per-endpoint try/except:

```python
# api/main.py
from fastapi import Request
from fastapi.responses import JSONResponse
from api.domain.exceptions import NotFoundError, ConflictError, ValidationError

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "request_id": request.state.request_id},
    )

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc), "request_id": request.state.request_id},
    )
```

**Rule**: routers should `raise DomainError` subclasses, never `raise HTTPException` for business errors.

## 3. Structured error response envelope

All error responses MUST follow this JSON shape:

```json
{
  "detail": "Human-readable error message",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "NOT_FOUND"
}
```

Pydantic schema:
```python
class ErrorResponse(BaseModel):
    detail: str
    request_id: str
    code: str = "INTERNAL_ERROR"
```

## 4. Sentry integration

```python
# api/main.py — add after app creation
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,   # 10% of requests
        environment=os.getenv("ENVIRONMENT", "development"),
        release=os.getenv("APP_VERSION", "0.0.0"),
    )
```

### Capture with correlation ID as tag
```python
import sentry_sdk

async def some_service_call(request_id: str) -> None:
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("request_id", request_id)
        try:
            await risky_operation()
        except Exception:
            sentry_sdk.capture_exception()
            raise
```

## 5. Logging configuration

Use structured logging (JSON) in production:

```python
# api/logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        return json.dumps(log_record)
```

```python
# In lifespan or app startup:
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)
```

## 6. Testing error handling

```python
async def test_not_found_returns_404_with_request_id(mocker: MockerFixture) -> None:
    from api.main import app
    mocker.patch("api.services.registry.get_entry", side_effect=NotFoundError("prompt not found"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/prompts/registry/missing/1")

    assert response.status_code == 404
    body = response.json()
    assert "request_id" in body
    assert body["detail"] == "prompt not found"
```

## 7. Forbidden patterns

| Anti-pattern | Fix |
|---|---|
| `raise HTTPException(status_code=404)` inline in router | `raise NotFoundError(...)` — handler maps to 404 |
| No `request_id` in error response | Always include via exception handler |
| `except Exception: pass` (silent swallowing) | Log + re-raise or return structured error |
| `print(traceback)` in production | Use `logger.exception()` which includes traceback |
| Sentry DSN hardcoded | Always from `os.getenv("SENTRY_DSN")` |
