#!/usr/bin/env python3
"""auto_mir.py — MIR reviewer assistant entrypoint.

AI-assisted tool that fetches a Launchpad MIR bug, collects evidence inside a
fresh LXD container, evaluates checks from the catalog, and renders a
reviewer-template-aligned draft ready to post on the bug.

Exits 0 on successful run (even if review has required findings).
Exits 1 on hard stop conditions (missing reporter MIR content, tool errors).

Run with --help for full option reference.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import catalog
import checks
import llm
import lp_intake
import lxd_runner
from evidence import collect_from_catalog
from render import write_outputs

log = logging.getLogger("auto_mir")


# ---------------------------------------------------------------------------
# Run-name helpers (shared base name for container + output dir)
# ---------------------------------------------------------------------------


def _make_run_name(bug_id: str) -> str:
    """Generate a human-readable run name: mir-<bugid>-<YYYYMMDD-HHMMSS>."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"mir-{bug_id}-{ts}"


def _name_in_use(name: str) -> bool:
    """Return True if /tmp/<name> dir exists or an LXD container named <name> exists."""
    if Path(f"/tmp/{name}").exists():
        return True
    # Best-effort LXD check; ignore if lxc is not installed yet.
    try:
        result = subprocess.run(
            ["lxc", "info", name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def _resolve_run_name(bug_id: str, user_name: str | None) -> str:
    """Return the resolved run name, applying collision logic.

    Auto-generated name: bumped with -1, -2, ... suffix when taken.
    User-supplied name:   refused with SystemExit(1) when already in use.
    """
    if user_name:
        if _name_in_use(user_name):
            log.error(
                "Run name '%s' already exists (LXD container or /tmp/%s directory). "
                "Choose a different name with --run-name.",
                user_name,
                user_name,
            )
            raise SystemExit(1)
        return user_name

    base = _make_run_name(bug_id)
    if not _name_in_use(base):
        return base

    for suffix in range(1, 100):
        candidate = f"{base}-{suffix}"
        if not _name_in_use(candidate):
            log.warning(
                "Run name '%s' already in use; using '%s' instead.",
                base,
                candidate,
            )
            return candidate

    log.error("Could not find an unused run name after 99 attempts (base: %s).", base)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="AI-assisted MIR reviewer assistant",
    )
    p.add_argument("bug_id", help="Launchpad MIR bug ID")
    p.add_argument(
        "--series",
        default=None,
        metavar="SERIES",
        help=(
            "Force a specific Ubuntu series (e.g. focal, noble), skipping auto-detection. "
            "When omitted, the series is derived from the Launchpad bug tasks: if all tasks "
            "target one particular release that release is used, otherwise the development "
            "release (devel) is assumed."
        ),
    )
    p.add_argument(
        "--lxd-image",
        default=None,
        help=(
            "LXD image alias to run checks in"
            " (default: target release image, falling back to Ubuntu devel)"
        ),
    )
    p.add_argument(
        "--keep-container",
        dest="keep_container",
        action="store_true",
        default=False,
        help="Keep LXD container after run (default: off)",
    )
    p.add_argument(
        "--pin-uat-tooling",
        default=None,
        metavar="COMMIT",
        help="Pin ubuntu-archive-tools to this git commit (default: HEAD)",
    )
    p.add_argument(
        "--llm-model",
        default="gpt-4.1-mini",
        help=(
            "Model name for the selected LLM provider. "
            "Defaults: copilot → gpt-4.1-mini; openai-compatible → openai/gpt-4.1-mini."
        ),
    )
    p.add_argument(
        "--llm-provider",
        default=None,
        choices=["copilot", "openai-compatible"],
        help=(
            "LLM provider to use. When omitted, auto-detected from environment: "
            "COPILOT_GITHUB_TOKEN/GH_TOKEN/GITHUB_TOKEN → copilot; "
            "OPENAI_API_KEY → openai-compatible; "
            "gh auth token → copilot."
        ),
    )
    p.add_argument(
        "--run-name",
        default=None,
        metavar="NAME",
        help=(
            "Base name used for both the LXD container and the /tmp/<NAME> output directory "
            "(default: mir-<bugid>-<YYYYMMDD-HHMMSS>). "
            "When auto-generated, an existing name is bumped with a -1/-2 suffix. "
            "When specified manually, the run is refused if the name already exists."
        ),
    )
    p.add_argument(
        "--debug-collect-only",
        dest="collect_only",
        action="store_true",
        default=False,
        help=(
            "Debug mode: fetch LP bug and collect evidence only; "
            "skip AI synthesis and rendering. "
            "Evidence is saved to the output directory for inspection."
        ),
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    return p


# ---------------------------------------------------------------------------
# Run context
# ---------------------------------------------------------------------------


class RunContext:
    """Holds all runtime parameters and accumulated evidence for one review run.

    Attribute lifecycle
    -------------------
    Resolved in __init__ (from CLI args):
        bug_id, series, keep_container, pin_uat_tooling, lxd_image,
        llm_model, _llm_provider_flag, collect_only, tool_root,
        workspace_root, catalog_path, run_name, output_dir

    Populated by stage_auth (Stage 0 — auth setup):
        llm_provider, llm_api_url, llm_token, auth_source, container_env

    Populated by stage_intake / lp_intake.run() (Stage 1):
        bug, source_package, reporter_mir_content, series (may be refined)

    Populated by stage_spawn_container / lxd_runner.spawn() (Stage 2):
        container_name, container_env (refined with run-time values)

    Populated by stage_collect_evidence / evidence.collect_from_catalog() (Stage 3):
        evidence (including evidence["adapters"], evidence["catalog_summary"], etc.)

    Populated by stage_analyse / checks.evaluate_checks() (Stage 4):
        findings

    Populated by stage_render / render.write_outputs() (Stage 5):
        report_path, review_draft_path

    Updated incrementally by llm.call_llm() (during Stage 4):
        llm_calls_by_model, llm_estimated_tokens
    """

    def __init__(self, args: argparse.Namespace):
        # --- From CLI args (immutable after __init__) ---
        self.bug_id: str = str(args.bug_id)
        self.series: str | None = args.series
        self.keep_container: bool = args.keep_container
        self.pin_uat_tooling: str | None = args.pin_uat_tooling
        self.lxd_image: str | None = args.lxd_image
        self.llm_model: str = args.llm_model
        self._llm_provider_flag: str | None = getattr(args, "llm_provider", None)
        self.collect_only: bool = args.collect_only
        self.tool_root = Path(__file__).resolve().parent
        self.workspace_root = self.tool_root.parent.parent
        self.catalog_path = self.tool_root / "catalog.yaml"

        self.run_name: str = _resolve_run_name(
            bug_id=self.bug_id,
            user_name=getattr(args, "run_name", None),
        )
        self.output_dir = Path("/tmp") / self.run_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # --- Populated by stage_auth (Stage 0) ---
        self.llm_provider: str = ""
        self.llm_api_url: str = ""
        self.llm_token: str = ""
        self.auth_source: str = ""
        self.container_env: dict[str, str] = {}

        # --- Populated by stage_intake / lp_intake.run() (Stage 1) ---
        self.bug: dict = {}
        self.source_package: str = ""
        self.reporter_mir_content: str = ""

        # --- Populated by stage_spawn_container / lxd_runner.spawn() (Stage 2) ---
        self.container_name: str = ""

        # --- Populated by stage_collect_evidence / evidence.collect_from_catalog() (Stage 3) ---
        self.catalog: dict = {}   # loaded in Stage 3 (or Stage 4 if Stage 3 skipped)
        self.evidence: dict = {}

        # --- Populated by stage_analyse / checks.evaluate_checks() (Stage 4) ---
        self.findings: list[dict] = []

        # --- Populated by stage_render / render.write_outputs() (Stage 5) ---
        self.report_path: Path | None = None
        self.review_draft_path: Path | None = None

        # --- Updated by llm.call_llm() during Stage 4 ---
        self.llm_calls_by_model: dict[str, int] = {}
        self.llm_estimated_tokens: dict[str, int] = {}

    def save_evidence(self) -> None:
        """Persist accumulated evidence to output directory for debugging/audit."""
        evidence_path = self.output_dir / "evidence.json"
        with evidence_path.open("w") as f:
            json.dump(self.evidence, f, indent=2, default=str)
        log.debug("Evidence saved to %s", evidence_path)


# ---------------------------------------------------------------------------
# Pipeline stages (stubs)
# ---------------------------------------------------------------------------


def stage_intake(ctx: RunContext) -> None:
    """Stage 1: Launchpad API intake.

    - Fetch bug metadata, description, comments, and target source package.
    - Hard-fail if reporter MIR content is not found.
    - Auto-detect target Ubuntu series from LP bug tasks when not explicitly forced
      via --series; defaults to devel when no single series can be inferred.
    """
    log.info("Stage 1: Launchpad intake for bug %s", ctx.bug_id)
    lp_intake.run(ctx)
    # lp_intake.run() populates ctx.bug, ctx.source_package, ctx.reporter_mir_content
    # and raises SystemExit(1) with a clear message if reporter content is missing.


def stage_spawn_container(ctx: RunContext) -> None:
    """Stage 2: Spawn LXD container and provision tooling.

    - Create new container from target Ubuntu release image (or devel fallback).
    - Install required tools inside container.
    - Bootstrap ubuntu-archive-tools at requested revision.
    """
    log.info("Stage 2: Spawning LXD container for %s", ctx.source_package)
    lxd_runner.spawn(ctx)
    ctx.evidence["runtime_isolation"] = lxd_runner.collect_runtime_facts(ctx)
    # lxd_runner.spawn() populates ctx.container_name


def stage_collect_evidence(ctx: RunContext) -> None:
    """Stage 3: Run deterministic evidence collectors inside the container.

    Collectors run in-container via lxd_runner.exec():
    - sbuild test build -> build logs + lintian output
    - packaging source fetch via git-ubuntu
    - runtime dependency extraction
    - component-mismatches tooling
    - Launchpad API queries (build state, upload history, bug search)
    - Debian BTS queries
    - upstream tracker detection and querying
    - Ubuntu CVE tracker + cve.org queries
    - autopkgtest DB queries
    """
    log.info("Stage 3: Collecting evidence for %s", ctx.source_package)
    if not ctx.catalog:
        ctx.catalog = catalog.load_catalog(ctx.catalog_path, ctx.workspace_root)
        ctx.evidence["catalog_summary"] = catalog.summarize_catalog(ctx.catalog)

    collect_from_catalog(ctx)
    adapter_results = ctx.evidence.get("adapters", {})
    ctx.evidence["collection_summary"] = {
        "total_adapters_seen": len(adapter_results),
        "implemented_ok": len([x for x in adapter_results.values() if x.get("status") == "ok"]),
        "pending": len([x for x in adapter_results.values() if x.get("status") == "pending"]),
        "error": len([x for x in adapter_results.values() if x.get("status") == "error"]),
    }


def stage_analyse(ctx: RunContext) -> None:
    """Stage 4: Run check catalog against collected evidence.

    - Load catalog.yaml
    - For each check: run deterministic rules, then AI synthesis where mode requires it.
    - Evaluate security triggers.
    - Produce findings list with status/severity/confidence per check.
    """
    log.info("Stage 4: Analysing evidence for %s", ctx.source_package)
    if not ctx.catalog:
        ctx.catalog = catalog.load_catalog(ctx.catalog_path, ctx.workspace_root)

    ctx.findings = checks.evaluate_checks(ctx)
    ctx.evidence["analysis_summary"] = {
        "total_checks": len(ctx.findings),
        "evaluated_checks": len([f for f in ctx.findings if f["status"] != "not-evaluated"]),
        "pending_checks": len([f for f in ctx.findings if f["status"] == "not-evaluated"]),
    }


def stage_render(ctx: RunContext) -> None:
    """Stage 5: Render findings into output artefacts.

    Outputs:
    - evidence.json: full evidence store for debugging/audit
    - report.json: structured findings with severity, confidence, evidence refs
    - review-draft.txt: reviewer-template-aligned draft ready to post on LP bug

    Rendering rules (from catalog render_policy):
    - Template-close wording; AI may append up to 2-sentence rationale
    - Unresolved items begin with TODO:
    - No RULE: lines survive
    - Output linter validates conformance before writing
    """
    log.info("Stage 5: Rendering output for %s", ctx.source_package)
    write_outputs(ctx)


def stage_auth(ctx: RunContext) -> None:
    """Stage 0: Resolve LLM provider, endpoint URL, and authentication token.

    Provider selection priority:
    1. --llm-provider flag (explicit override)
    2. COPILOT_GITHUB_TOKEN / GH_TOKEN / GITHUB_TOKEN present → copilot
    3. OPENAI_API_KEY present                                  → openai-compatible
    4. gh auth token succeeds                                  → copilot
    5. No token found                                          → hard-fail
    """
    explicit_provider = getattr(ctx, "_llm_provider_flag", None)
    provider, token, source, api_url = llm.resolve_auth(explicit_provider)

    if not token:
        log.error(
            "No LLM authentication token found.\n"
            "For copilot:           set COPILOT_GITHUB_TOKEN, GH_TOKEN, or GITHUB_TOKEN\n"
            "                       or run: gh auth login\n"
            "For openai-compatible: set OPENAI_API_KEY (and optionally OPENAI_API_BASE)"
        )
        raise SystemExit(1)

    ctx.llm_provider = provider
    ctx.llm_api_url = api_url
    ctx.llm_token = token
    ctx.auth_source = source

    # Export token into container environment for in-container use
    if provider == "copilot":
        ctx.container_env = {
            "COPILOT_GITHUB_TOKEN": token,
            "GH_TOKEN": token,
            "GITHUB_TOKEN": token,
        }
    else:
        ctx.container_env = {
            "OPENAI_API_KEY": token,
            "OPENAI_API_BASE": api_url.rstrip("/chat/completions"),
        }

    ctx.evidence["auth"] = {
        "provider": provider,
        "source": source,
        "api_url": api_url,
    }
    log.info("LLM provider '%s' resolved from %s (url: %s)", provider, source, api_url)


def _stub_stage(name: str, ctx: RunContext) -> None:
    """Placeholder for unimplemented pipeline stages."""
    log.warning("Stage '%s' is not yet implemented (stub)", name)
    ctx.evidence[f"_stub_{name}"] = True


# ---------------------------------------------------------------------------
# Container teardown
# ---------------------------------------------------------------------------


def teardown_container(ctx: RunContext) -> None:
    """Destroy or preserve LXD container based on --keep-container flag."""
    if not ctx.container_name:
        return
    if ctx.keep_container:
        log.info(
            "Container %s preserved for debugging. To destroy: lxc delete --force %s",
            ctx.container_name,
            ctx.container_name,
        )
    else:
        log.info("Destroying container %s", ctx.container_name)
        lxd_runner.destroy(ctx)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    ctx = RunContext(args)

    log.info(
        "auto-mir starting: bug=%s keep_container=%s debug_collect_only=%s",
        ctx.bug_id,
        ctx.keep_container,
        ctx.collect_only,
    )
    log.debug(
        "LLM configuration for this run: provider=auto requested_model=%s",
        ctx.llm_model or "(provider default)",
    )

    try:
        # Stage 0: Resolve provider auth and container token export values
        stage_auth(ctx)

        # Stage 1: Launchpad intake (hard-fails if reporter MIR content missing)
        stage_intake(ctx)

        # Stage 2: Spawn LXD container
        stage_spawn_container(ctx)

        # Stage 3: Collect evidence in-container
        stage_collect_evidence(ctx)

        # Save evidence checkpoint for audit/debugging
        ctx.save_evidence()

        if ctx.collect_only:
            log.info("--debug-collect-only: stopping after evidence collection")
            _log_artifact_locations(ctx)
            return 0

        # Stage 4: Analyse against catalog checks
        stage_analyse(ctx)

        # Stage 5: Render output artefacts
        stage_render(ctx)

        log.info("Review draft written to: %s", ctx.review_draft_path)
        log.info("Structured report written to: %s", ctx.report_path)
        _log_artifact_locations(ctx)

    except SystemExit:
        # Hard-stop conditions (e.g. missing reporter content) raise SystemExit
        raise
    except Exception as exc:
        log.error("Unexpected error: %s", exc, exc_info=args.verbose)
        _log_artifact_locations(ctx)
        return 1
    finally:
        teardown_container(ctx)

    return 0


def _log_artifact_locations(ctx: RunContext) -> None:
    """Print concise artifact paths so users can continue after noisy output."""
    log.info("Artifacts directory: %s", ctx.output_dir)

    evidence_path = ctx.output_dir / "evidence.json"
    if evidence_path.exists():
        log.info("Evidence file: %s", evidence_path)

    if ctx.report_path:
        log.info("Structured report: %s", ctx.report_path)

    if ctx.review_draft_path:
        log.info("Review draft: %s", ctx.review_draft_path)

    # Print a prominent end-of-run summary so paths are easy to spot after
    # verbose logging output.
    lines = [
        "",
        "━" * 64,
        "  auto-mir complete",
        f"  Output directory : {ctx.output_dir}",
    ]
    if ctx.review_draft_path:
        lines.append(f"  Review draft     : {ctx.review_draft_path}")
    if ctx.report_path:
        lines.append(f"  Structured report: {ctx.report_path}")
    evidence_path = ctx.output_dir / "evidence.json"
    if evidence_path.exists():
        lines.append(f"  Evidence file    : {evidence_path}")
    lines.append("━" * 64)
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
