.DEFAULT_GOAL := help

PYTHON := python3
PKG    := lifeos

.PHONY: help install install-ui dev test lint format clean run run-headless run-discord quality-gate-baseline quality-gate-verify

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime dependencies (headless)
	pip install -e .

install-ui:  ## Install with PySide6 overlay UI
	pip install -e ".[ui,discord]"

dev:  ## Install all dev dependencies + pre-commit
	pip install -e ".[ui,discord,dev]"
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov --cov-report=term-missing --cov-report=xml

docker-test: ## Run tests inside Docker
	docker build --target test -f Dockerfile.test -t lifeos-test .
	docker run --rm lifeos-test

lint:  ## Run linter (ruff check)
	ruff check $(PKG) tests

format:  ## Format code (ruff format)
	ruff format $(PKG) tests

clean:  ## Remove build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml .pytest_cache dist build

run:  ## Start with floating overlay UI
	$(PYTHON) -m my_assistant --ui

run-headless:  ## Start headless (system tray only, no overlay)
	$(PYTHON) -m my_assistant --headless

run-discord:  ## Start with Discord plugin enabled
	$(PYTHON) -m my_assistant --ui --enable discord

typecheck: ## Run mypy type checking
	mypy $(PKG) tests

build: clean ## Build wheel distribution package
	$(PYTHON) -m build

pre-commit: ## Run all pre-commit hooks on every file
	pre-commit run --all-files --verbose

# ── Quality Gates ──────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify
