# Makefile for tools/ — developer workflow targets
#
# Usage (from repo root):  make -C tools/ check
# Usage (from tools/):     make check
#
# Requires: uv (https://github.com/astral-sh/uv)

TOOLS_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.DEFAULT_GOAL := all

.PHONY: all
all: format check render-review-template test

.PHONY: help
help:
	@echo "Developer workflow targets for tools/"
	@echo ""
	@echo "  make check    — lint all Python tools with ruff"
	@echo "  make format   — format all Python tools with ruff"
	@echo "  make render-review-template - strictly generate the reviewer template include"
	@echo "  make check-review-template  - verify the generated include is current"
	@echo "  make test     — run unit tests (tools/auto-mir/tests/)"
	@echo "  make clean    — remove __pycache__ directories"
	@echo ""
	@echo "Targets can be scoped to a subdirectory, e.g.:"
	@echo "  make -C tools/auto-mir check"

.PHONY: check
check:
	uv tool run ruff check $(TOOLS_DIR)

.PHONY: format
format:
	uv tool run ruff format $(TOOLS_DIR)

.PHONY: test
test:
	uv run --with pytest pytest $(TOOLS_DIR)auto-mir/tests/ -v

.PHONY: render-review-template
render-review-template:
	python3 $(TOOLS_DIR)auto-mir/render_review_template.py --strict

.PHONY: check-review-template
check-review-template:
	python3 $(TOOLS_DIR)auto-mir/render_review_template.py --strict --check

.PHONY: clean
clean:
	find $(TOOLS_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(TOOLS_DIR) -name "*.pyc" -delete 2>/dev/null || true
