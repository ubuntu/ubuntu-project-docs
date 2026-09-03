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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.review_type")

# Review types. ``fresh`` is the safe default (normal, blocking review).
FRESH = "fresh"
REREVIEW = "rereview"
REORG = "reorg"

_VALID_FORCED = {FRESH, REREVIEW, REORG}

# Reporter-text signals - FALLBACK ONLY, used when the LLM is unavailable.
# Kept as word-boundary regexes so we do not match inside unrelated words
# (e.g. "mirror" must not trigger on "mir").
# High-precision rename wording only: "replace/supersede <other package>" is
# ordinary role-replacement rationale (RDO-1 territory) and "split out of
# <bug number>" is process language - both caused false reorgs in user tests,
# so "supersed"/"replac*" are gone and "split out/from/of" requires a
# non-numeric object.
_REREVIEW_TEXT_RE = re.compile(
    r"re-?review|opt-?in\s+re-?review|voluntary\s+re-?review",
    re.IGNORECASE,
)
_REORG_TEXT_RE = re.compile(
    r"renam(?:e|ed|ing)|reorganiz|reorganis|"
    r"split\s+(?:out\s+of|from|of)\s+(?!\d)(?!bug)|"
    r"was\s+previously|formerly\s+(?:known|named|called)",
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


def _reporter_text(ctx: RunContext) -> str:
    """Return the combined reporter/bug text to scan, lower-cased-safe."""
    parts: list[str] = []
    parts.append(str(getattr(ctx, "reporter_mir_content", "") or ""))
    bug = getattr(ctx, "bug", None)
    if isinstance(bug, dict):
        parts.append(str(bug.get("title", "") or ""))
        parts.append(str(bug.get("description", "") or ""))
        for comment in bug.get("comments", []) or []:
            parts.append(str(comment or ""))
    return "\n".join(p for p in parts if p)


def _adapters(ctx: RunContext) -> dict:
    evidence = getattr(ctx, "evidence", None)
    if isinstance(evidence, dict):
        adapters = evidence.get("adapters", {})
        if isinstance(adapters, dict):
            return adapters
    return {}


def _all_binaries_already_in_main(ctx: RunContext) -> bool:
    """True when the source's binaries are currently published in main.

    Uses ``lp-package-api``'s ``current_component`` — the component of the
    newest publish record for this source in the target series, equivalent to
    what ``rmadison`` shows — as the sole source of truth. Fails closed
    (returns False) when that adapter is missing/unavailable/unresolved,
    rather than guessing: this is deliberately the only source of truth here.

    NOTE: ``component-mismatches`` (the ubuntu-archive-tools promotion-report
    script) was previously (mis)used as this signal by treating an empty
    promotion-candidate list as "already in main". That tool only reports
    seed/component *mismatches*; an empty list is equally produced when a
    package is correctly sitting in universe with no main-seed expectation at
    all, so it cannot answer "is this already in main" (see decisions.md for
    the 2026-08-05 correction).
    """
    adapters = _adapters(ctx)
    lp_package = adapters.get("lp-package-api", {})
    if not isinstance(lp_package, dict):
        return False
    return lp_package.get("current_component") == "main"


def _prior_mir_under_other_name(ctx: RunContext) -> list[str]:
    """Return links of prior MIR bugs for a *retired* predecessor name.

    Only names that are no longer published in the archive count (the
    lp-mir-history adapter verifies each distinct matched name): a matched
    name that is still published is a sibling package, not a rename - e.g.
    a MIR for a related tool filed under an unrelated Launchpad project must
    never turn a fresh review into a reorg. Fails safe: unverified names
    (missing still_published flag) are not rename evidence.
    """
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
        if not matched or matched == current:
            continue
        if bug.get("still_published") is not False:
            continue
        hits.append(str(bug.get("web_link") or bug.get("id") or matched))
    return hits


def _text_signals(ctx: RunContext) -> tuple[list[str], list[str]]:
    """Return (reorg_signals, rereview_signals) from fallback bug-text patterns.

    High-precision rename/re-review wording only (see the regex comments);
    never the primary signal - the LLM classification is. Returns empty lists
    on clean text.
    """
    text = _reporter_text(ctx)
    reorg: list[str] = []
    rereview: list[str] = []
    if _REORG_TEXT_RE.search(text):
        reorg.append("bug text contains explicit rename/reorganisation wording")
    if _REREVIEW_TEXT_RE.search(text):
        rereview.append("bug text requests a (voluntary) re-review")
    return reorg, rereview


_LLM_REVIEW_TYPE_PROMPT = """You are assisting with an Ubuntu Main Inclusion Review (MIR).
Classify the MIR bug text below into exactly one category:

- "new": this is a genuinely new MIR for a package entering main for the first time.
- "rereview": this is a voluntary opt-in re-review of a package that is already in main
  and has been for a long time.
- "reorg": this source package was previously in main under a DIFFERENT name
  (renamed, split from, or absorbed into another source package).
- "unsure": the text is ambiguous about which of the above applies.

Important context:
- A rationale that says this package "replaces" or "supersedes" a different package
  (e.g. "we want to eventually replace gnupg2 with Sequoia") is role-replacement
  rationale, NOT a rename: it does NOT make this a reorg.
- References to other MIR bug numbers ("split out of 2089690") are process
  language, not a source-package split.
- Only classify as "reorg" if the SAME software/source was previously in main
  under a different source-package name.
- Only classify as "rereview" if the same source package has already been in
  main and this bug asks for a fresh review of it.

Return exactly this JSON (no markdown fences, no extra keys):
{"classification": "<new|rereview|reorg|unsure>",
 "reasoning": "1-3 sentences explaining your classification"}

MIR bug text (title, description, comments, reporter template):
"""


_LLM_REVIEW_TYPE_MAX_TEXT_CHARS = 24_000


def llm_classify_review_text(ctx: RunContext) -> tuple[str, str] | None:
    """Classify the MIR bug text as new/rereview/reorg/unsure with one LLM call.

    Returns ``(classification, reasoning)`` or ``None`` when the LLM is
    unavailable, misconfigured or the response is unusable - the caller then
    falls back to the high-precision regex signals.
    """
    token = str(getattr(ctx, "llm_token", "") or "")
    if not token or getattr(ctx, "no_llm", False):
        return None
    text = _reporter_text(ctx)[:_LLM_REVIEW_TYPE_MAX_TEXT_CHARS]
    if not text.strip():
        return None

    import llm

    prompt = _LLM_REVIEW_TYPE_PROMPT + text
    try:
        response = llm.call_llm(prompt, ctx, model_tier="small", trace_label="REVIEW-TYPE")
    except llm.LLMError as exc:
        log.debug("review-type LLM classification unavailable: %s", exc)
        return None

    classification = str(response.get("classification", "")).strip().lower()
    reasoning = str(response.get("reasoning", "")).strip()
    if classification not in {"new", "rereview", "reorg", "unsure"}:
        log.debug("review-type LLM classification unusable: %r", classification)
        return None
    return classification, reasoning


def _interactive_confirm(
    ctx: RunContext, suggested: str, reasoning: str
) -> ReviewTypeDecision | None:
    """Present a suspicious classification with its reasoning; the human decides.

    Returns the human's decision, or ``None`` when no interactive terminal is
    available (headless runs stay on the safe fresh path with a warning).
    """
    import sys

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None

    from utils.cli import ask_yes_no

    print("\n" + "=" * 64)
    print("The MIR bug text suggests this might be a %s." % suggested)
    if reasoning:
        print("Reasoning: %s" % reasoning)
    print("=" * 64)
    if ask_yes_no(f"Classify this run as {suggested}?", default=False):
        return ReviewTypeDecision(
            review_type=suggested,
            forced=False,
            rationale=(
                f"LLM classified the MIR bug text as '{suggested}' "
                f"({reasoning or 'no reasoning provided'}) and the user confirmed."
            ),
            signals=[f"llm:{suggested}", "user-confirmed"],
        )
    print("Continuing as a fresh (blocking) review per user decision.")
    return ReviewTypeDecision(
        review_type=FRESH,
        forced=False,
        rationale=(
            f"LLM suggested '{suggested}' ({reasoning or 'no reasoning provided'}) "
            "but the user overrode it to a fresh review."
        ),
        signals=[f"llm:{suggested}", "user-override"],
    )


def pre_classify_review_type(ctx: RunContext) -> ReviewTypeDecision:
    """Stage-1 first decision over the MIR bug text (user-test round 3 design).

    One bounded LLM call classifies the reporter's content
    {new|rereview|reorg|unsure}. 'new' proceeds silently; anything suspicious
    is presented interactively with the LLM's reasoning and the human decides.
    Falls back to the narrowed rename-wording regex when the LLM is
    unavailable. Headless (no TTY) defaults to fresh with a warning - fresh is
    the strict classification, so misclassifying fresh-on-suspicion only costs
    the softer fast-path, never the blocking findings.

    The decision is recorded on ``ctx.review_type_pre_decision`` so the
    authoritative Stage-4 resolution (``detect_review_type``) honors the
    human's choice.
    """
    forced = str(getattr(ctx, "review_type_arg", "auto") or "auto").strip().lower()
    if forced in _VALID_FORCED:
        decision = ReviewTypeDecision(
            review_type=forced,
            forced=True,
            rationale=f"Forced via --review-type={forced}.",
            signals=[f"forced:{forced}"],
        )
        ctx.review_type_pre_decision = decision
        return decision

    classification = llm_classify_review_text(ctx)
    if classification is not None:
        kind, reasoning = classification
        if kind == "new":
            decision = ReviewTypeDecision(
                review_type=FRESH,
                forced=False,
                rationale=(
                    "LLM classified the MIR bug text as a new MIR"
                    + (f" ({reasoning})" if reasoning else "")
                    + "."
                ),
                signals=["llm:new"],
            )
        else:
            decision = _interactive_confirm(ctx, kind, reasoning)
            if decision is None:
                log.warning(
                    "Review-type LLM classification suggested '%s' but no "
                    "interactive terminal is available; defaulting to a fresh "
                    "(blocking) review. LLM reasoning: %s",
                    kind,
                    reasoning or "(none)",
                )
                decision = ReviewTypeDecision(
                    review_type=FRESH,
                    forced=False,
                    rationale=(
                        f"Headless run: LLM suggested '{kind}' "
                        f"({reasoning or 'no reasoning provided'}) but fresh was "
                        "chosen as the safe default."
                    ),
                    signals=[f"llm:{kind}", "headless-default"],
                )
        ctx.review_type_pre_decision = decision
        return decision

    # Fallback: narrowed regex signals + same interactive treatment.
    reorg_signals, rereview_signals = _text_signals(ctx)
    if reorg_signals or rereview_signals:
        suggested = REORG if reorg_signals else REREVIEW
        detail = "; ".join(reorg_signals or rereview_signals)
        decision = _interactive_confirm(ctx, suggested, f"fallback text-pattern match: {detail}")
        if decision is None:
            log.warning(
                "Fallback text signals suggest %s but no interactive terminal "
                "is available; defaulting to a fresh (blocking) review. "
                "Signals: %s",
                suggested,
                detail,
            )
            decision = ReviewTypeDecision(
                review_type=FRESH,
                forced=False,
                rationale=(
                    f"Headless run: fallback text signals suggested '{suggested}' "
                    f"({detail}) but fresh was chosen as the safe default."
                ),
                signals=[f"fallback:{suggested}", "headless-default"],
            )
        ctx.review_type_pre_decision = decision
        return decision

    decision = ReviewTypeDecision(
        review_type=FRESH,
        forced=False,
        rationale=(
            "No re-review or reorganisation signals detected in the MIR bug "
            "text; treated as a normal (blocking) fresh review."
        ),
        signals=[],
    )
    ctx.review_type_pre_decision = decision
    return decision


def detect_review_type(ctx: RunContext, use_evidence: bool = True) -> ReviewTypeDecision:
    """Detect (or honour a forced) review type for this run.

    The ``--review-type`` CLI value on ``ctx.review_type_arg`` takes precedence:
    ``fresh``/``rereview``/``reorg`` short-circuit auto-detection (but still
    record a rationale), while ``auto`` (the default) runs the heuristics below.

    ``use_evidence=False`` is the Stage-1 pre-detection entry point
    (``pre_classify_review_type``, called by ``lp_intake.run()``): the LLM
    classification of the reporter's MIR content plus, on suspicion, an
    interactive human confirmation. The resulting human decision is honoured
    here before any evidence heuristics; ``lp-mir-history`` (verified retired
    names) and ``lp-package-api`` (all-in-main) can still upgrade a fresh
    pre-decision to ``reorg``/``rereview``.

    reorg is checked before rereview because a renamed/reorganised source is the
    more specific case; both soften findings identically, so the label mainly
    tells the human reviewer which fast-path applies.

    ``dup-search`` is deliberately not a reorg signal: it is a low-precision
    suggestion pool whose proper consumer is the RDO-1 check (which reasons about
    genuine functional overlap). Using its raw candidate list as a reorg signal
    produced contradictory output (RDO-1 ok vs a "functionally-similar in main"
    rationale naming unrelated category-neighbours).
    """
    forced = str(getattr(ctx, "review_type_arg", "auto") or "auto").strip().lower()
    if forced in _VALID_FORCED:
        return ReviewTypeDecision(
            review_type=forced,
            forced=True,
            rationale=f"Forced via --review-type={forced}.",
            signals=[f"forced:{forced}"],
        )

    signals: list[str] = []

    # --- the Stage-1 human decision wins (the LLM classification +
    # interactive confirm already happened at intake; the reviewer chose). ---
    pre = getattr(ctx, "review_type_pre_decision", None)
    if isinstance(pre, ReviewTypeDecision):
        return pre

    # --- reorg (renamed / reorganised source already in main) -------------
    # NOTE: dup-search is intentionally NOT a reorg signal (see the RDO-1
    # notes). The only non-interactive reorg evidence is the verified
    # retired-name prior MIR (user-test round 2's still_published check).
    reorg_signals: list[str] = []
    prior_other = _prior_mir_under_other_name(ctx) if use_evidence else []
    if prior_other:
        reorg_signals.append(
            f"a prior MIR bug exists under a source name that is no longer published "
            f"in the archive - a renamed/absorbed predecessor ({', '.join(prior_other[:3])})"
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
    if use_evidence and _all_binaries_already_in_main(ctx):
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
