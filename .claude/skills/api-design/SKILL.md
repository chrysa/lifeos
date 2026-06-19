# Skill: REST API Design

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

// Error
{ "error": { "code": "NOT_FOUND", "message": "Project not found", "detail": null } }
```

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

### Versioning
- Version in URL path: `/api/v1/...`
- Never break existing v1 contracts — add v2 for breaking changes
