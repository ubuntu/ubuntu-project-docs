"""Regression tests using saved test artifacts from real MIR bugs.

These tests replay deterministic evidence through the check evaluators
and compare findings against known-good baselines.

Artifacts are stored in: tools/auto-mir/tests/fixtures/<bug_id>/

To create or update artifacts:
    ./tools/auto-mir/auto_mir.py <bug_id> --collect-only \
      --output-dir tools/auto-mir/tests/fixtures/<bug_id>
"""

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import catalog
import checks

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_auto_mir_help_runs():
    """Verify auto_mir.py --help executes without syntax errors."""
    script = Path(__file__).parent.parent / "auto_mir.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"auto_mir.py --help failed:\n{result.stderr}"
    assert "usage:" in result.stdout.lower() or "auto_mir.py" in result.stdout


class ReplayContext:
    """Lightweight context object for replaying saved artifacts."""

    def __init__(self, context_data: dict, evidence_data: dict, catalog_data: dict):
        self.bug_id = context_data["bug_id"]
        self.source_package = context_data["source_package"]
        self.series = context_data["series"]
        self.reporter_mir_content = context_data["reporter_mir_content"]
        self.bug = context_data["bug"]
        self.evidence = evidence_data
        self.catalog = catalog_data


def load_fixture(bug_id: str) -> tuple[ReplayContext, list[dict]]:
    """Load fixture files for a given bug ID."""
    fixture_dir = FIXTURES_DIR / bug_id

    with (fixture_dir / "context.json").open() as f:
        context_data = json.load(f)

    with (fixture_dir / "evidence.json").open() as f:
        evidence_data = json.load(f)

    with (fixture_dir / "deterministic_findings.json").open() as f:
        expected_findings = json.load(f)

    tool_root = Path(__file__).parent.parent
    workspace_root = tool_root.parent.parent
    catalog_data = catalog.load_catalog_for_role(tool_root, workspace_root, "review")

    catalog_data = {
        "checks": [c for c in catalog_data.get("checks", []) if c.get("mode") == "deterministic"]
    }

    ctx = ReplayContext(context_data, evidence_data, catalog_data)
    return ctx, expected_findings


def get_fixture_bug_ids() -> list[str]:
    """Discover available fixture bug IDs."""
    if not FIXTURES_DIR.exists():
        return []
    return sorted([d.name for d in FIXTURES_DIR.iterdir() if d.is_dir()])


@pytest.mark.skipif(not get_fixture_bug_ids(), reason="No test fixtures available")
@pytest.mark.parametrize("bug_id", get_fixture_bug_ids())
def test_deterministic_checks_regression(bug_id: str):
    """Replay saved artifacts and verify deterministic check findings match."""
    ctx, expected_findings = load_fixture(bug_id)

    actual_findings = checks.evaluate_checks(ctx)

    actual_data = [asdict(f) for f in actual_findings]

    assert len(actual_data) == len(expected_findings), (
        f"Finding count mismatch for bug {bug_id}: "
        f"{len(actual_data)} actual vs {len(expected_findings)} expected"
    )

    for i, (actual, expected) in enumerate(zip(actual_data, expected_findings)):
        for field in ["id", "status", "severity", "confidence", "message", "todo", "evidence_refs"]:
            assert actual[field] == expected[field], (
                f"Bug {bug_id}, finding {i} ({actual['id']}) field '{field}' mismatch:\n"
                f"  actual:   {actual[field]}\n"
                f"  expected: {expected[field]}"
            )
