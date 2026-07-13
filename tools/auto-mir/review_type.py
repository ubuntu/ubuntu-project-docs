"""Review-type detection for auto-mir.

Most MIR bugs are *fresh* reviews: a new source enters main for the first time
and its findings are blocking. Two fast-path cases are handled more softly:

- ``rereview``: a voluntary opt-in re-review of a package that has been in main
  for so long that no modern quality control was applied. The reviewer mostly
  runs a normal review, but everything is considered non-blocking and
  recommendation-only.
  https://ubuntu.com/project/docs/MIR/mir-rereview/#opt-in-re-review

- ``reorg``: a source that was already in main under a *different* name, due to
  renaming (often libraries carrying a version in the name) or splitting/
  reorganising sources. These are handled like a full review but, as with
  voluntary re-reviews, all findings are treated as non-blocking.
  https://ubuntu.com/project/docs/MIR/mir-rereview/#renamed-or-reorganized-sources

The final judgement is always the human reviewer's; they can promote any
softened "Recommended" line back to "Required" if they disagree. This module
only proposes a type and records the reasoning behind it. Detection is
deliberately tolerant of missing evidence (best-effort adapters may not have
run) and never raises.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

log = logging.getLogger("auto_mir.review_type")

# Review types. ``fresh`` is the safe default (normal, blocking review).
FRESH = "fresh"
REREVIEW = "rereview"
REORG = "reorg"

_VALID_FORCED = {FRESH, REREVIEW, REORG}

# Reporter-text signals. Kept as word-boundary regexes so we do not match inside
# unrelated words (e.g. "mirror" must not trigger on "mir").
_REREVIEW_TEXT_RE = re.compile(
    r"re-?review|opt-?in\s+re-?review|voluntary\s+re-?review",
    re.IGNORECASE,
)
_REORG_TEXT_RE = re.compile(
    r"renam(?:e|ed|ing)|reorganiz|reorganis|split\s+(?:out|from|of)|"
    r"was\s+previously|formerly\s+(?:known|named|called)|supersed",
    re.IGNORECASE,
)


@dataclass
class ReviewTypeDecision:
    """Outcome of review-type detection."""

    review_type: str = FRESH
    forced: bool = False
    rationale: str = ""
    signals: list[str] = field(default_factory=list)

    def to_evidence(self) -> dict:
        """Return a JSON-serialisable dict for ctx.evidence / report.json."""
        return {
            "review_type": self.review_type,
            "forced": self.forced,
            "rationale": self.rationale,
            "signals": list(self.signals),
        }


def _reporter_text(ctx) -> str:
    """Return the combined reporter/bug text to scan, lower-cased-safe."""
    parts: list[str] = []
    parts.append(str(getattr(ctx, "reporter_mir_content", "") or ""))
    bug = getattr(ctx, "bug", None)
    if isinstance(bug, dict):
        parts.append(str(bug.get("title", "") or ""))
        parts.append(str(bug.get("description", "") or ""))
    return "\n".join(p for p in parts if p)


def _adapters(ctx) -> dict:
    evidence = getattr(ctx, "evidence", None)
    if isinstance(evidence, dict):
        adapters = evidence.get("adapters", {})
        if isinstance(adapters, dict):
            return adapters
    return {}


def _all_binaries_already_in_main(ctx) -> bool:
    """True when the package ships binaries yet none need promotion.

    dep-analysis lists every binary package; component-mismatches lists the ones
    still needing a universe->main promotion. If there are binaries but the
    promotion list is empty, the package is effectively already in main — a
    strong voluntary-re-review signal.
    """
    adapters = _adapters(ctx)
    dep = adapters.get("dep-analysis", {})
    cm = adapters.get("component-mismatches", {})
    if not isinstance(dep, dict) or not isinstance(cm, dict):
        return False
    binaries = dep.get("binary_packages", []) or []
    promotion = cm.get("promotion_candidates", []) or []
    return bool(binaries) and not promotion


def _prior_mir_under_other_name(ctx) -> list[str]:
    """Return web links of prior MIR bugs matched under a *different* name."""
    adapters = _adapters(ctx)
    hist = adapters.get("lp-mir-history", {})
    if not isinstance(hist, dict):
        return []
    current = str(getattr(ctx, "source_package", "") or "").strip().lower()
    hits: list[str] = []
    for bug in hist.get("prior_mir_bugs", []) or []:
        if not isinstance(bug, dict):
            continue
        matched = str(bug.get("matched_name", "") or "").strip().lower()
        if matched and matched != current:
            hits.append(str(bug.get("web_link") or bug.get("id") or matched))
    return hits


def _dup_predecessor_in_main(ctx) -> list[str]:
    """Return dup-search candidate names that are already in main.

    A functional twin already in main is, in the rename/split context, a hint
    that this source may be a reorganised continuation of it.
    """
    adapters = _adapters(ctx)
    dup = adapters.get("dup-search", {})
    if not isinstance(dup, dict):
        return []
    names: list[str] = []
    for cand in dup.get("candidates", []) or []:
        if isinstance(cand, dict) and str(cand.get("component", "")).lower() == "main":
            name = str(cand.get("name", "") or "").strip()
            if name:
                names.append(name)
    return names


def detect_review_type(ctx) -> ReviewTypeDecision:
    """Detect (or honour a forced) review type for this run.

    The ``--review-type`` CLI value on ``ctx.review_type_arg`` takes precedence:
    ``fresh``/``rereview``/``reorg`` short-circuit auto-detection (but still
    record a rationale), while ``auto`` (the default) runs the heuristics below.

    reorg is checked before rereview because a renamed/reorganised source is the
    more specific case; both soften findings identically, so the label mainly
    tells the human reviewer which fast-path applies.
    """
    forced = str(getattr(ctx, "review_type_arg", "auto") or "auto").strip().lower()
    if forced in _VALID_FORCED:
        return ReviewTypeDecision(
            review_type=forced,
            forced=True,
            rationale=f"Forced via --review-type={forced}.",
            signals=[f"forced:{forced}"],
        )

    text = _reporter_text(ctx)
    signals: list[str] = []

    # --- reorg (renamed / reorganised source already in main) -------------
    reorg_signals: list[str] = []
    if _REORG_TEXT_RE.search(text):
        reorg_signals.append("reporter text mentions a rename/split/reorganisation")
    prior_other = _prior_mir_under_other_name(ctx)
    if prior_other:
        reorg_signals.append(
            f"a prior MIR bug exists under a different source name ({', '.join(prior_other[:3])})"
        )
    dup_main = _dup_predecessor_in_main(ctx)
    if dup_main:
        reorg_signals.append(
            "a functionally-similar package is already in main "
            f"({', '.join(sorted(set(dup_main))[:3])})"
        )
    if reorg_signals:
        signals.extend(f"reorg: {s}" for s in reorg_signals)
        rationale = (
            "Detected a renamed/reorganised source that appears to have been in "
            "main before: " + "; ".join(reorg_signals) + ". Treated like a "
            "re-review — all findings are non-blocking recommendations; the "
            "reviewer can promote any line back to Required."
        )
        return ReviewTypeDecision(
            review_type=REORG, forced=False, rationale=rationale, signals=signals
        )

    # --- rereview (voluntary opt-in re-review of a package in main) -------
    rereview_signals: list[str] = []
    if _REREVIEW_TEXT_RE.search(text):
        rereview_signals.append("reporter text requests a (voluntary) re-review")
    if _all_binaries_already_in_main(ctx):
        rereview_signals.append("all binary packages are already in main")
    if rereview_signals:
        signals.extend(f"rereview: {s}" for s in rereview_signals)
        rationale = (
            "Detected a voluntary re-review of a package already in main: "
            + "; ".join(rereview_signals)
            + ". All findings are non-blocking "
            "recommendations; the reviewer can promote any line back to Required."
        )
        return ReviewTypeDecision(
            review_type=REREVIEW, forced=False, rationale=rationale, signals=signals
        )

    return ReviewTypeDecision(
        review_type=FRESH,
        forced=False,
        rationale="No re-review or reorganisation signals detected; treated as a "
        "normal (blocking) fresh review.",
        signals=[],
    )
