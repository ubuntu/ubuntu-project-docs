"""Unit tests for lp_intake detection helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lp_intake


# ---------------------------------------------------------------------------
# Reporter template detection
# ---------------------------------------------------------------------------


def _reporter_block() -> str:
    return "\n".join(
        [
            "[Availability]",
            "Package is available in Debian unstable.",
            "[Rationale]",
            "We need this for our product.",
            "[Security]",
            "No known issues.",
            "[Quality assurance: Testing]",
            "There is a test suite.",
            "[Maintenance]",
            "We will maintain it.",
        ]
    )


def test_detect_reporter_mir_content_positive():
    assert lp_intake._detect_reporter_mir_content(_reporter_block()) is True


def test_detect_reporter_mir_content_negative_empty():
    assert lp_intake._detect_reporter_mir_content("") is False


def test_detect_reporter_mir_content_negative_partial():
    # Only 2 markers — below the threshold of 3
    text = "[Availability]\nsome text\n[Rationale]\nmore text"
    assert lp_intake._detect_reporter_mir_content(text) is False


def test_find_reporter_mir_content_in_description():
    result = lp_intake._find_reporter_mir_content(_reporter_block(), [])
    assert result == _reporter_block()


def test_find_reporter_mir_content_in_comment():
    result = lp_intake._find_reporter_mir_content("Just a bug report.", [_reporter_block()])
    assert result == _reporter_block()


def test_find_reporter_mir_content_not_found():
    result = lp_intake._find_reporter_mir_content("nothing", ["also nothing"])
    assert result is None


# ---------------------------------------------------------------------------
# Reviewer template (prior review) detection
# ---------------------------------------------------------------------------


def _reviewer_block() -> str:
    return "\n".join(
        [
            "Required TODOs:",
            "- TODO: - Fix the thing",
            "Recommended TODOs:",
            "- TODO: - Consider the other thing",
            "Left to decide:",
            "TODO: - Review the policy",
            "[Rationale, Duplication and Ownership]",
            "OK:",
            "- package is unique",
            "[Embedded sources and static linking]",
            "OK:",
            "- no embedded sources",
        ]
    )


def test_detect_reviewer_mir_content_positive():
    assert lp_intake._detect_reviewer_mir_content(_reviewer_block()) is True


def test_detect_reviewer_mir_content_negative_empty():
    assert lp_intake._detect_reviewer_mir_content("") is False


def test_detect_reviewer_mir_content_negative_reporter_content():
    # Reporter content should NOT trigger reviewer detection
    assert lp_intake._detect_reviewer_mir_content(_reporter_block()) is False


def test_find_prior_reviews_detects_reviewer_comment():
    comments = ["Just a comment.", _reviewer_block(), "Another comment."]
    indices = lp_intake._find_prior_reviews(comments)
    assert indices == [2]  # 1-based: second comment


def test_find_prior_reviews_no_prior():
    comments = ["Just a comment.", _reporter_block()]
    assert lp_intake._find_prior_reviews(comments) == []


def test_find_prior_reviews_multiple():
    comments = [_reviewer_block(), "some text", _reviewer_block()]
    indices = lp_intake._find_prior_reviews(comments)
    assert indices == [1, 3]
