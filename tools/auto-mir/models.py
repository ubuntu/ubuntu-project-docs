"""Data models shared across auto-mir modules."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Finding:
    """A structured result for a single catalog check evaluation.

    This dataclass represents the outcome of evaluating one MIR check from the catalog.
    It captures the check result, severity, confidence level, and any TODO items for
    human reviewers.

    Required Fields (set at construction from check definition):
        id:             Catalog check identifier (e.g. "SUM-1", "DEP-3", "SEC-2")
        section:        Template section name (e.g. "Summary", "Dependencies", "Security")
        title:          Human-readable check title (e.g. "Source package identified")
        mode:           Evaluation mode, one of:
                        - "deterministic": Pure logic, no AI
                        - "ev_to_ai": Evidence-based AI analysis
                        - "ai": AI synthesis across findings
                        - "human_only": Requires manual review

    Optional Fields (set by evaluators, have sensible defaults):
        blocker_class:  Blocker class from catalog: "none" (default), "advisory", or "hard"
        status:         Check result: "ok", "not-ok", "unknown", or "not-evaluated" (default)
        severity:       Impact level: "ok" (default), "recommended", "required", or "nack"
        confidence:     Evidence strength: "low" (default), "medium", or "high"
        message:        Reviewer-facing statement (1-2 sentences), defaults to "Check not evaluated"
        todo:           TODO item for unresolved checks, empty string when resolved (default)
        evidence_refs:  List of adapter keys consulted (e.g. ["dep-analysis:runtime_deps"])

    LLM-Specific Fields (set only by AI evaluators):
        risk_flags:                  Free-form risk annotations from LLM response
        human_confirmation_required: Always True for AI-derived findings, False otherwise

    Post-Processing Fields (set during evaluate_checks()):
        adapter_error_cause: List of adapter IDs whose failure caused unresolved status

    Invariants:
        - When status == "ok", severity MUST also be "ok"
        - When status == "not-ok", todo should contain a TODO: prefixed line
        - AI-derived findings (mode in ["ev_to_ai", "ai"]) have confidence capped at "medium"

    Examples:
        # Successful deterministic check
        >>> ok_finding = Finding(
        ...     id="SUM-1",
        ...     section="Summary",
        ...     title="Source package identified",
        ...     mode="deterministic",
        ...     status="ok",
        ...     severity="ok",
        ...     confidence="high",
        ...     message="Source package: libfoo",
        ...     evidence_refs=["lp-bug-api:source_package"]
        ... )

        # Failed check requiring action
        >>> failed_finding = Finding(
        ...     id="DEP-1",
        ...     section="Dependencies",
        ...     title="Runtime dependencies in main",
        ...     mode="deterministic",
        ...     blocker_class="hard",
        ...     status="not-ok",
        ...     severity="required",
        ...     confidence="high",
        ...     message="Runtime dependency 'libbar' not in main",
        ...     todo="TODO: - Promote libbar to main or remove dependency",
        ...     evidence_refs=["dep-analysis:runtime_deps"]
        ... )

        # AI-evaluated check with medium confidence
        >>> ai_finding = Finding(
        ...     id="RDO-1",
        ...     section="Rationale, Duplication and Ownership",
        ...     title="Duplicate functionality",
        ...     mode="ev_to_ai",
        ...     status="not-ok",
        ...     severity="recommended",
        ...     confidence="medium",
        ...     message="Possible overlap with libfoo-utils",
        ...     todo="TODO: - Investigate overlap with libfoo-utils",
        ...     human_confirmation_required=True,
        ...     risk_flags=["functional overlap detected"]
        ... )

        # Unresolved check due to adapter failure
        >>> unresolved_finding = Finding(
        ...     id="SEC-1",
        ...     section="Security",
        ...     title="CVE analysis",
        ...     mode="deterministic",
        ...     status="unknown",
        ...     severity="ok",
        ...     confidence="low",
        ...     message="Could not evaluate: adapter failed",
        ...     todo="TODO: - Manually check CVE database",
        ...     adapter_error_cause=["ubuntu-cve-tracker"]
        ... )
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
    # Evidence/reasoning behind the verdict, kept separate from the reviewer
    # statement (message/todo). The renderer composes it into a parenthetical
    # continuation line so the reviewer sees why the tool reached its
    # conclusion, whether the outcome is ok, a problem, or left to decide.
    rationale: str = ""
    evidence_refs: list[str] = field(default_factory=list)

    # --- Set by LLM evaluators only ---
    risk_flags: list[str] = field(default_factory=list)
    human_confirmation_required: bool = False

    # --- Rendering routing (from check definition) ---
    # When True, this finding's TODO is surfaced in the consolidated
    # Required/Recommended TODO blocks even though it lives in the [Summary]
    # section. Summary decision checks (ACK/NACK verdict, security review)
    # default to False so they render inline only and are not duplicated.
    aggregate_todo: bool = False

    # --- Set during post-processing ---
    adapter_error_cause: list[str] = field(default_factory=list)

    def succeed(self, message: str, confidence: str = "high", rationale: str = "") -> None:
        """Mark this finding as successfully met (ok)."""
        self.status = "ok"
        self.severity = "ok"
        self.confidence = confidence
        self.message = message
        self.todo = ""
        self.rationale = rationale

    def fail(
        self,
        message: str,
        todo: str,
        severity: str = "required",
        confidence: str = "high",
        status: str = "not-ok",
        rationale: str = "",
    ) -> None:
        """Mark this finding as failed or unknown, requiring a human TODO."""
        self.status = status
        self.severity = severity
        self.confidence = confidence
        self.message = message
        if not todo.startswith("TODO:"):
            todo = f"TODO: {todo}"
        self.todo = todo
        self.rationale = rationale

    def mark_unknown(
        self,
        message: str,
        todo: str = "",
        severity: str = "ok",
        confidence: str = "low",
        rationale: str = "",
    ) -> None:
        """Mark this finding as unresolved and leave reviewer guidance if needed."""
        self.status = "unknown"
        self.severity = severity
        self.confidence = confidence
        self.message = message
        self.todo = todo if (not todo or todo.startswith("TODO:")) else f"TODO: {todo}"
        self.rationale = rationale

    def ensure_todo(self, fallback: str) -> None:
        """Ensure unresolved findings carry a normalized TODO line."""
        if self.status == "ok":
            return
        if self.todo.startswith("TODO:") or self.todo.startswith("TODO-"):
            return
        self.todo = f"TODO: - {fallback}"

    def __post_init__(self):
        """Validate Finding invariants after initialization.

        Invariants:
        - When status == "ok", severity MUST also be "ok"
        - When status == "not-ok", todo should contain a TODO: prefixed line
        - confidence must be one of: "low", "medium", "high"
        - severity must be one of: "ok", "recommended", "required", "nack"
        - status must be one of: "ok", "not-ok", "unknown", "not-evaluated"
        """
        valid_statuses = {"ok", "not-ok", "unknown", "not-evaluated"}
        valid_severities = {"ok", "recommended", "required", "nack"}
        valid_confidences = {"low", "medium", "high"}

        if self.status not in valid_statuses:
            raise ValueError(
                f"Finding {self.id}: invalid status '{self.status}'. "
                f"Must be one of: {', '.join(sorted(valid_statuses))}"
            )

        if self.severity not in valid_severities:
            raise ValueError(
                f"Finding {self.id}: invalid severity '{self.severity}'. "
                f"Must be one of: {', '.join(sorted(valid_severities))}"
            )

        if self.confidence not in valid_confidences:
            raise ValueError(
                f"Finding {self.id}: invalid confidence '{self.confidence}'. "
                f"Must be one of: {', '.join(sorted(valid_confidences))}"
            )

        # Invariant: status="ok" implies severity="ok"
        if self.status == "ok" and self.severity != "ok":
            raise ValueError(
                f"Finding {self.id}: invariant violation - status='ok' requires severity='ok', "
                f"but severity='{self.severity}'"
            )

        # Invariant: status="not-ok" should have a TODO
        if self.status == "not-ok" and self.todo:
            if not (self.todo.startswith("TODO:") or self.todo.startswith("TODO-")):
                # This is a warning, not an error, to allow for transitional states
                import logging

                logging.getLogger("auto_mir.models").warning(
                    "Finding %s: status='not-ok' but todo doesn't start with 'TODO:': %s",
                    self.id,
                    self.todo[:50],
                )

    @classmethod
    def ok(
        cls,
        check: dict,
        message: str,
        evidence_refs: list[str] | None = None,
    ) -> "Finding":
        """Create a successful finding.

        Args:
            check: Check definition dict from catalog
            message: Reviewer-facing success message
            evidence_refs: Optional list of evidence adapter references

        Returns:
            Finding with status="ok", severity="ok", confidence="high"
        """
        return cls(
            id=check["id"],
            section=check.get("section", "unknown"),
            title=check.get("title", ""),
            mode=check.get("mode", "deterministic"),
            blocker_class=check.get("blocker_class", "none"),
            status="ok",
            severity="ok",
            confidence="high",
            message=message,
            todo="",
            evidence_refs=evidence_refs or [],
        )

    @classmethod
    def not_ok(
        cls,
        check: dict,
        severity: str,
        message: str,
        todo: str,
        confidence: str = "high",
        evidence_refs: list[str] | None = None,
    ) -> "Finding":
        """Create a failed finding.

        Args:
            check: Check definition dict from catalog
            severity: "recommended" | "required" | "nack"
            message: Reviewer-facing failure message
            todo: TODO item for human reviewer
            confidence: "low" | "medium" | "high" (default: "high")
            evidence_refs: Optional list of evidence adapter references

        Returns:
            Finding with status="not-ok"
        """
        return cls(
            id=check["id"],
            section=check.get("section", "unknown"),
            title=check.get("title", ""),
            mode=check.get("mode", "deterministic"),
            blocker_class=check.get("blocker_class", "none"),
            status="not-ok",
            severity=severity,
            confidence=confidence,
            message=message,
            todo=todo,
            evidence_refs=evidence_refs or [],
        )

    @classmethod
    def unknown(
        cls,
        check: dict,
        message: str,
        todo: str,
        adapter_error_cause: list[str] | None = None,
    ) -> "Finding":
        """Create an unresolved finding due to missing evidence.

        Args:
            check: Check definition dict from catalog
            message: Reviewer-facing explanation of why check couldn't be evaluated
            todo: TODO item for manual review
            adapter_error_cause: Optional list of failed adapter IDs

        Returns:
            Finding with status="unknown", severity="ok", confidence="low"
        """
        return cls(
            id=check["id"],
            section=check.get("section", "unknown"),
            title=check.get("title", ""),
            mode=check.get("mode", "deterministic"),
            blocker_class=check.get("blocker_class", "none"),
            status="unknown",
            severity="ok",
            confidence="low",
            message=message,
            todo=todo,
            adapter_error_cause=adapter_error_cause or [],
        )
