.DEFAULT_GOAL := help

PYTHON := python3
PKG    := my_assistant

.PHONY: help install install-ui dev test lint format clean run run-headless run-discord

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
