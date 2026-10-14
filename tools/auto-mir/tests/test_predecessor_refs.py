"""Unit tests for utils.predecessor_refs (bug-text predecessor extraction)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import predecessor_refs
from utils.predecessor_refs import PredecessorRef

# ---------------------------------------------------------------------------
# replace / supersedes / renamed phrases (name only)
# ---------------------------------------------------------------------------


def test_replace_phrase_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "mysql-9.7 to replace mysql-8.4 as the provider", "mysql-9.7"
    )
    names = [r.name for r in refs if r.name]
    assert "mysql-8.4" in names
    assert "mysql-9.7" not in names  # current source never a predecessor


def test_replaces_phrase_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "mysql-9.7 replaces mysql-8.4 in devel.", "mysql-9.7"
    )
    assert any(r.name == "mysql-8.4" for r in refs)


def test_replaced_phrase_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "The new source replaced mysql-8.4 this cycle.", "mysql-9.7"
    )
    assert any(r.name == "mysql-8.4" for r in refs)


def test_replacement_noun_does_not_extract():
    # "replacement" as a noun must not produce a spurious name.
    refs = predecessor_refs.extract_predecessor_refs(
        "This package is a replacement for the old one.", "libfoo"
    )
    # "old" is a stopword and "one" is a stopword, so no name refs.
    assert all(r.name is None for r in refs)


def test_renamed_from_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "libfoo2 was renamed from libfoo this cycle.", "libfoo2"
    )
    assert any(r.name == "libfoo" for r in refs)


def test_formerly_known_as_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "bar, formerly known as foo, is up for review.", "bar"
    )
    assert any(r.name == "foo" for r in refs)


def test_supersedes_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs("mysql-9.7 supersedes mysql-8.4.", "mysql-9.7")
    assert any(r.name == "mysql-8.4" for r in refs)


def test_was_previously_extracts_name():
    refs = predecessor_refs.extract_predecessor_refs(
        "This source was previously libfoo-old.", "libfoo"
    )
    assert any(r.name == "libfoo-old" for r in refs)


def test_was_previously_called_uses_formerly_pattern_not_bare_name():
    # "was previously called foo" must not capture "called" as a predecessor
    # name; it should be handled by the formerly/called pattern instead.
    refs = predecessor_refs.extract_predecessor_refs(
        "This source was previously called libfoo-old.", "libfoo"
    )
    names = [r.name for r in refs if r.name]
    assert "libfoo-old" in names
    assert "called" not in names


# ---------------------------------------------------------------------------
# Bug-id references
# ---------------------------------------------------------------------------


def test_lp_hash_extracts_bug_id():
    refs = predecessor_refs.extract_predecessor_refs(
        "MIR for mysql-8.4 - LP: #2089720", "mysql-9.7"
    )
    ids = [r.bug_id for r in refs if r.bug_id]
    assert "2089720" in ids


def test_lp_hash_no_space_extracts_bug_id():
    refs = predecessor_refs.extract_predecessor_refs(
        "See LP#2089720 for the prior review.", "mysql-9.7"
    )
    assert any(r.bug_id == "2089720" for r in refs)


def test_lp_url_extracts_bug_id():
    refs = predecessor_refs.extract_predecessor_refs(
        "Prior: https://bugs.launchpad.net/ubuntu/+source/mysql-8.4/+bug/2089720",
        "mysql-9.7",
    )
    assert any(r.bug_id == "2089720" for r in refs)


def test_short_number_not_extracted_as_bug_id():
    # Numbers with fewer than 6 digits are not Launchpad bug ids.
    refs = predecessor_refs.extract_predecessor_refs("See LP: #123 for context.", "libfoo")
    assert all(r.bug_id is None for r in refs)


# ---------------------------------------------------------------------------
# Paired name + bug id (single span)
# ---------------------------------------------------------------------------


def test_mir_for_name_with_lp_hash_pairs_name_and_bug_id():
    refs = predecessor_refs.extract_predecessor_refs(
        "MIR for mysql-8.4 - LP: #2089720", "mysql-9.7"
    )
    paired = [r for r in refs if r.name and r.bug_id]
    assert len(paired) == 1
    assert paired[0].name == "mysql-8.4"
    assert paired[0].bug_id == "2089720"


def test_mir_title_with_lp_hash_pairs_name_and_bug_id():
    refs = predecessor_refs.extract_predecessor_refs(
        "Prior review [MIR] mysql-8.4 tracked as LP: #2089720.", "mysql-9.7"
    )
    paired = [r for r in refs if r.name and r.bug_id]
    assert len(paired) == 1
    assert paired[0].name == "mysql-8.4"


# ---------------------------------------------------------------------------
# Validation / stopwords / current-source exclusion
# ---------------------------------------------------------------------------


def test_stopword_token_not_extracted():
    refs = predecessor_refs.extract_predecessor_refs("This package replaces the old one.", "libfoo")
    assert all(r.name is None for r in refs)


def test_replaces_pronoun_them_not_extracted():
    # Real-world false positive (bug 2161382): rationale prose referring back to
    # an earlier plural noun ("GNU Readline and pyreadline3") via "them" must not
    # be misread as a literal predecessor package named "them".
    refs = predecessor_refs.extract_predecessor_refs(
        "cmd2 used to depend on GNU Readline and pyreadline3; prompt-toolkit "
        "replaces them with a single cross-platform implementation.",
        "prompt-toolkit",
    )
    assert all(r.name != "them" for r in refs)


def test_replaces_other_pronouns_and_determiners_not_extracted():
    for pronoun in (
        "they",
        "these",
        "those",
        "us",
        "we",
        "some",
        "others",
        "all",
        "both",
        "either",
        "neither",
        "more",
        "most",
        "several",
        "many",
    ):
        refs = predecessor_refs.extract_predecessor_refs(
            f"prompt-toolkit replaces {pronoun} in this release.", "prompt-toolkit"
        )
        assert all(r.name != pronoun for r in refs), f"{pronoun!r} was extracted as a name"


def test_replaces_real_predecessor_name_still_extracted_alongside_pronoun_fix():
    # Guard against over-filtering: a genuine rename must still be detected.
    refs = predecessor_refs.extract_predecessor_refs(
        "mysql-9.7 replaces mysql-8.4 in devel.", "mysql-9.7"
    )
    assert any(r.name == "mysql-8.4" for r in refs)


def test_current_source_never_a_predecessor():
    refs = predecessor_refs.extract_predecessor_refs(
        "mysql-9.7 replaces mysql-9.7 (same package).", "mysql-9.7"
    )
    assert all(r.name is None for r in refs)


def test_invalid_name_token_not_extracted():
    # A token that is not a valid Debian source name is rejected.
    refs = predecessor_refs.extract_predecessor_refs("foo replaces !!! as the provider.", "foo")
    assert all(r.name is None for r in refs)


# ---------------------------------------------------------------------------
# Deduplication and helpers
# ---------------------------------------------------------------------------


def test_duplicate_refs_deduplicated():
    text = "MIR for mysql-8.4 - LP: #2089720. Also see MIR for mysql-8.4 again."
    refs = predecessor_refs.extract_predecessor_refs(text, "mysql-9.7")
    paired = [r for r in refs if r.name == "mysql-8.4" and r.bug_id == "2089720"]
    assert len(paired) == 1


def test_candidate_names_returns_distinct_in_order():
    refs = [
        PredecessorRef(name="mysql-8.4", bug_id=None),
        PredecessorRef(name="mysql-8.0", bug_id=None),
        PredecessorRef(name="mysql-8.4", bug_id="1"),
        PredecessorRef(name=None, bug_id="2"),
    ]
    assert predecessor_refs.candidate_names(refs) == ["mysql-8.4", "mysql-8.0"]


def test_explicit_bug_ids_returns_distinct_in_order():
    refs = [
        PredecessorRef(name="mysql-8.4", bug_id="2089720"),
        PredecessorRef(name=None, bug_id="111"),
        PredecessorRef(name=None, bug_id="2089720"),
    ]
    assert predecessor_refs.explicit_bug_ids(refs) == ["2089720", "111"]


def test_empty_text_returns_empty():
    assert predecessor_refs.extract_predecessor_refs("", "libfoo") == []


def test_no_signals_returns_empty():
    assert predecessor_refs.extract_predecessor_refs("A brand new library.", "libfoo") == []


# ---------------------------------------------------------------------------
# Real-world bug text (mysql-9.7 / LP #2160635 style)
# ---------------------------------------------------------------------------


def test_real_world_mysql_rename_text():
    text = (
        "This MIR will allow mysql-9.7 to replace mysql-8.4 as the provider of "
        "libmysqlclient24 and related binaries with the same level of security "
        "support.\n\nMIR for mysql-8.4 - LP: #2089720\n\nThis MIR should be "
        "compatible with the renamed-or-reorganized-sources policy."
    )
    refs = predecessor_refs.extract_predecessor_refs(text, "mysql-9.7")
    names = predecessor_refs.candidate_names(refs)
    ids = predecessor_refs.explicit_bug_ids(refs)
    assert "mysql-8.4" in names
    assert "2089720" in ids
    # The current source is never reported.
    assert "mysql-9.7" not in names
