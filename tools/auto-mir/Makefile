.PHONY: lint unit test setup teardown integration

# Name of the file where the integration VM name is stored between make targets.
INT_VM_FILE := .int-vm-name

# Run ruff format and lint checks.
lint:
	uv tool run ruff format --check .
	uv tool run ruff check .

# Run unit and mock tests (no VM required; uses VM if AUTO_MIR_TEST_VM is set).
unit:
	pytest tests/ -v

# Fast target: lint + unit tests (no VM needed).
test: lint unit

# Provision a fresh integration VM and record its name in $(INT_VM_FILE).
setup:
	python3 tests/run_integration.py setup

# Destroy the integration VM recorded in $(INT_VM_FILE).
teardown:
	python3 tests/run_integration.py teardown

# Full integration run: lint first (bails before any VM cost on failure), then
# provision a VM, run the complete test suite with AUTO_MIR_TEST_VM set, and
# always tear the VM down via an EXIT trap even when tests fail.
integration: lint
	@$(MAKE) setup && \
	    trap "$(MAKE) teardown" EXIT && \
	    AUTO_MIR_TEST_VM=$$(cat $(INT_VM_FILE)) $(MAKE) unit
