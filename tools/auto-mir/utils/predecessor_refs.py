"""predecessor_refs.py — extract rename/predecessor references from bug text.

When a MIR bug is a re-review of a renamed/reorganised source (e.g.
mysql-8.4 -> mysql-9.7), the reporter almost always says so in plain text:
"mysql-9.7 to replace mysql-8.4", "MIR for mysql-8.4 - LP: #2089720", etc.
These explicit references are the strongest, lowest-cost signal that a prior
MIR bug exists under a *different* source name — far more precise than probing
the archive for functionality neighbours (which is what dup-search does, and
which is consumed by the RDO-1 check rather than review-type detection).

This module is dependency-free and side-effect-free so it can be unit-tested
in isolation and reused by the ``lp-mir-history`` host adapter without
inverting the evidence -> review_type layering.

It performs no network access. Bug-id references are extracted as numbers; the
caller decides whether and how to fetch them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Debian source package names: lowercase alphanumeric, plus ``+``, ``.``, ``-``;
# must start with an alphanumeric. This mirrors dpkg's source-name charset and
# rejects free-form prose tokens like "the", "this", "old", "one".
_SOURCE_NAME_RE = re.compile(r"[a-z0-9][a-z0-9+.\-]*")

# Words that are syntactically valid source-name tokens but semantically are
# not package names. Kept lowercase. This is a stopword filter, not a heuristic
# whitelist: the patterns below only capture tokens that immediately follow a
# rename-indicating phrase, so the false-positive surface is already small.
#
# Pronouns/determiners (them, they, these, ...) are included because ordinary
# prose routinely uses "replace(s)/supersede(s) <pronoun>" to refer back to
# something named earlier in the sentence (e.g. "prompt-toolkit replaces them"
# meaning the GNU Readline family, not a literal package called "them"). Without
# these, such prose is misread as a real predecessor name and probed against
# Launchpad, where it reliably 404s (bug: candidate name "them" observed in the
# wild from exactly this phrasing).
_STOPWORDS = frozenset(
    {
        "the",
        "this",
        "that",
        "these",
        "those",
        "old",
        "new",
        "one",
        "other",
        "others",
        "package",
        "source",
        "version",
        "previous",
        "prior",
        "former",
        "upstream",
        "it",
        "a",
        "an",
        "them",
        "they",
        "us",
        "we",
        "some",
        "all",
        "both",
        "either",
        "neither",
        "more",
        "most",
        "several",
        "many",
    }
)


@dataclass(frozen=True)
class PredecessorRef:
    """A predecessor reference extracted from bug text.

    - ``name``: a candidate source-package name, validated against the Debian
      source-name charset. ``None`` when only a bare bug-id reference was found
      with no accompanying name.
    - ``bug_id``: an explicit Launchpad bug number, as a string of digits.
      ``None`` when the reference carried no ``LP: #NNNN`` / bug URL.
    """

    name: str | None
    bug_id: str | None


# --- bug-id patterns ---------------------------------------------------------
# "LP: #2089720", "LP #2089720", and canonical bug URLs. Launchpad bug ids are
# 6+ digits; the lower bound avoids matching short numbers in prose while still
# covering real MIR bugs (which are well into 7 digits today).
_LP_HASH_RE = re.compile(r"LP\s*:?\s*#(\d{6,})", re.IGNORECASE)
_LP_URL_RE = re.compile(
    r"bugs\.launchpad\.net/[^/\s)]+(?:/\+source/[^/\s)]+)?/\+bug/(\d{6,})",
    re.IGNORECASE,
)

# --- name-bearing phrases ----------------------------------------------------
# Each pattern must capture exactly one group: the candidate predecessor name
# token. The patterns are anchored on rename-indicating verbs/phrases so that
# ordinary prose does not produce spurious refs.
#
# The leading token of the captured name is validated post-match against
# _SOURCE_NAME_RE and filtered through _STOPWORDS, because a regex capturing
# "replace\s+(\S+)" can grab trailing punctuation or a stray word.
_NAME_PATTERNS = [
    re.compile(r"to\s+replace\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
    re.compile(r"\breplaces?\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
    re.compile(r"\breplaced\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
    re.compile(r"formerly\s+(?:known\s+as|named|called)\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
    re.compile(r"renamed\s+from\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
    re.compile(
        r"was\s+previously\s+(?:(?:known\s+as|named|called)\s+)?([A-Za-z0-9][\w+.\-]*)",
        re.IGNORECASE,
    ),
    re.compile(r"\bsupersed(?:es|ed)\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE),
]

# Title-form references: "[MIR] mysql-8.4" or "MIR for mysql-8.4". These appear
# both in bug titles and inline in descriptions/comments pointing at the prior
# review. The name must NOT equal the current source.
_MIR_TITLE_NAME_RE = re.compile(r"\[mir\]\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE)
_MIR_FOR_NAME_RE = re.compile(r"\bmir\s+for\s+([A-Za-z0-9][\w+.\-]*)", re.IGNORECASE)


def _valid_name(token: str, current_source: str) -> str | None:
    """Return the cleaned, validated name, or None if it is not a real ref.

    Strips trailing punctuation that the word-boundary capture may have
    included, validates the remaining token against the Debian source-name
    charset, and rejects stopwords and the current source name.
    """
    cleaned = token.rstrip(".,;:!?)")
    if not cleaned:
        return None
    if not _SOURCE_NAME_RE.fullmatch(cleaned):
        return None
    low = cleaned.lower()
    if low == current_source.lower():
        return None
    if low in _STOPWORDS:
        return None
    return cleaned


def extract_predecessor_refs(text: str, current_source: str) -> list[PredecessorRef]:
    """Extract rename/predecessor references from free-form bug text.

    Scans the combined bug title, description, comments, and reporter content
    (the caller is responsible for concatenation). Returns refs in source-text
    order, deduplicated by (name, bug_id). A single span such as
    "MIR for mysql-8.4 - LP: #2089720" yields one ref carrying both the name
    and the bug id.

    ``current_source`` is the source package under review; it is never returned
    as a predecessor name.
    """
    if not text:
        return []

    refs: list[PredecessorRef] = []
    seen: set[tuple[str | None, str | None]] = set()

    def _add(name: str | None, bug_id: str | None) -> None:
        key = (name.lower() if name else None, bug_id)
        if key in seen:
            return
        seen.add(key)
        refs.append(PredecessorRef(name=name, bug_id=bug_id))

    # Bug-id references. We capture the surrounding window so a co-located name
    # (e.g. "MIR for mysql-8.4 - LP: #2089720") can be paired with the bug id.
    bug_id_spans: list[tuple[str, int, int]] = []
    for rx in (_LP_HASH_RE, _LP_URL_RE):
        for m in rx.finditer(text):
            bug_id = m.group(1)
            start, end = m.span()
            bug_id_spans.append((bug_id, start, end))
            # Look for a name within a small window around the bug id so an
            # inline "MIR for X - LP: #NNNN" reference is paired.
            window_start = max(0, start - 60)
            window_end = min(len(text), end + 10)
            window = text[window_start:window_end]
            paired_name: str | None = None
            for name_rx in (_MIR_FOR_NAME_RE, _MIR_TITLE_NAME_RE):
                nm = name_rx.search(window)
                if nm:
                    candidate = _valid_name(nm.group(1), current_source)
                    if candidate:
                        paired_name = candidate
                        break
            _add(paired_name, bug_id)

    # Name-bearing phrases (without a bug id). Scan the whole text; refs that
    # already appeared paired with a bug id are deduplicated by the seen-set.
    for rx in _NAME_PATTERNS:
        for m in rx.finditer(text):
            candidate = _valid_name(m.group(1), current_source)
            if candidate:
                _add(candidate, None)

    # Title-form names not adjacent to a bug id.
    for rx in (_MIR_FOR_NAME_RE, _MIR_TITLE_NAME_RE):
        for m in rx.finditer(text):
            candidate = _valid_name(m.group(1), current_source)
            if candidate:
                _add(candidate, None)

    return refs


def candidate_names(refs: list[PredecessorRef]) -> list[str]:
    """Return the distinct predecessor names from ``refs``, in first-seen order.

    Bug-ref-only entries (name is None) contribute nothing. This is the list a
    caller feeds to a Launchpad searchTasks probe; explicit bug-id refs are
    fetched directly by the caller rather than re-probed by name.
    """
    names: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref.name:
            low = ref.name.lower()
            if low not in seen:
                seen.add(low)
                names.append(ref.name)
    return names


def explicit_bug_ids(refs: list[PredecessorRef]) -> list[str]:
    """Return the distinct explicit bug ids from ``refs``, in first-seen order."""
    ids: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref.bug_id and ref.bug_id not in seen:
            seen.add(ref.bug_id)
            ids.append(ref.bug_id)
    return ids
