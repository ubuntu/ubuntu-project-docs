# Render Module - MIR Review Draft Generator

This module generates the final MIR review draft document from evaluated findings.

## Architecture

The render module transforms structured findings into a human-readable review template:

```
render/__init__.py    # Main rendering logic and template generation
```

## Rendering Pipeline

The rendering process follows these stages:

1. **Section Grouping**: Group findings by template section (Summary, Dependencies, Security, etc.)
2. **Severity Sorting**: Within each section, sort by severity (required → recommended → ok)
3. **Confidence Filtering**: Separate high-confidence from low/medium-confidence findings
4. **Template Population**: Fill template sections with formatted findings
5. **Summary Generation**: Create executive summary with overall recommendation
6. **Linting**: Validate output structure and formatting

## Output Structure

The review draft follows the MIR reviewer template structure:

```
[Summary]
OK:
- Source package identified: package-name
- Reporter MIR content present

Required TODOs:
- TODO: - Address security concern X

Recommended TODOs:
- TODO: - Consider adding autopkgtest

[Dependencies]
OK:
- All runtime dependencies in main
- No build-time dependencies with active code

Problems:
- webkit dependency found (hard blocker)

[Security]
OK:
- No known CVEs
- No setuid/setgid binaries

Left to decide:
- TODO: - Verify upstream security posture (medium confidence)
```

## Section Rendering

Each section is rendered with three subsections:

### OK Subsection
Lists resolved checks with high confidence:
```python
def _render_ok_findings(findings: list[Finding]) -> list[str]:
    """Render OK subsection"""
    lines = ["OK:"]
    for finding in findings:
        if finding.status == "ok" and finding.confidence == "high":
            lines.append(f"- {finding.message}")
    return lines
```

### Problems Subsection
Lists high-confidence failures (deterministic or high-confidence AI):
```python
def _render_problems(findings: list[Finding]) -> list[str]:
    """Render Problems subsection"""
    lines = ["Problems:"]
    for finding in findings:
        if finding.status != "ok":
            if finding.confidence == "high" or finding.mode == "deterministic":
                lines.append(f"- {finding.message}")
    return lines
```

### Left to Decide Subsection
Lists low/medium-confidence findings requiring human judgment:
```python
def _render_undecided(findings: list[Finding]) -> list[str]:
    """Render Left to decide subsection"""
    lines = ["Left to decide:"]
    for finding in findings:
        if finding.status != "ok":
            if finding.confidence in ("low", "medium"):
                lines.append(f"- {finding.todo}")
    return lines
```

## Summary Section

The Summary section is rendered specially with ACK/NACK recommendation:

```python
def _render_summary(findings: list[Finding]) -> list[str]:
    """Render Summary section with overall recommendation"""
    lines = ["[Summary]"]
    
    # Determine overall recommendation
    has_required = any(f.severity == "required" for f in findings)
    has_nack = any(f.severity == "nack" for f in findings)
    
    if has_nack:
        lines.append("TODO-B: MIR team NACK")
    elif has_required:
        lines.append("TODO-C: MIR team ACK under constraint to resolve required TODOs")
    else:
        lines.append("TODO-A: MIR team ACK")
    
    # Add OK findings
    lines.append("OK:")
    for finding in findings:
        if finding.section == "Summary" and finding.status == "ok":
            lines.append(f"- {finding.message}")
    
    return lines
```

## Required/Recommended TODOs

The renderer aggregates TODOs by severity:

```python
def _render_required_todos(findings: list[Finding]) -> list[str]:
    """Render Required TODOs section"""
    lines = ["Required TODOs:"]
    for finding in findings:
        if finding.severity == "required" and finding.todo:
            lines.append(f"- {finding.todo}")
    return lines

def _render_recommended_todos(findings: list[Finding]) -> list[str]:
    """Render Recommended TODOs section"""
    lines = ["Recommended TODOs:"]
    for finding in findings:
        if finding.severity == "recommended" and finding.todo:
            lines.append(f"- {finding.todo}")
    return lines
```

## Linting Rules

The renderer enforces structural correctness:

