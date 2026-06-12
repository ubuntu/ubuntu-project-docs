# Phase Recap — Reacting to Design Rewrite (c391e1401a30)

Tracks work needed after the high-level design rewrite in commit c391e1401a30.
Work is sequenced: agentic markdown files first, code changes second.

---

## Part 1 — Markdown / Agentic Document Updates

### 1.1 `tasks_phase10.md` — Remove Mermaid diagram requirement

**Why**: Design phase 9 was simplified from "README with Mermaid diagram + concise
usage intent with `--help` as reference" to simply "put the user documentation
into `tools/auto-mir/README.md`". The Mermaid diagram and `--help` reference are
no longer mandated.

**Change**: Remove the `Mermaid architecture diagram` bullet and `--help` reference
from the deliverables list. Update the exit criteria and phrasing to match the
simplified goal: README covers the full pipeline in a form useful to users.

### 1.2 `tasks_phase8.md` — Align terminology with design

**Why**: Design phase 8 bullet changed "corpus" to "cases"
(Phase 8C: "Validation against recent cases...").

**Change**: Replace "corpus" with "cases" throughout `tasks_phase8.md` to keep
language consistent with `design.md`.

### 1.3 `testing.md` — Update container image failure note

**Why**: The design now says the container runs on "the target Ubuntu release"
rather than the Ubuntu devel image. The failure table has
`Ensure lxc works and devel image exists`, which no longer accurately reflects
the intent.

**Change**: Update the failure-mode table row for "Smoke test container fail" to
reflect that the required image is the target release image (or devel as fallback
when the series is unresolved), not exclusively the devel image.

---

## Part 2 — Code Updates

### 2.1 `lxd_runner.py` — Use target-series image when series is known

**Why**: Design now reads: "provisions tooling, executes the pipeline in a LXD
container of the target Ubuntu release for reproducibility." The module currently
always tries a fixed list of Ubuntu devel aliases (`ubuntu-daily:devel`,
`images:ubuntu/devel`, `ubuntu:devel`) regardless of the target series.

**Change**:
- Update module docstring: replace "Ubuntu devel images" with "the target Ubuntu
  release image (falling back to Ubuntu devel when the series is unknown)".
- Extend `resolve_image_alias()` so that when a target series is known it probes
  series-specific aliases first (`ubuntu-daily:SERIES`, `ubuntu:SERIES`) before
  falling back to the existing devel list.
- Update constant name / comments: `_UBUNTU_DEVEL_IMAGES` →
  `_UBUNTU_DEVEL_FALLBACK_IMAGES` and update surrounding comments accordingly.
- Update `create_container()` docstring to say "target Ubuntu release" rather than
  "Ubuntu devel".

### 2.2 `auto_mir.py` — Fix help text and inline comments

**Why**: The module docstring still says the `--lxd-image` default is "Ubuntu
devel" and an inline comment says "Create new container from Ubuntu devel image
alias". Both contradict the updated design intent.

**Change**:
- `--lxd-image` help line: change "(default: Ubuntu devel)" to
  "(default: target release image, falling back to Ubuntu devel)".
- Inline orchestration comment at the `create_container` call: update
  "Create new container from Ubuntu devel image alias" to "Create new container
  from target Ubuntu release image (or devel fallback)".

### 2.3 `render/__init__.py` — Implement three-tier output model

**Why**: The new design defines a three-tier output model:
1. **Unresolvable / missing evidence** → stays as `TODO` under `Left to decide:`.
2. **Low-confidence AI result** → suggestion with `TODO` note under `Left to decide:`.
3. **Deterministic or high-confidence** → answered and grouped under `OK:` (pass)
   or `Problems:` (fail).

Currently `_render_section()` only has `OK:` (status == "ok") and
`Left to decide:` (everything else). High-confidence failures are folded into
"Left to decide" together with genuinely unresolvable items, which obscures clear
problems.

**Change**:
- Add a `Problems:` sub-block between `OK:` and `Left to decide:`.
- Route findings with `status != "ok"` **and** `confidence == "high"` (or mode
  `"deterministic"`) into `Problems:` with their `message` (not as a TODO line).
- Route findings with `status != "ok"` **and** `confidence in ("low", "medium")`
  or unresolvable evidence into `Left to decide:` as before.
- Update `_lint_review_draft()` to accept `Problems:` as a valid sub-block header
  and not require its content lines to start with `TODO:`.
- Update the module docstring to document the three-tier structure.

### 2.4 `checks.py` — Align module docstring with new output model

**Why**: The `evaluate_checks()` docstring still documents the old two-state
framing (`ok` / `not-ok`). The new design's three-tier model (TODO / suggestion /
answered) is expressed through the existing `confidence` field but the docstring
does not explain how confidence maps to render tiers.

**Change**: Extend the `evaluate_checks()` docstring to state that
`confidence: high` (or mode `deterministic`) findings that are not-ok will be
rendered under `Problems:` in the output, whereas low/medium-confidence findings
remain under `Left to decide:`.

---

## Sequencing Notes

- Do all Part 1 tasks before Part 2.
- Within Part 2: do 2.1 (lxd_runner) before 2.2 (auto_mir) so the function
  signatures are consistent when updating the call-site comments.
- 2.3 (render) and 2.4 (checks docstring) can be done in parallel but 2.3
  should be done first since it is the larger change.
- After all changes: run `make -C tools/` to verify format + lint + template
  consistency still pass.
