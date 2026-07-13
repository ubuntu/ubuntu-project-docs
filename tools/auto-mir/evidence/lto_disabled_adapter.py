"""LTO-disabled-list adapter.

Fetches the ``lto-disabled-list`` source package list to determine whether the
package under review is one that must not be built with link-time optimization
(LTO). A package may be listed for ``any`` architecture or for a specific set of
architectures; being listed for any architecture at all is enough to flag it.

Source of truth:
https://git.launchpad.net/ubuntu/+source/lto-disabled-list/plain/lto-disabled-list
"""

from __future__ import annotations

import logging
from typing import Any

from catalog_enums import AdapterID
from evidence.registry import adapter
from utils import http as http_utils

log = logging.getLogger("auto_mir.evidence.lto_disabled")

LTO_DISABLED_LIST_URL = (
    "https://git.launchpad.net/ubuntu/+source/lto-disabled-list/plain/lto-disabled-list"
)


def _parse_lto_disabled_list(text: str) -> dict[str, list[str]]:
    """Parse the list body into a ``{source_package: [arches]}`` mapping.

    Data lines have the form ``<source> <arch> [<arch> ...]`` where an arch may
    be the literal ``any``. Comment lines (``#``) and blank lines are skipped.
    """
    mapping: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        source = parts[0]
        arches = parts[1:]
        mapping[source] = arches
    return mapping


@adapter(AdapterID.LTO_DISABLED_LIST)
def collect_lto_disabled_list(ctx) -> dict[str, Any]:
    """Check whether the source package is on the lto-disabled-list.

    Returns a dict reporting whether the package is listed and, if so, for which
    architectures. On fetch/parse failure returns ``status: error`` so the
    consuming check degrades to "unknown" rather than a false pass.
    """
    source_package = ctx.source_package
    if not source_package:
        return {
            "status": "error",
            "error": "source_package not set in context",
        }

    try:
        log.info("Fetching lto-disabled-list from %s", LTO_DISABLED_LIST_URL)
        text = http_utils.get_text(LTO_DISABLED_LIST_URL, errors="strict")
    except Exception as e:
        log.error("Failed to fetch lto-disabled-list: %s", e)
        return {
            "status": "error",
            "error": str(e),
        }

    mapping = _parse_lto_disabled_list(text)
    disabled_arches = mapping.get(source_package, [])

    log.info(
        "lto-disabled-list check complete: %s is%s on the list (%d entries total)",
        source_package,
        "" if disabled_arches else " not",
        len(mapping),
    )

    return {
        "status": "ok",
        "source_package": source_package,
        "on_list": bool(disabled_arches),
        "disabled_arches": disabled_arches,
    }
