"""Unit tests for review-type detection and softening (review_type + checks)."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import review_type
from checks import _apply_review_type_softening
from models import Finding


def _ctx(**kwargs):
    base = {
        "review_type_arg": "auto",
        "reporter_mir_content": "",
        "bug": {},
        "source_package": "libfoo",
        "evidence": {"adapters": {}},
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


# ---------------------------------------------------------------------------
# Forced --review-type overrides
# ---------------------------------------------------------------------------


def test_forced_review_type_short_circuits_detection():
    for forced in ("fresh", "rereview", "reorg"):
        ctx = _ctx(review_type_arg=forced, reporter_mir_content="please re-review")
        decision = review_type.detect_review_type(ctx)
        assert decision.review_type == forced
        assert decision.forced is True
        assert forced in decision.rationale


def test_forced_invalid_value_falls_back_to_auto_detection():
    # An unexpected value is treated as auto (heuristics run).
    ctx = _ctx(review_type_arg="bogus")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH
    assert decision.forced is False


# ---------------------------------------------------------------------------
# Auto detection — rereview
# ---------------------------------------------------------------------------


def test_reporter_text_requests_rereview():
    ctx = _ctx(reporter_mir_content="This is a voluntary re-review of the package.")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REREVIEW
    assert not decision.forced


def test_all_binaries_already_in_main_signals_rereview():
    ctx = _ctx(
        evidence={
            "adapters": {
                "dep-analysis": {"binary_packages": ["libfoo1", "libfoo-dev"]},
                "component-mismatches": {"promotion_candidates": []},
            }
        }
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REREVIEW
    assert "already in main" in decision.rationale


def test_mirror_word_does_not_trigger_rereview():
    # 'mirror' must not match the \bmir\b / re-review patterns.
    ctx = _ctx(reporter_mir_content="The package sets up a mirror of upstream data.")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH


# ---------------------------------------------------------------------------
# Auto detection — reorg
# ---------------------------------------------------------------------------


def test_reporter_text_mentions_rename_signals_reorg():
    ctx = _ctx(reporter_mir_content="libfoo was renamed from libfoo-old this cycle.")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG


def test_prior_mir_under_other_name_signals_reorg():
    ctx = _ctx(
        source_package="libfoo2",
        evidence={
            "adapters": {
                "lp-mir-history": {
                    "prior_mir_bugs": [
                        {
                            "id": "111",
                            "title": "[MIR] libfoo",
                            "matched_name": "libfoo",
                            "web_link": "https://bugs.launchpad.net/bugs/111",
                        }
                    ]
                }
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG
    assert "different source name" in decision.rationale


def test_reorg_takes_precedence_over_rereview():
    # Both signal sets present: reorg (more specific) wins.
    ctx = _ctx(
        reporter_mir_content="This renamed source is up for a re-review.",
        evidence={
            "adapters": {
                "dep-analysis": {"binary_packages": ["libfoo1"]},
                "component-mismatches": {"promotion_candidates": []},
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG


# ---------------------------------------------------------------------------
# Fresh (default)
# ---------------------------------------------------------------------------


def test_no_signals_is_fresh():
    ctx = _ctx(reporter_mir_content="A brand new library for Ubuntu main.")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH
    assert decision.signals == []


# ---------------------------------------------------------------------------
# Softening pass
# ---------------------------------------------------------------------------


def _finding(fid, section, severity):
    return Finding(
        id=fid,
        section=section,
        title="t",
        mode="deterministic",
        status="not-ok",
        severity=severity,
        confidence="high",
        message="m",
        todo="TODO: - x",
        evidence_refs=[],
    )


def test_softening_downgrades_required_and_nack_but_not_summary():
    findings = [
        _finding("CB-2", "Common blockers", "required"),
        _finding("DEP-4", "Dependencies", "nack"),
        _finding("PRF-2", "Packaging red flags", "recommended"),
        _finding("SUM-5", "Summary", "required"),
    ]
    decision = review_type.ReviewTypeDecision(review_type=review_type.REREVIEW)
    _apply_review_type_softening(findings, decision)

    by_id = {f.id: f for f in findings}
    assert by_id["CB-2"].severity == "recommended"
    assert by_id["DEP-4"].severity == "recommended"
    assert by_id["PRF-2"].severity == "recommended"
    # Summary decision checks are never softened.
    assert by_id["SUM-5"].severity == "required"


def test_softening_is_a_noop_for_fresh():
    findings = [_finding("CB-2", "Common blockers", "required")]
    decision = review_type.ReviewTypeDecision(review_type=review_type.FRESH)
    _apply_review_type_softening(findings, decision)
    assert findings[0].severity == "required"
