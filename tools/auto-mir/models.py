"""Data models shared across auto-mir modules."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Finding:
    """A structured result for a single catalog check evaluation.

    Fields set at construction (from the check definition):
        id:           Catalog check identifier (e.g. "SUM-1")
        section:      Template section name (e.g. "Summary")
        title:        Human-readable check title
        mode:         Evaluation mode: "deterministic" | "ev_to_ai" | "ai" | "human_only"
        blocker_class: Blocker class from catalog (e.g. "none", "advisory", "hard")

    Fields set by evaluators:
        status:       "ok" | "not-ok" | "unknown" | "not-evaluated"
        severity:     "ok" | "recommended" | "required" | "nack"
        confidence:   "low" | "medium" | "high"
        message:      Reviewer-facing statement (1-2 sentences)
        todo:         Empty when resolved; TODO: prefixed line(s) when unresolved
        evidence_refs: Adapter keys consulted (e.g. ["dep-analysis:runtime_deps"])

    Fields set by LLM evaluators only:
        risk_flags:                  Free-form risk annotations from LLM response
        human_confirmation_required: Always True for AI-derived findings

    Fields set during post-processing in evaluate_checks():
        adapter_error_cause: Adapter IDs whose failure caused this finding to be unresolved
    """

    # --- From check definition ---
    id: str
    section: str
    title: str
    mode: str
    blocker_class: str = "none"

    # --- Set by evaluators ---
    status: str = "not-evaluated"
    # Invariant: severity is "ok" whenever status is "ok"
    severity: str = "ok"
    confidence: str = "low"
    message: str = "Check not evaluated"
    todo: str = ""
    evidence_refs: list[str] = field(default_factory=list)

    # --- Set by LLM evaluators only ---
    risk_flags: list[str] = field(default_factory=list)
    human_confirmation_required: bool = False

    # --- Set during post-processing ---
    adapter_error_cause: list[str] = field(default_factory=list)
