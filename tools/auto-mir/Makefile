.PHONY: test integration

# Fast target: lint + unit/mock tests (no VM required)
test:
	uv tool run ruff format --check .
	uv tool run ruff check .
	pytest tests/ -v

# Slow target: provisions a fresh LXD VM, runs the full test suite including
# integration tests, then destroys the VM.  Requires lxd to be available.
integration:
	python3 tests/run_integration.py
