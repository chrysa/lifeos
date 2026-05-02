.PHONY: quality-gate-baseline quality-gate-verify

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python scripts/quality_gate.py verify
