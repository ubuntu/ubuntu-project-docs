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
                "lp-package-api": {"current_component": "main"},
            }
        }
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REREVIEW
    assert "already in main" in decision.rationale


def test_universe_component_does_not_signal_rereview():
    # Regression for the prompt-toolkit MIR bug: component-mismatches reporting
    # zero promotion candidates does NOT mean "already in main" — it is equally
    # produced when a package correctly sits in universe with no main-seed
    # expectation. current_component is the sole source of truth now.
    ctx = _ctx(
        evidence={
            "adapters": {
                "dep-analysis": {"binary_packages": ["python3-prompt-toolkit"]},
                "component-mismatches": {"promotion_candidates": []},
                "lp-package-api": {"current_component": "universe"},
            }
        }
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH


def test_missing_lp_package_api_does_not_signal_rereview():
    # Fail closed: no positive evidence of "already in main" means fresh, never
    # a silent fallback to the old (wrong) component-mismatches-based proxy.
    ctx = _ctx(
        evidence={
            "adapters": {
                "dep-analysis": {"binary_packages": ["libfoo1"]},
                "component-mismatches": {"promotion_candidates": []},
            }
        }
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH


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


def test_reporter_text_replace_signals_reorg():
    ctx = _ctx(reporter_mir_content="mysql-9.7 to replace mysql-8.4 as the provider")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG


def test_replacement_word_does_not_signal_reorg():
    # "replacement" as a noun must not trigger the verb pattern.
    ctx = _ctx(reporter_mir_content="This package is a replacement for the old one.")
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH


def test_reorg_signal_in_comment_detected():
    # Text signals must scan comments, not just reporter content / title / desc.
    ctx = _ctx(
        bug={
            "title": "MIR for testpkg",
            "description": "clean",
            "comments": ["The source was renamed from testpkg-old."],
        }
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG


def test_prior_mir_under_retired_name_signals_reorg():
    """A prior MIR for a name that is GONE from the archive is rename
    evidence: the lp-mir-history adapter verified it as not still published."""
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
                            "still_published": False,
                            "web_link": "https://bugs.launchpad.net/bugs/111",
                        }
                    ]
                }
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG
    assert "no longer published" in decision.rationale


def test_prior_mir_under_still_published_name_is_a_sibling_not_a_reorg():
    """Exact regression shape from the rust-sequoia-sq user test: a MIR for
    the sibling tool rust-sequoia-sqv was found while probing gnupg2 (the LP
    project it was filed under), and the old matched-name logic turned that
    into 'reorg', wrongly softening every finding of a fresh MIR. A matched
    name that is still published is a sibling, not a rename."""
    ctx = _ctx(
        source_package="rust-sequoia-sq",
        evidence={
            "adapters": {
                "lp-mir-history": {
                    "prior_mir_bugs": [
                        {
                            "id": "2089690",
                            "title": "[MIR] rust-sequoia-sqv",
                            "matched_name": "gnupg2",
                            "still_published": True,
                            "web_link": "https://bugs.launchpad.net/ubuntu/+source/gnupg2/+bug/2089690",
                        }
                    ]
                }
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH


def test_prior_mir_without_verification_never_signals_reorg():
    """Fails safe: an unverified matched name (adapter could not check it) is
    not rename evidence either."""
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
    assert decision.review_type == review_type.FRESH


def test_dup_search_main_candidates_do_not_signal_reorg():
    # dup-search is a low-precision suggestion pool whose proper consumer is the
    # RDO-1 check. Raw main-component candidates must NOT drive reorg detection,
    # which previously produced contradictory output (RDO-1 ok vs a
    # "functionally-similar in main" rationale naming unrelated category
    # neighbours such as libdbi-perl / libecpg-compat3 for mysql-9.7).
    ctx = _ctx(
        source_package="mysql-9.7",
        reporter_mir_content="A brand new database package with no prior name.",
        evidence={
            "adapters": {
                "dup-search": {
                    "candidates": [
                        {
                            "name": "libdbi-perl",
                            "synopsis": "Perl Database Interface (DBI)",
                            "component": "main",
                        },
                        {
                            "name": "libecpg-compat3",
                            "synopsis": "older version of run-time library for ECPG programs",
                            "component": "main",
                        },
                        {
                            "name": "libecpg-dev",
                            "synopsis": "development files for ECPG",
                            "component": "main",
                        },
                    ]
                }
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.FRESH
    assert "functionally-similar" not in decision.rationale
    assert "libdbi-perl" not in decision.rationale
    assert "libecpg" not in decision.rationale


def test_reorg_takes_precedence_over_rereview():
    # Both signal sets present: reorg (more specific) wins.
    ctx = _ctx(
        reporter_mir_content="This renamed source is up for a re-review.",
        evidence={
            "adapters": {
                "lp-package-api": {"current_component": "main"},
            }
        },
    )
    decision = review_type.detect_review_type(ctx)
    assert decision.review_type == review_type.REORG


# ---------------------------------------------------------------------------
# Pre-detection (Stage 1, text-only, used by lp_intake gate)
# ---------------------------------------------------------------------------


def test_pre_detect_forced_rereview():
    ctx = _ctx(review_type_arg="rereview", reporter_mir_content="fresh review")
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REREVIEW
    assert decision.forced is True


def test_pre_detect_forced_reorg():
    ctx = _ctx(review_type_arg="reorg")
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REORG
    assert decision.forced is True


def test_pre_detect_reorg_from_description():
    ctx = _ctx(bug={"title": "MIR for mysql-9.7", "description": "mysql-9.7 to replace mysql-8.4"})
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REORG
    assert decision.forced is False


def test_pre_detect_reorg_from_replace():
    ctx = _ctx(bug={"title": "MIR for foo", "description": "foo replaces bar as the provider"})
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REORG


def test_pre_detect_rereview_from_description():
    ctx = _ctx(bug={"title": "MIR for foo", "description": "This is a voluntary re-review."})
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REREVIEW
    assert decision.forced is False


def test_pre_detect_reorg_from_comment():
    ctx = _ctx(
        bug={
            "title": "MIR for foo",
            "description": "clean",
            "comments": ["The source was reorganized."],
        }
    )
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.REORG


def test_pre_detect_fresh_no_signals():
    ctx = _ctx(bug={"title": "MIR for foo", "description": "A brand new library."})
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.FRESH
    assert decision.signals == []


def test_pre_detect_mirror_no_false_positive():
    ctx = _ctx(reporter_mir_content="The package sets up a mirror of upstream data.")
    decision = review_type.detect_review_type(ctx, use_evidence=False)
    assert decision.review_type == review_type.FRESH


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
