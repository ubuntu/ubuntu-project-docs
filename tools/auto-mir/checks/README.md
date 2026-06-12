# Checks Module - MIR Check Evaluation Engine

This module implements the evaluation logic for all MIR (Main Inclusion Review) checks defined in `catalog.yaml`.

## Architecture

The checks module follows a **dispatcher pattern** with specialized evaluators for different check types:

```
checks/__init__.py          # Main dispatcher and language gate logic
checks/deterministic.py     # Pure logic checks (no AI)
checks/llm_eval.py          # AI-powered evaluation
```

## Evaluation Flow

1. **Check Loading**: `evaluate_checks()` reads check definitions from `catalog.yaml`
2. **Language Gate**: For language-specific checks (Go, Rust, Python), determines if the check applies
3. **Adapter Collection**: Gathers evidence from required adapters
4. **Evaluation**: Routes to appropriate evaluator based on check mode
5. **Result Mapping**: Converts evidence to Finding objects with severity/confidence

## Check Modes

Each check in `catalog.yaml` specifies an evaluation mode:

- **`deterministic`**: Pure logic, no AI involvement
  - Examples: SUM-1 (source package identified), DEP-1 (runtime deps in main)
  - Evaluator: `checks/deterministic.py`
  - Confidence: Always `high` when evidence is available

- **`ev_to_ai`**: Evidence-based AI analysis
  - Examples: RDO-1 (duplicate functionality), DEP-2 (build-time deps)
  - Evaluator: `checks/llm_eval.py::evaluate_with_evidence()`
  - Confidence: Capped at `medium` (AI-derived)

- **`ai`**: AI synthesis across multiple findings
  - Examples: SUM-5 (overall ACK/NACK decision)
  - Evaluator: `checks/llm_eval.py::evaluate_synthesis()`
  - Confidence: Capped at `medium` (AI-derived)

- **`human_only`**: Requires manual review
  - Examples: Checks requiring human judgment
  - Evaluator: Returns `unknown` status with TODO

## Language Gates

Language-specific checks (e.g., ESL-4 for Go, ESL-8 for Rust) use **language gates** to determine applicability:

```python
# checks/__init__.py
def _language_gate_active(language: str, ctx: RunContext) -> bool:
    """Check if package uses specified language"""
    if language == "go":
        return _is_go_package(ctx)
    elif language == "rust":
        return _is_rust_package(ctx)
    elif language == "python":
        return _is_python_package(ctx)
```

**Detection heuristics**:
- **Go**: `go.mod` file, Go source files, `dh-golang` in debian/rules
- **Rust**: `Cargo.toml` file, Rust source files, `dh-cargo` in debian/rules
- **Python**: `setup.py`, `pyproject.toml`, Python source files

If the gate returns `False`, the check is skipped with status `ok` and message "not applicable".

## Dispatch Mechanism

The dispatcher routes checks to evaluators:

```python
# checks/__init__.py::evaluate_checks()
for check in catalog_checks:
    mode = check.get("mode")
    
    # Language gate check
    if "language_gate" in check:
        if not _language_gate_active(check["language_gate"], ctx):
            findings.append(_not_applicable_finding(check))
            continue
    
    # Route to evaluator
    if mode == "deterministic":
        finding = deterministic.evaluate(check, ctx)
    elif mode in ("ev_to_ai", "ai"):
        finding = llm_eval.evaluate(check, ctx)
    elif mode == "human_only":
        finding = _human_only_finding(check)
    
    findings.append(finding)
```

## Deterministic Checks

Located in `checks/deterministic.py`, these checks use pure logic:

**Pattern**:
```python
def evaluate(check: dict, ctx: RunContext) -> Finding:
    """Evaluate a deterministic check"""
    check_id = check["id"]
    
    # Get required evidence
    evidence = _get_evidence(ctx, check["adapters_required"])
    
    # Apply logic
    if _check_condition(evidence):
        return Finding.ok(check, "Condition met", evidence_refs=[...])
    else:
        return Finding.not_ok(
            check,
            severity="required",
            message="Condition not met",
            todo="TODO: - Fix the issue",
            evidence_refs=[...]
        )
```

