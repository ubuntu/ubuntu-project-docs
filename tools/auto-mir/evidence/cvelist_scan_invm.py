#!/usr/bin/env python3
"""Self-contained cvelistV5 baseline scanner used by the host adapter.

This script is intentionally dependency-free (Python standard library only) and
does NOT import any auto-mir modules. The host adapter ``collect_cvelist_scan``
imports its ``scan_zip`` function. The command-line entry point remains useful
for isolated scanner tests and preserves the historical module interface; the
2026-07-13 data-lifecycle decision moved normal execution from the guest to the
host.

Workflow:
1. Discover the most recent cvelistV5 "all CVEs at midnight" baseline zip from the
   GitHub releases API.
2. Download that compressed baseline (the documented bulk-download method).
3. Stream-scan every CVE record in the zip WITHOUT extracting it to disk: a fast
   raw-bytes prefilter narrows the corpus, then matching records are JSON-parsed
   and confirmed with word-boundary matching against the search terms.

The goal is "parse a lot, identify few": the whole corpus is scanned but only a
handful of candidate CVE IDs are returned for downstream NVD enrichment.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import urllib.request
import zipfile

RELEASES_API = "https://api.github.com/repos/CVEProject/cvelistV5/releases?per_page=40"
BASELINE_SUFFIX = "_all_CVEs_at_midnight.zip"
_USER_AGENT = "auto-mir-cvelist-scan/1.0"
_HTTP_TIMEOUT = 180


def _http_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_baseline(url: str = RELEASES_API) -> tuple[str, str]:
    """Return (asset_name, download_url) of the newest midnight baseline zip."""
    releases = _http_json(url)
    if not isinstance(releases, list):
        raise RuntimeError("unexpected releases payload from GitHub API")
    for release in releases:
        for asset in release.get("assets", []) or []:
            name = str(asset.get("name") or "")
            if name.endswith(BASELINE_SUFFIX):
                download_url = str(asset.get("browser_download_url") or "")
                if download_url:
                    return name, download_url
    raise RuntimeError("no '*_all_CVEs_at_midnight.zip' asset found in recent releases")


def download(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)


def _term_patterns(terms: list[dict]) -> list[tuple[str, str, re.Pattern, bytes]]:
    """Compile (term, kind, word-regex, lowercased-bytes-prefilter) tuples."""
    compiled: list[tuple[str, str, re.Pattern, bytes]] = []
    seen: set[str] = set()
    for entry in terms:
        term = str(entry.get("term") or "").strip()
        kind = str(entry.get("kind") or "current").strip() or "current"
        if not term or term.lower() in seen:
            continue
        seen.add(term.lower())
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        compiled.append((term, kind, pattern, term.lower().encode("utf-8")))
    return compiled


def _en_description(cna: dict) -> str:
    descriptions = cna.get("descriptions") or []
    for desc in descriptions:
        if isinstance(desc, dict) and str(desc.get("lang") or "").lower().startswith("en"):
            return str(desc.get("value") or "").strip()
    if descriptions and isinstance(descriptions[0], dict):
        return str(descriptions[0].get("value") or "").strip()
    return ""


def _affected_products(cna: dict) -> list[str]:
    products: list[str] = []
    for item in cna.get("affected", []) or []:
        if not isinstance(item, dict):
            continue
        for key in ("product", "vendor"):
            value = str(item.get(key) or "").strip()
            if value and value not in products:
                products.append(value)
    return products


def _affected_versions(cna: dict) -> list[str]:
    versions: list[str] = []
    for item in cna.get("affected", []) or []:
        if not isinstance(item, dict):
            continue
        for ver in item.get("versions", []) or []:
            if not isinstance(ver, dict):
                continue
            base = str(ver.get("version") or "").strip()
            status = str(ver.get("status") or "").strip()
            less_than = str(ver.get("lessThan") or ver.get("lessThanOrEqual") or "").strip()
            if less_than and base:
                label = f"{base} to {less_than}"
            else:
                label = base
            if status and label:
                label = f"{label} ({status})"
            if label and label not in versions:
                versions.append(label)
    return versions[:20]


def _references(cna: dict) -> list[str]:
    refs: list[str] = []
    for ref in cna.get("references", []) or []:
        if isinstance(ref, dict):
            url = str(ref.get("url") or "").strip()
            if url and url not in refs:
                refs.append(url)
    return refs[:20]


def _severity(cna: dict) -> tuple[str, float]:
    best_label = "UNKNOWN"
    best_score = -1.0
    for metric in cna.get("metrics", []) or []:
        if not isinstance(metric, dict):
            continue
        for key in ("cvssV4_0", "cvssV3_1", "cvssV3_0"):
            values = metric.get(key)
            if isinstance(values, dict):
                label = str(values.get("baseSeverity") or "UNKNOWN").upper()
                try:
                    score = float(values.get("baseScore", -1))
                except (TypeError, ValueError):
                    score = -1.0
                if score > best_score:
                    best_score = score
                    best_label = label
    return best_label, best_score


def _match_term(record: dict, patterns: list[tuple[str, str, re.Pattern, bytes]]) -> tuple | None:
    cna = record.get("containers", {}).get("cna", {})
    haystacks = [
        " ".join(_affected_products(cna)),
        str(cna.get("title") or ""),
        _en_description(cna),
        " ".join(_references(cna)),
    ]
    blob = "\n".join(haystacks)
    # Prefer a "current" match over a "predecessor" match for the same record.
    fallback: tuple | None = None
    for term, kind, pattern, _prefilter in patterns:
        if pattern.search(blob):
            if kind == "current":
                return term, kind
            if fallback is None:
                fallback = (term, kind)
    return fallback


def scan_zip(zip_path: str, terms: list[dict]) -> list[dict]:
    """Scan every CVE record in the baseline zip and return candidate dicts."""
    patterns = _term_patterns(terms)
    if not patterns:
        return []
    prefilters = [prefilter for _term, _kind, _pat, prefilter in patterns]

    candidates: dict[str, dict] = {}
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename
            if not name.endswith(".json") or "/cves/" not in f"/{name}":
                continue
            try:
                raw = zf.read(info)
            except (OSError, zipfile.BadZipFile):
                continue
            lowered = raw.lower()
            if not any(prefilter in lowered for prefilter in prefilters):
                continue
            try:
                record = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                continue
            matched = _match_term(record, patterns)
            if not matched:
                continue
            matched_term, matched_kind = matched
            metadata = record.get("cveMetadata", {})
            cve_id = str(metadata.get("cveId") or "").strip()
            if not cve_id or cve_id in candidates:
                continue
            cna = record.get("containers", {}).get("cna", {})
            severity, _score = _severity(cna)
            candidates[cve_id] = {
                "id": cve_id,
                "matched_term": matched_term,
                "matched_kind": matched_kind,
                "title": str(cna.get("title") or "").strip(),
                "description": _en_description(cna),
                "affected_products": _affected_products(cna),
                "affected_versions": _affected_versions(cna),
                "references": _references(cna),
                "severity": severity,
            }
    return sorted(candidates.values(), key=lambda c: c["id"], reverse=True)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({"status": "error", "message": "missing terms file argument"}))
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        terms = json.load(fh)
    if not isinstance(terms, list):
        print(json.dumps({"status": "error", "message": "terms file must be a JSON list"}))
        return 2

    try:
        asset_name, download_url = discover_baseline()
    except Exception as exc:  # noqa: BLE001 - report any failure as JSON
        print(json.dumps({"status": "error", "message": f"baseline discovery failed: {exc}"}))
        return 1

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp:
        try:
            download(download_url, tmp.name)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"status": "error", "message": f"baseline download failed: {exc}"}))
            return 1
        try:
            candidates = scan_zip(tmp.name, terms)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"status": "error", "message": f"baseline scan failed: {exc}"}))
            return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "baseline": asset_name,
                "candidates": candidates,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
