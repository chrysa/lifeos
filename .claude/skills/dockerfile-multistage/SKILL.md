# Skill: Dockerfile multi-stage Python 3.14

## When to invoke
Auto-invoke when: creating or modifying a Dockerfile, updating docker-compose.yml, adding new services, changing Python version, asking about container strategy.

## Pattern

**4 mandatory stages: `base → builder → production → dev`**

```dockerfile
# syntax=docker/dockerfile:1.7

# Stage 1: OS base (shared parent)
FROM python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Stage 2: builder — installe les dépendances runtime UNIQUEMENT
FROM base AS builder
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Stage 3: production — IMAGE MINIMALE (pas pip, pas setuptools, pas outils build)
FROM base AS production
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ src/   # ou api/ selon le projet
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: dev — étend builder (pas production), contient tout
FROM builder AS dev
RUN pip install --no-cache-dir -e '.[dev]'
COPY src/ src/
COPY tests/ tests/
CMD ["pytest", "tests/", "--cov=app", "--cov-report=term-missing", "-v"]
```

## Rules

- **Python version**: toujours `python:3.14-slim`
- **production** repart de `base` (pas de `builder`) → pas de pip dans l'image finale
- **dev** repart de `builder` (prend tous les steps)
- L'utilisateur `appuser` est non-root dans **production**
- **Pas de venv** — les packages vont directement dans `site-packages` du système du conteneur

## docker-compose.yml
```yaml
services:
  backend:
    build:
      context: .
      target: production    # ← image minimale

  backend-test:
    build:
      context: .
      target: dev           # ← tous les steps
    profiles:
      - test
```

## Makefile
```makefile
test:
    docker compose run --rm --no-deps --profile test backend-test

build:
    docker compose build backend

build-all:
    docker compose build backend backend-test
```

## Forbidden
- `FROM python:3.12` ou toute version < 3.14
- Installer pip dans le stage `production`
- Créer ou activer un venv (`virtualenv`, `python -m venv`, `pip install --user`)
- Copier `pyproject.toml`/`setup.py` dans `production`
