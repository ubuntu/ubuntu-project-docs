"""Byte-for-byte guards for the generated human template include files.

The two golden fixtures hold the template content users historically saw
(the reviewer golden additionally carries the Maintainer-field rule and
TODO line the user explicitly approved as an intentional addition).
Generation must keep reproducing them exactly; any diff here means the
catalog or render logic unintentionally changed human-visible template
text.

If a change to these files is intentional, regenerate the goldens in the
same commit (the failure output names both fixtures) and state the intent
in the commit message.
"""

import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402
import render_template  # noqa: E402


def _render_reporter() -> str:
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    return render_template.render_template(data, "report")


def _render_reviewer() -> str:
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")
    return render_template.render_template(data, "review")


def test_reporter_include_matches_golden():
    assert _render_reporter() == (FIXTURES / "include_reporters.golden").read_text(encoding="utf-8")


def test_reviewer_include_matches_golden():
    assert _render_reviewer() == (FIXTURES / "include_reviewers.golden").read_text(encoding="utf-8")