**Examples**:
- `SUM-1`: Verify source package identified from Launchpad bug
- `DEP-1`: Check all runtime dependencies are in main
- `SEC-3`: Detect webkit dependency (hard blocker)

## AI-Powered Checks

Located in `checks/llm_eval.py`, these checks use LLM analysis:

**Pattern**:
```python
def evaluate_with_evidence(check: dict, ctx: RunContext) -> Finding:
    """Evaluate using evidence + AI analysis"""
    # Collect evidence from adapters
    evidence = _gather_evidence(ctx, check["adapters_required"])
    
    # Build prompt with evidence
    prompt = _build_prompt(check, evidence)
    
    # Call LLM
    response = llm.call_llm(prompt, ctx)
    
    # Parse response
    return Finding(
        id=check["id"],
        status=response["status"],
        severity=response["severity"],
        confidence="medium",  # AI cap
        message=response["message"],
        todo=response.get("todo", ""),
        evidence_refs=response.get("evidence_refs", [])
    )
```

**Confidence cap**: AI-derived findings are capped at `medium` confidence to indicate human verification is recommended.

## Finding Object

All evaluators return a `Finding` object (defined in `models.py`):

```python
@dataclass
class Finding:
    id: str                    # Check ID (e.g., "SUM-1")
    section: str               # Template section (e.g., "Summary")
    title: str                 # Human-readable check name
    mode: str                  # Evaluation mode
    status: str                # "ok" | "not-ok" | "unknown"
    severity: str              # "ok" | "recommended" | "required" | "nack"
    confidence: str            # "low" | "medium" | "high"
    message: str               # Reviewer-facing statement
    todo: str                  # TODO item (empty if resolved)
    evidence_refs: list[str]   # Adapters consulted
    risk_flags: list[str]      # AI-identified risks
    human_confirmation_required: bool
    adapter_error_cause: list[str]
```

**Invariant**: When `status == "ok"`, `severity` must also be `"ok"`.

## Adapter Dependencies

Checks declare adapter dependencies in `catalog.yaml`:

```yaml
- id: DEP-1
  adapters_required:
    - dep-analysis      # Must succeed
  adapters_optional:
    - lp-package-api    # Enhances but not required
```

**Required adapters**: If any fail, the check returns `unknown` status with `adapter_error_cause` populated.

**Optional adapters**: Failures are logged but don't block evaluation.

## Error Handling

**Adapter failures**:
```python
if adapter_failed:
    return Finding(
        status="unknown",
        severity="ok",
        confidence="low",
        message="Could not evaluate: adapter X failed",
        todo="TODO: - Manually verify...",
        adapter_error_cause=["adapter-x"]
    )
```

**LLM failures**:
```python
try:
    response = llm.call_llm(prompt, ctx)
except LLMError:
    return Finding(
        status="unknown",
        severity="ok",
        confidence="low",
        message="AI evaluation unavailable",
        todo="TODO: - Manual review required"
    )
```

## Testing

Unit tests in `tests/test_checks.py` cover:
- Deterministic check logic
- Language gate detection
- Adapter failure handling
- Finding object creation

Run tests:
```bash
cd tools/auto-mir
python3 -m pytest tests/test_checks.py -v
```

## Adding New Checks

1. **Define in catalog.yaml**:
   ```yaml
   - id: NEW-1
     section: Security
     title: New security check
     mode: deterministic
     adapters_required:
       - packaging-source
     blocker_class: hard
   ```

2. **Implement evaluator** in `checks/deterministic.py`:
   ```python
   def _check_new_1(check: dict, ctx: RunContext) -> Finding:
       evidence = ctx.evidence.get("adapters", {}).get("packaging-source", {})
       # ... evaluation logic ...
       return Finding.ok(check, "Check passed")
   ```

3. **Register in dispatcher**:
   ```python
   DETERMINISTIC_CHECKS = {
       "SUM-1": _check_sum_1,
       "NEW-1": _check_new_1,  # Add here
   }
   ```

4. **Add tests** in `tests/test_checks.py`

## Key Files

- `checks/__init__.py`: Dispatcher, language gates, `evaluate_checks()`
- `checks/deterministic.py`: Pure logic evaluators
- `checks/llm_eval.py`: AI-powered evaluators
- `models.py`: `Finding` dataclass definition
- `catalog.yaml`: Check definitions and metadata
