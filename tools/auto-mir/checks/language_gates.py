"""Language gate resolution for auto-mir checks.

The per-language detectors live in ``utils.language_detection`` (the
single source of truth shared with the evidence adapters); this module
maps gate names to those detectors and resolves whether a gate is active
for the current run's packaging evidence.
"""

from __future__ import annotations

import logging
from typing import Callable

from utils.language_detection import (
    _is_go_package,
    _is_python_package,
    _is_rust_package,
)

log = logging.getLogger("auto_mir.checks.language_gates")

# Maps a single-language gate name to the one detector function used both
# here and directly by any check that needs the fact outside the gating path
# (e.g. CB-8 calls ``_is_python_package`` itself). Keeping exactly one
# detector per language avoids two independently-evolving implementations of
# "is this package written in X" ever silently drifting apart.
_GATE_DETECTORS: dict[str, Callable[[dict], bool]] = {
    "go": _is_go_package,
    "rust": _is_rust_package,
    "python": _is_python_package,
}


def _language_gate_active(gate: str, ctx) -> bool:
    """Return True when the named language gate is active for this package.

    The gate is resolved from evidence already collected by ESL-4 (Go gate)
    and ESL-8 (Rust gate).  If evidence is unavailable we conservatively
    return True (treat as potentially applicable) so the check is not silently
    skipped when we cannot confirm the absence of the language.

    Gates:
            go     — active when a declared Go signal (dh-golang /
                    --with golang / go.sum / dh-sequence-golang) or the
                    package's own Go tree hints are present
                    (``_is_go_package``)
            rust   — active when a declared Rust signal (dh_cargo /
                    --buildsystem cargo / Cargo.lock / dh-sequence-cargo)
                    or the package's own Rust tree hints are present
                    (``_is_rust_package``)
      python  — active per the same packaging-metadata heuristics CB-8 uses
                    directly (``_is_python_package``)
      go|rust — active when either go or rust is present (combined gate)

    Tree hints only activate a gate when no *other* language is declared by
    the packaging (declared buildsystem wins), so foreign-language files in
    vendored or auxiliary trees cannot misclassify a package.

    Supports pipe-separated combined gates; returns True if any of the listed
    gates would be active. Every single-language gate dispatches to the one
    detector function also used directly by checks that need the fact outside
    the gating path (e.g. CB-8 calls ``_is_python_package``), so there is
    exactly one detection heuristic per language, never a second, looser
    one duplicated here.
    """
    gate = gate.lower()

    # Support combined gates like "go|rust"
    if "|" in gate:
        gates = [g.strip() for g in gate.split("|")]
        return any(_language_gate_active(g, ctx) for g in gates)

    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})

    if packaging.get("status") != "ok":
        # Cannot confirm absence; assume gate may be active.
        return True

    detector = _GATE_DETECTORS.get(gate)
    if detector is None:
        log.warning("Unknown language gate '%s'; treating as active", gate)
        return True
    return detector(packaging)
