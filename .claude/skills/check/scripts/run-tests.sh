#!/usr/bin/env bash
# Auto-detect and run project verification (lint + typecheck + tests).
# Run from the project root. Exits non-zero on failure.
#
# project standard (NON-NEGOTIABLE): tests/lint/build run via Docker, make, or
# pre-commit ONLY — never bare on the host. We therefore prefer a Makefile or
# docker-compose entrypoint and only fall back to host runners for foreign
# projects that ship neither.
set -euo pipefail

if [ -f Makefile ] && grep -qE '^tests?:' Makefile; then
    grep -q '^tests:' Makefile && make tests || make test
elif [ -f docker-compose.yml ] || [ -f compose.yml ]; then
    # Convention: an `app` service exposing the project's `make test`.
    docker compose run --rm app make test
elif [ -f Cargo.toml ]; then
    cargo check && cargo test
elif [ -f tsconfig.json ]; then
    npx tsc --noEmit && npm test
elif [ -f package.json ] && grep -q '"test"' package.json; then
    npm test
elif [ -f pytest.ini ] || [ -f pyproject.toml ] || find . -maxdepth 2 -name "test_*.py" | grep -q .; then
    pytest
else
    echo "(no test command detected - ask the user for the verification command)"
    exit 1
fi
