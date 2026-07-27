---
name: api-design
description: 'Use when designing new API endpoints, reviewing API responses, adding HTTP status codes, writing FastAPI routes, defining request/response schemas.'
---

# REST API Design

## When to invoke
Auto-invoke when: designing new API endpoints, reviewing API responses, adding HTTP status codes, writing FastAPI routes, defining request/response schemas.

## Core rules

### Resource naming
```
✅ /api/v1/projects           # plural noun
✅ /api/v1/projects/{id}      # sub-resource with ID
✅ /api/v1/projects/{id}/tasks
❌ /api/v1/getProjects         # no verbs in path
❌ /api/v1/project             # no singular
```

### HTTP Methods
| Method   | URL                  | Action               | Success code  |
|----------|----------------------|----------------------|---------------|
| `GET`    | `/resources`         | List                 | `200 OK`      |
| `GET`    | `/resources/{id}`    | Get one              | `200 OK`      |
| `POST`   | `/resources`         | Create               | `201 Created` |
| `PUT`    | `/resources/{id}`    | Full replace         | `200 OK`      |
| `PATCH`  | `/resources/{id}`    | Partial update       | `200 OK`      |
| `DELETE` | `/resources/{id}`    | Delete               | `204 No Content` |

### Status codes — always use constants
```python
from fastapi import status
# or
from http import HTTPStatus

# 2xx
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT

# 4xx
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
status.HTTP_409_CONFLICT
status.HTTP_422_UNPROCESSABLE_ENTITY

# 5xx
status.HTTP_500_INTERNAL_SERVER_ERROR
status.HTTP_503_SERVICE_UNAVAILABLE
```
**Forbidden**: hardcoded integers (`200`, `404`, `500`)

### Response envelope
```json
// Success list
{ "data": [...], "total": 42, "page": 1 }

// Success single
{ "data": { "id": "...", ... } }
```
Errors use **RFC 7807 Problem Details** (see *Errors* below), never this envelope.

### FastAPI route pattern
```python
from fastapi import APIRouter, status
from .schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
async def list_projects(service: ProjectService = Depends(get_service)):
    return await service.list()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, service: ProjectService = Depends(get_service)):
    return await service.create(payload)
```

### Security (OWASP Top 10)
- Auth: `Authorization: Bearer <token>` — never in query params
- Validate all inputs with Pydantic schemas
- Rate limit public endpoints
- CORS: explicit `allow_origins`, never `["*"]` in production
- No sensitive data in `4xx/5xx` error bodies

### Versioning (mandatory from V1)
- Version in URL path: `/api/v1/...`, `/api/v2/...` (alt header `Accept: application/vnd.<project>.v1+json`).
- Never break existing v1 contracts — add v2 for breaking changes.
- **Max 2 versions supported simultaneously**; deprecation cycle >= 6 months.
- Sunset a version with `Deprecation` + `Sunset` response headers.

### HATEOAS — pragmatic (REST level 3, moderate)
**Required on primary resources**, not on everything:
```json
{
  "id": 42,
  "name": "...",
  "_links": {
    "self":    { "href": "/api/v1/missions/42" },
    "next":    { "href": "/api/v1/missions/43" },
    "vehicle": { "href": "/api/v1/vehicles/12" }
  }
}
```
- Format is a per-project choice (documented in a project ADR): HAL
  (`application/hal+json`, recommended for public APIs), JSON:API (existing tooling), or a
  lightweight custom `_links`.
- **Caveat**: do not generate a full graph on every response. Include only links useful to
  client navigation (`self`, pagination, directly-consumed related resources). Do not fill
  `_links` with every possible action the client never uses.

### Errors — RFC 7807 Problem Details
```json
{
  "type": "https://docs.<project>/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Field 'email' is required",
  "instance": "/api/v1/users",
  "errors": [ ]
}
```
- Correct HTTP codes (4xx client, 5xx server, 422 validation).
- **Never** a stack trace in production, and no sensitive data in any `4xx`/`5xx` body.

### Pagination & filtering
- Pagination is mandatory on list endpoints: `?page=1&size=20`, **max `size` = 100**.
- Standard filtering/sort: `?filter[status]=active&sort=-created_at`.
- Total count in the `X-Total-Count` header + `_links.{next,prev,first,last}`.

### OpenAPI / Swagger
- Swagger UI at `/docs` — **auth-protected in production**. ReDoc at `/redoc` — read-only,
  may stay public.
- Schema source of truth: Pydantic v2 (FastAPI) or DRF serializers (Django). Document every
  endpoint: params, responses, errors, examples.
- CI: `openapi-spec-validator` + breaking-change detection (`oasdiff`).
- **Conditional visibility**: the generated schema must reflect the authenticated caller's
  permissions — endpoints the caller cannot access are **omitted** (or `x-hidden: true` when
  dynamic omission is unsupported). Never expose protected routes to an unauthenticated or
  under-privileged caller.