```python
def _lint_review_draft(draft: str, findings: list[Finding]) -> None:
    """Validate review draft structure"""
    
    # Rule 1: No RULE: lines in output
    if "RULE:" in draft:
        raise ValueError("Draft contains RULE: lines")
    
    # Rule 2: TODO lines must start with "TODO:" or "TODO-"
    for line in draft.split("\n"):
        if line.strip().startswith("TODO"):
            if not (line.startswith("TODO:") or line.startswith("TODO-")):
                raise ValueError(f"Invalid TODO format: {line}")
    
    # Rule 3: Problems section cannot contain TODO lines
    in_problems = False
    for line in draft.split("\n"):
        if line.strip() == "Problems:":
            in_problems = True
        elif line.startswith("["):
            in_problems = False
        elif in_problems and line.strip().startswith("TODO"):
            raise ValueError("TODO found in Problems section")
    
    # Rule 4: OK findings cannot have TODO
    for finding in findings:
        if finding.status == "ok" and finding.todo:
            raise ValueError(f"OK finding {finding.id} has TODO")
```

## Main Entry Point

`write_outputs()` orchestrates the rendering process:

```python
def write_outputs(ctx: RunContext) -> None:
    """Generate review draft and structured report"""
    
    # 1. Build review draft
    draft = _build_review_draft(ctx.findings, ctx.catalog)
    
    # 2. Lint the draft
    _lint_review_draft(draft, ctx.findings)
    
    # 3. Write review draft
    draft_path = ctx.output_dir / "review-draft.txt"
    draft_path.write_text(draft)
    
    # 4. Build structured report (JSON)
    report = _build_structured_report(ctx)
    report_path = ctx.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2))
    
    ctx.review_draft_path = draft_path
    ctx.report_path = report_path
```

## Structured Report

In addition to the human-readable draft, the renderer produces a JSON report:

```python
def _build_structured_report(ctx: RunContext) -> dict:
    """Build structured JSON report"""
    return {
        "bug_id": ctx.bug_id,
        "source_package": ctx.source_package,
        "series": ctx.series,
        "timestamp": datetime.now().isoformat(),
        "findings": [
            {
                "id": f.id,
                "section": f.section,
                "status": f.status,
                "severity": f.severity,
                "confidence": f.confidence,
                "message": f.message,
                "todo": f.todo,
                "evidence_refs": f.evidence_refs,
            }
            for f in ctx.findings
        ],
        "summary": {
            "total_checks": len(ctx.findings),
            "ok_count": sum(1 for f in ctx.findings if f.status == "ok"),
            "required_count": sum(1 for f in ctx.findings if f.severity == "required"),
            "recommended_count": sum(1 for f in ctx.findings if f.severity == "recommended"),
        }
    }
```

## Section Order

Sections are rendered in canonical order defined by the template:

```python
SECTION_ORDER = [
    "Summary",
    "Rationale, Duplication and Ownership",
    "Dependencies",
    "Embedded sources and static linking",
    "Security",
    "Common blockers",
    "Packaging red flags",
    "Upstream red flags",
]
```

This order matches the MIR reviewer template structure.

## Testing

Unit tests in `tests/test_render.py` cover:
- Section rendering logic
- TODO formatting
- Linting rules
- Summary generation
- Structured report output

Run tests:
```bash
cd tools/auto-mir
python3 -m pytest tests/test_render.py -v
```

## Output Files

The renderer produces two output files:

### review-draft.txt
Human-readable review draft ready to post on Launchpad:
- Follows MIR reviewer template structure
- Contains OK/Problems/Left to decide subsections
- Includes Required/Recommended TODOs
- Suitable for copy-paste to bug comment

### report.json
Machine-readable structured report:
- Complete finding details
- Evidence references
- Metadata (bug ID, package, series, timestamp)
- Summary statistics
- Suitable for programmatic analysis

## Customization

The renderer can be customized via:
- **Section order**: Modify `SECTION_ORDER` list
- **Linting rules**: Add/remove rules in `_lint_review_draft()`
- **Summary logic**: Adjust ACK/NACK criteria in `_render_summary()`
- **TODO formatting**: Modify `_render_required_todos()` and `_render_recommended_todos()`

## Key Files

- `render/__init__.py`: All rendering logic, linting, and output generation
- `models.py`: `Finding` dataclass used as input
- `catalog.yaml`: Defines section order and check metadata
