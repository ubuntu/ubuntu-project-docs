---
applyTo: "tools/**"
---

# Tools development

Scope contract: This file governs automation/tooling code and workflows under
`tools/**`. It does not define MyST semantic-role rules or docs prose conventions
for `docs/**`.


## Command surface

Run commands from the tool directory unless documented otherwise.

For `tools/auto-mir`:

```bash
make test         # lint + unit
make lint         # Ruff format check + Ruff lint
make integration  # full integration flow with VM setup/teardown
```


## Python and linting policy

- Follow `pyproject.toml` for Python and Ruff policy.
- Keep code Ruff-clean by fixing root causes rather than adding broad ignores.
- Preserve explicit typing and typed contracts where already established.


## Commit hygiene for multi-task work

- When handed multiple tasks in one request, produce individual, logically
  separated commits — one per task — rather than a single combined commit.
- Sign-off is not configured here: create every commit with
  `git commit --no-gpg-sign` (It will be reviewed and signed by a human
  reviewer later).
- Validate each commit independently: `make test` (or the tool's documented
  validation target) must pass before committing.


## Planning-mode interactivity

When planning changes under `tools/**` (before writing code):

- Feel empowered to ask. Whenever a requirement, scope boundary, or design
  tradeoff is unclear, ask the user rather than guessing or deferring.
- Aim for full alignment before acting. Resolve open questions up front so the
  agreed plan can be implemented without mid-flight reinterpretation.
- Present "further considerations" as interactive questions, not free-text-only
  prompts. Offer concrete options (with a recommended default where sensible) so
  the user can answer with a quick selection instead of composing prose.


## Source-of-truth boundaries

- Architecture and operating model live in `tools/auto-mir/design.md`.
- Design rationale and tradeoffs live in `tools/auto-mir/decisions.md`.
- Keep this instruction file compact: extract only stable, high-frequency rules.
- Do not migrate full design/decision narratives into `.github/instructions`.


## Guidance extension policy for future tools

- New tools under `tools/<name>/` inherit this file by default.
- Add a narrower instruction file only when a tool has materially different
  stack, validation flow, or release process.
- When a narrower file is added, include a scope contract and avoid duplicating
  unchanged parent rules.
