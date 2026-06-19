# Skill: Clean Architecture for FastAPI projects

## When to invoke
Auto-invoke when: creating a new FastAPI module, adding a new domain feature, reviewing existing project structure, deciding where to place new code.

## Layer definitions

Every FastAPI project in the chrysa ecosystem MUST follow this 4-layer structure:

```
api/
  routers/          # HTTP boundary — schemas, Depends injection, HTTP errors only
  services/         # Application layer — orchestrates domain logic + infra
  domain/           # Pure business logic — no FastAPI, no SQLAlchemy, no I/O
  infrastructure/   # Adapters — DB repositories, external providers, clients
  db/               # SQLAlchemy models + session factory (belongs to infrastructure)
  models/           # Pydantic schemas (request/response + domain value objects)
```

## Strict import rules

| Layer | May import | Must NOT import |
|-------|-----------|-----------------|
| `domain/` | stdlib, pydantic | FastAPI, SQLAlchemy, httpx, any I/O |
| `services/` | domain, infrastructure interfaces | FastAPI (except type hints), SQLAlchemy models directly |
| `routers/` | services, models, fastapi | domain (direct), SQLAlchemy, infrastructure |
| `infrastructure/` | domain interfaces, SQLAlchemy, httpx | FastAPI (except `Request` for deps) |

### Enforced rule
If a `routers/*.py` file imports from `sqlalchemy` → it belongs in `services/` or `infrastructure/`.
If a `domain/*.py` file imports from `fastapi` → it belongs in `services/`.

## Required patterns

### Router — HTTP boundary only
```python
# api/routers/completions.py
from fastapi import APIRouter, Depends, HTTPException
from api.models.completions import CompletionRequest, CompletionResponse
from api.services.completions import CompletionService, NoProviderAvailableError

router = APIRouter(tags=["completions"])

@router.post("/completions", response_model=CompletionResponse)
async def create_completion(
    body: CompletionRequest,
    service: CompletionService = Depends(get_completion_service),
) -> CompletionResponse:
    try:
        return await service.complete(body)
    except NoProviderAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
```

### Service — orchestration only
```python
# api/services/completions.py
from api.domain.routing import route_request
from api.infrastructure.providers.base import ProviderGateway

class CompletionService:
    def __init__(self, gateway: ProviderGateway) -> None:
        self._gateway = gateway

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        provider = route_request(request, self._gateway.available())
        return await self._gateway.send(provider, request)
```

### Domain — pure logic, no I/O
```python
# api/domain/routing.py
from dataclasses import dataclass
from api.domain.provider import ProviderInfo

@dataclass(frozen=True)
class RouteDecision:
    provider: str
    reason: str

def route_request(
    required_capability: str | None,
    available_providers: list[ProviderInfo],
) -> RouteDecision:
    # Pure function — no async, no DB, no HTTP
    ...
```

## Project layout checklist (pre-PR gate)

Before merging any new feature:
- [ ] No `sqlalchemy` import in `routers/`
- [ ] No `fastapi` import in `domain/` (except type stubs)
- [ ] No business logic (if/else on domain objects) in `routers/`
- [ ] Every new service has a corresponding `tests/services/test_<name>.py`
- [ ] Every new domain function is a pure function (testable without mocks)

## When to create a new layer file vs. extend existing

- Rule: max 150 lines per service file. If over → split by sub-domain.
- Rule: domain functions that are called from 2+ services → move to `domain/shared.py`.
- Anti-pattern: `services/god_service.py` with 500 lines — split by bounded context.

## Refactoring existing routers that violate boundaries

When a router directly imports SQLAlchemy or builds providers:
1. Extract the logic to a `services/<name>.py`
2. Add the service as a FastAPI dependency via `Depends()`
3. Update tests to mock the service, not the infrastructure
4. The router test should never need a DB fixture

## Reference implementation
See `chrysa/ai-aggregator/` as the canonical reference.
Routers: `api/routers/` — Services: `api/services/` — Engine: `api/engine/` (domain equivalent).
