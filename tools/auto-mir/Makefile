.PHONY: test

test:
	uv tool run ruff format --check .
	uv tool run ruff check .
	pytest tests/ -v
