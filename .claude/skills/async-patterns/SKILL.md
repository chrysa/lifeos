# Skill: Async patterns for FastAPI + SQLAlchemy 2.0

## When to invoke
Auto-invoke when: writing async FastAPI endpoints, setting up SQLAlchemy async sessions, writing async tests, using asyncio/anyio, creating background tasks, or designing repository classes.

## 1. DB engine — lifespan pattern (mandatory)

Never use global mutable state for the engine. Always use FastAPI's lifespan:

```python
# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.db.session import create_engine_from_config

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    engine, session_factory = create_engine_from_config()
    app.state.session_factory = session_factory
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

```python
# api/db/session.py
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

def create_engine_from_config(database_url: str | None = None) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    url = database_url or get_url_from_config()
    engine = create_async_engine(url, echo=False, pool_pre_ping=True)
    return engine, async_sessionmaker(engine, expire_on_commit=False)

async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session
```

**Why**: A module-level `_engine: AsyncEngine | None = None` singleton creates a shared mutable state across tests. Tests that run in parallel corrupt each other's circuit state.

## 2. Repository pattern

Wrap all DB access in a repository class injected via `Depends`:

```python
# api/infrastructure/repositories/prompt_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.models import PromptEntry

class PromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(self, key: str, version: int) -> PromptEntry | None:
        stmt = select(PromptEntry).where(
            PromptEntry.key == key,
            PromptEntry.version == version,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, entry: PromptEntry) -> PromptEntry:
        self._session.add(entry)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry
```

```python
# Dependency factory
def get_prompt_repo(session: AsyncSession = Depends(get_session)) -> PromptRepository:
    return PromptRepository(session)
```

## 3. Testing async code

### Required setup
```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"   # all async test functions run automatically
```

### DB fixtures use SQLite in-memory
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from api.db.base import Base

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
```

### Override get_session in router tests
```python
app.dependency_overrides[get_session] = lambda: db_session_fixture
```

### Mock async providers
```python
# Always pytest-mock, never unittest.mock
async def test_service_calls_provider(mocker: MockerFixture) -> None:
    mock_provider = mocker.AsyncMock()
    mock_provider.complete.return_value = ProviderResponse(...)
    service = CompletionService(provider=mock_provider)
    await service.complete(request)
    mock_provider.complete.assert_awaited_once()
```

## 4. Forbidden patterns

| Anti-pattern | Fix |
|---|---|
| `global _engine: AsyncEngine \| None = None` | Use lifespan + `app.state` |
| `asyncio.run(...)` inside FastAPI route | Already in async context — just `await` |
| `loop.run_until_complete()` anywhere | Use `anyio.from_thread.run_sync()` if crossing thread boundary |
| `session.execute(stmt).fetchall()` | Use `(await session.execute(stmt)).fetchall()` |
| `async with AsyncSession(engine)` in each function | Use `get_session` dependency — never create ad-hoc sessions in services |
| Module-level `async_sessionmaker(engine, ...)` singleton | Always scoped to lifespan |

## 5. Background tasks

```python
# Prefer FastAPI BackgroundTasks over asyncio.create_task for request-scoped work
@router.post("/jobs")
async def create_job(
    body: JobRequest,
    background_tasks: BackgroundTasks,
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    job = await service.create(body)
    background_tasks.add_task(service.process, job.id)
    return job
```

For long-running independent tasks (not request-scoped): use a task queue (Redis + arq or Celery), not `asyncio.create_task` — those tasks are lost on restart.

## 6. Connection pool tuning (production)

```python
# For a single Kimsufi node with multiple services:
engine = create_async_engine(
    database_url,
    pool_size=5,         # connections per worker
    max_overflow=10,     # burst connections
    pool_pre_ping=True,  # detect stale connections
    pool_recycle=3600,   # recycle connections every hour
)
```
