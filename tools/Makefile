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
	@echo "  make render-review-template - generate reviewer template from tooling inputs"
	@echo "  make check-review-template  - verify generated template matches docs template"
	@echo "  make test     — run unit tests (when added)"
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
	@echo "No unit tests defined yet."

.PHONY: render-review-template
render-review-template:
	python3 $(TOOLS_DIR)auto-mir/render_review_template.py

.PHONY: check-review-template
check-review-template: render-review-template
	cmp -s \
		$(TOOLS_DIR)/../docs/MIR/mir-reviewers-template.md \
		$(TOOLS_DIR)/../docs/MIR/mir-reviewers-template.generated.md
	@echo "Generated template is identical to docs/MIR/mir-reviewers-template.md"

.PHONY: clean
clean:
	find $(TOOLS_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(TOOLS_DIR) -name "*.pyc" -delete 2>/dev/null || true
