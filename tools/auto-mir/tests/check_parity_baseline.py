"""Validate parity baseline fixture availability for refactor guardrails.

The manifest in tests/parity_baseline.json declares the baseline bug corpus and
required fixture files. In advisory mode, missing fixtures are reported but do
not fail. In strict mode, missing fixtures fail with a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    return data


def _as_string_list(obj: object, field: str) -> list[str]:
    if not isinstance(obj, list) or not all(isinstance(i, str) for i in obj):
        raise ValueError(f"{field} must be a list of strings")
    return list(obj)


def _manifest_cases(manifest: dict) -> list[dict]:
    cases = manifest.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("cases must be a list")
    normalized: list[dict] = []
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case entries must be objects")
        bug_id = case.get("bug_id")
        if not isinstance(bug_id, str) or not bug_id:
            raise ValueError("each case must include non-empty bug_id")
        normalized.append(case)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Check auto-mir parity baseline fixtures")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing fixtures regardless of manifest enforcement",
    )
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    manifest_path = here / "parity_baseline.json"
    fixtures_root = here / "fixtures"

    if not manifest_path.exists():
        print(f"ERROR: missing manifest: {manifest_path}")
        return 2

    try:
        manifest = _load_manifest(manifest_path)
        required = _as_string_list(manifest.get("required_artifacts", []), "required_artifacts")
        cases = _manifest_cases(manifest)
    except ValueError as exc:
        print(f"ERROR: invalid manifest: {exc}")
        return 2

    enforcement = str(manifest.get("enforcement", "advisory")).lower()
    strict = args.strict or enforcement == "strict"

    missing: list[str] = []
    for case in cases:
        bug_id = case["bug_id"]
        case_dir = fixtures_root / bug_id
        if not case_dir.exists():
            missing.append(f"{bug_id}: missing fixture directory {case_dir}")
            continue
        for filename in required:
            file_path = case_dir / filename
            if not file_path.exists():
                missing.append(f"{bug_id}: missing {filename}")

    mode = "strict" if strict else "advisory"
    print(f"Parity baseline manifest: {manifest_path.name} | mode={mode} | cases={len(cases)}")

    if missing:
        print("Missing baseline artifacts:")
        for line in missing:
            print(f"- {line}")
        if strict:
            print("Result: FAIL (strict mode)")
            return 1
        print("Result: WARN (advisory mode)")
        return 0

    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
