"""Shared protocol contracts for cross-module orchestration boundaries.

These protocols document the minimal context surfaces consumed by major
subsystems. They are intentionally narrow so modules rely on explicit contracts
instead of the full RunContext implementation.
"""

from __future__ import annotations

from typing import Any, Protocol

from models import Finding


class ChecksContext(Protocol):
    """Minimal context surface required by checks evaluation."""

    catalog: dict[str, Any]
    evidence: dict[str, Any]
    findings: list[Finding]


class EvidenceContext(Protocol):
    """Minimal context surface required by evidence collection orchestration."""

    catalog: dict[str, Any]
    evidence: dict[str, Any]
    collect_only: bool
