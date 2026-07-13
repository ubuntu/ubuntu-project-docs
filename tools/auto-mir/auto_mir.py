#!/usr/bin/env python3
"""auto_mir.py — MIR reviewer assistant entrypoint.

AI-assisted tool that fetches a Launchpad MIR bug, collects evidence inside a
fresh LXD guest, evaluates checks from the catalog, and renders a
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
import time
from datetime import datetime
from pathlib import Path

import catalog
import checks
import llm
import lp_intake
import lxd_runner
from evidence import collect_from_catalog
from render import _render_llm_usage_report, write_outputs
from utils.cli import parse_bool_arg
from utils.llm_sanitize import make_nonce

log = logging.getLogger("auto_mir")


# ---------------------------------------------------------------------------
# Run-name helpers (shared base name for LXD guest + output dir)
# ---------------------------------------------------------------------------


def _make_run_name(bug_id: str) -> str:
    """Generate a human-readable run name: mir-<bugid>-<YYYYMMDD-HHMMSS>."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"mir-{bug_id}-{ts}"


def _name_in_use(name: str) -> bool:
    """Return True if /tmp/<name> dir exists or an LXD guest named <name> exists."""
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
                "Run name '%s' already exists (LXD guest or /tmp/%s directory). "
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
        help="Target Ubuntu series (e.g., 'noble', 'jammy'). Auto-detected if not specified.",
    )
    p.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help=(
            "Directory to save artifacts (default: /tmp/mir-<bugid>-<YYYYMMDD-HHMMSS>). "
            "The LXD guest name is auto-generated independently."
        ),
    )
    p.add_argument(
        "--collect-only",
        dest="collect_only",
        action="store_true",
        default=False,
        help=(
            "Collect evidence only; skip AI synthesis and rendering. "
            "Use this to regenerate test fixtures by passing "
            "--output-dir tools/auto-mir/tests/fixtures/<bug_id>."
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
        "--lxd-options",
        dest="lxd_options",
        type=str,
        default="--vm -c limits.cpu=4 -c limits.memory=8GiB -d root,size=20GiB",
        help=(
            "LXD launch options (default: "
            "'--vm -c limits.cpu=4 -c limits.memory=8GiB -d root,size=20GiB'). "
            "Pass any lxc launch flags. Use empty string or override "
            "to switch guest type or change resources."
        ),
    )
    p.add_argument(
        "--keep-guest",
        dest="keep_guest",
        nargs="?",
        const=True,
        default=None,
        type=parse_bool_arg,
        metavar="true|false",
        help=(
            "Control LXD guest cleanup (tri-state). "
            "Not specified: destroy on success, preserve on failure. "
            "--keep-guest or --keep-guest=true: always preserve. "
            "--keep-guest=false: always destroy."
        ),
    )
    p.add_argument(
        "--pin-uat-tooling",
        dest="pin_uat_tooling",
        metavar="COMMIT",
        default=None,
        help="Pin ubuntu-archive-tools to a specific git commit (default: latest HEAD)",
    )
    p.add_argument(
        "--llm-model-small",
        dest="llm_model_small",
        default=None,
        help=("Model used for smaller/simpler LLM requests. Default when omitted: z-ai/glm-4.7."),
    )
    p.add_argument(
        "--llm-model-large",
        dest="llm_model_large",
        default=None,
        help=(
            "Model used for larger/more complex LLM requests. Default when omitted: z-ai/glm-5.2."
        ),
    )
    p.add_argument(
        "--request-binaries",
        dest="request_binaries",
        type=str,
        nargs="+",
        default=None,
        help="Binary packages requested for promotion in this MIR (space-separated)",
    )
    p.add_argument(
        "--source-pocket",
        dest="source_pocket",
        choices=["auto", "release", "proposed"],
        default="auto",
        help=(
            "Which archive pocket's source version to fetch, build and analyse. "
            "'auto' (default): prefer the version in -proposed when one exists "
            "(MIR maintainers often stage test/lintian fixes there), else the "
            "release pocket. 'proposed': require the proposed version. "
            "'release': always use the release-pocket version."
        ),
    )
    p.add_argument(
        "--review-type",
        dest="review_type",
        choices=["auto", "fresh", "rereview", "reorg"],
        default="auto",
        help=(
            "How to treat this review. 'auto' (default): detect a fast-path from "
            "the bug and evidence. 'fresh': a normal full review with blocking "
            "findings. 'rereview': a voluntary opt-in re-review of a package "
            "already in main; all findings are softened to non-blocking "
            "recommendations. 'reorg': a renamed/reorganised source that was "
            "already in main under another name; treated like a re-review with "
            "all findings softened to recommendations."
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
        bug_id, series, keep_guest, pin_uat_tooling, lxd_image,
        llm_model_small, llm_model_large, collect_only, tool_root,
        workspace_root, catalog_path, run_name, output_dir

    Populated by stage_auth (Stage 0 — auth setup):
        llm_provider, llm_api_url, llm_token, auth_source, guest_env

    Populated by stage_intake / lp_intake.run() (Stage 1):
        bug, source_package, reporter_mir_content, series (may be refined)

    Populated by stage_spawn_guest / lxd_runner.spawn() (Stage 2):
        guest_name, guest_env (refined with run-time values)

    Populated by stage_collect_evidence / evidence.collect_from_catalog() (Stage 3):
        evidence (including evidence["adapters"], evidence["catalog_summary"], etc.)

    Populated by stage_analyse / checks.evaluate_checks() (Stage 4):
        findings

    Populated by stage_render / render.write_outputs() (Stage 5):
        report_path, review_draft_path

    Updated incrementally by llm.call_llm() (during Stage 4):
        llm_calls_by_model, llm_estimated_tokens, llm_reasoning_traces
    """

    def __init__(self, args: argparse.Namespace):
        # --- From CLI args (immutable after __init__) ---
        self.bug_id: str = str(args.bug_id)
        self.series: str | None = args.series
        self.keep_guest: bool | None = args.keep_guest
        self.pin_uat_tooling: str | None = args.pin_uat_tooling
        self.lxd_image: str | None = args.lxd_image
        self.llm_model_small: str | None = args.llm_model_small
        self.llm_model_large: str | None = args.llm_model_large
        self.collect_only: bool = args.collect_only
        self.lxd_options: str = args.lxd_options
        self.requested_binaries: list[str] = args.request_binaries or []
        # Which archive pocket's source to fetch/build/analyse (auto|release|proposed).
        self.source_pocket: str = getattr(args, "source_pocket", "auto")
        # How to treat this review (auto|fresh|rereview|reorg). 'auto' lets the
        # code detect a fast-path; the resolved value lands in review_type below.
        self.review_type_arg: str = getattr(args, "review_type", "auto")
        # Resolved review type (fresh|rereview|reorg), filled in during analysis
        # by review_type.detect_review_type(). Defaults to 'fresh' until then.
        self.review_type: str = "fresh"
        self.tool_root = Path(__file__).resolve().parent
        self.workspace_root = self.tool_root.parent.parent
        self.catalog_path = self.tool_root / "catalog.yaml"

        # LXD guest name is always auto-generated
        self.run_name: str = _resolve_run_name(bug_id=self.bug_id, user_name=None)

        # Output directory can be user-specified or auto-generated
        if args.output_dir:
            self.output_dir = Path(args.output_dir)
        else:
            self.output_dir = Path("/tmp") / self.run_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # --- Populated by stage_auth (Stage 0) ---
        self.llm_provider: str = ""
        self.llm_api_url: str = ""
        self.llm_token: str = ""
        self.auth_source: str = ""
        self.guest_env: dict[str, str] = {}

        # --- Populated by stage_intake / lp_intake.run() (Stage 1) ---
        self.bug: dict = {}
        self.source_package: str = ""
        self.reporter_mir_content: str = ""
        # Per-run nonce used to delimit untrusted-data envelopes in LLM prompts.
        self.untrusted_nonce: str = make_nonce()
        # --- Populated by stage_spawn_guest / lxd_runner.spawn() (Stage 2) ---
        self.guest_name: str = ""

        # --- Populated by stage_collect_evidence / evidence.collect_from_catalog() (Stage 3) ---
        self.catalog: dict = {}  # loaded in Stage 3 (or Stage 4 if Stage 3 skipped)
        self.evidence: dict = {}
        # Path to the shared, cached autopkgtest DB temp file (large). Set on
        # first use by the autopkgtest adapters and removed at end of Stage 3.
        self._autopkgtest_db_path: str | None = None

        # --- Populated by stage_analyse / checks.evaluate_checks() (Stage 4) ---
        self.findings: list[dict] = []

        # --- Populated by stage_render / render.write_outputs() (Stage 5) ---
        self.report_path: Path | None = None
        self.review_draft_path: Path | None = None

        # --- Populated on failures for teardown/user messaging ---
        self.failure_summary: str | None = None

        # --- Updated by llm.call_llm() during Stage 4 ---
        self.llm_calls_by_model: dict[str, int] = {}
        self.llm_estimated_tokens: dict[str, int] = {}
        self.llm_reasoning_traces: list[dict[str, str]] = []

    def save_evidence(self) -> None:
        """Persist accumulated evidence to output directory for debugging/audit."""
        evidence_path = self.output_dir / "evidence.json"
        with evidence_path.open("w") as f:
            json.dump(self.evidence, f, indent=2, default=str)
        log.debug("Evidence saved to %s", evidence_path)

        # If sbuild fails, users usually want to debug in a non json file
        sbuild_result = self.evidence.get("adapters", {}).get("sbuild", {})
        if not sbuild_result.get("build_success", True):
            build_log = sbuild_result.get("build_log", "")
            if build_log:
                build_log_path = self.output_dir / "build_log.txt"
                build_log_path.write_text(build_log)
                log.debug("Build log written to %s", build_log_path)


# ---------------------------------------------------------------------------
# Pipeline stages (stubs)
# ---------------------------------------------------------------------------


def stage_intake(ctx: RunContext) -> None:
    """Stage 1: Launchpad intake.

    Fetch bug metadata, description, comments, and target source package.
    Hard-fail if reporter MIR content is not found.
    """
    log.info("Stage 1: Launchpad intake for bug %s", ctx.bug_id)
    lp_intake.run(ctx)
    # lp_intake.run() populates ctx.bug, ctx.source_package, ctx.reporter_mir_content
    # and raises SystemExit(1) with a clear message if reporter content is missing.


def stage_spawn_guest(ctx: RunContext) -> None:
    """Stage 2: Spawn the LXD guest and provision tooling.

    - Create a new LXD guest from target Ubuntu release image (or devel fallback).
    - Install required tools inside the guest.
    - Bootstrap ubuntu-archive-tools at requested revision.
    """
    log.info("Stage 2: Spawning LXD guest for %s", ctx.source_package)
    lxd_runner.spawn(ctx)
    ctx.evidence["runtime_isolation"] = lxd_runner.collect_runtime_facts(ctx)
    # lxd_runner.spawn() populates ctx.guest_name


def stage_collect_evidence(ctx: RunContext) -> int:
    """Stage 3: Run deterministic evidence collectors inside the LXD guest.

    Collectors run in-guest via lxd_runner.exec():
    - sbuild test build -> build logs + lintian output
    - packaging source fetch via git-ubuntu
    - runtime dependency extraction
    - component-mismatches tooling
    - Launchpad API queries (build state, upload history, bug search)
    - Debian BTS queries
    - upstream tracker detection and querying
    - Ubuntu CVE tracker + cve.org queries
    - autopkgtest DB queries

    Returns:
        0 if all evidence collection succeeded, 1 if any adapter failed.
    """
    log.info("Stage 3: Collecting evidence for %s", ctx.source_package)
    if not ctx.catalog:
        ctx.catalog = catalog.load_catalog(ctx.catalog_path, ctx.workspace_root)
        ctx.evidence["catalog_summary"] = catalog.summarize_catalog(ctx.catalog)

    result = collect_from_catalog(ctx)
    adapter_results = ctx.evidence.get("adapters", {})
    ctx.evidence["collection_summary"] = {
        "total_adapters_seen": len(adapter_results),
        "implemented_ok": len([x for x in adapter_results.values() if x.get("status") == "ok"]),
        "pending": len([x for x in adapter_results.values() if x.get("status") == "pending"]),
        "error": len([x for x in adapter_results.values() if x.get("status") == "error"]),
    }
    return result


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
        "evaluated_checks": len([f for f in ctx.findings if f.status != "not-evaluated"]),
        "pending_checks": len([f for f in ctx.findings if f.status == "not-evaluated"]),
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
    """Stage 0: Resolve OpenAI-compatible endpoint URL and authentication token."""
    provider, token, source, api_url = llm.resolve_auth()

    if not token:
        log.error(
            "No LLM authentication token found.\n"
            "Set OPENAI_API_KEY (and optionally OPENAI_API_BASE)."
        )
        raise SystemExit(1)

    ctx.llm_provider = provider
    ctx.llm_api_url = api_url
    ctx.llm_token = token
    ctx.auth_source = source

    # Export token into guest environment for in-guest use
    ctx.guest_env = {
        "OPENAI_API_KEY": token,
        "OPENAI_API_BASE": api_url.rstrip("/chat/completions"),
    }

    ctx.evidence["auth"] = {
        "provider": provider,
        "source": source,
        "api_url": api_url,
    }
    log.info("LLM provider '%s' resolved from %s (url: %s)", provider, source, api_url)


def _resolve_requested_binaries(all_binaries: list[str]) -> list[str]:
    """Determine the promotion scope when nothing was requested explicitly.

    Neither the reporter's MIR template nor the ``--request-binaries`` CLI flag
    named any binaries. Resolve the scope without needless interaction:

    - No binaries built: nothing to resolve (return empty).
    - Exactly one binary built: it is unambiguously the promotion target, so
      select it silently (this is why a reporter can omit it too).
    - More than one binary and an interactive TTY: ask the reviewer.
    - More than one binary without a TTY (headless/automation): default to all
      rather than blocking on input the caller cannot provide.
    """
    if not all_binaries:
        return []

    if len(all_binaries) == 1:
        only = all_binaries[0]
        log.info("Single binary package built (%s); selecting it as the promotion target", only)
        return [only]

    if not sys.stdin.isatty():
        log.info(
            "Multiple binary packages built and no interactive terminal; "
            "defaulting promotion scope to all: %s",
            ", ".join(sorted(all_binaries)),
        )
        return list(all_binaries)

    return _ask_requested_binaries(all_binaries)


def _ask_requested_binaries(all_binaries: list[str]) -> list[str]:
    """Interactively ask user which binaries to promote.

    Returns list of binary package names to promote, or all_binaries if user
    selects "all" or provides no input.
    """
    print("\nCould not determine which binary packages are requested for promotion.")
    print(f"Binary packages built by this source: {', '.join(sorted(all_binaries))}")
    print("\nEnter binary packages to promote (comma-separated), or 'all' for all:")
    try:
        response = input("> ").strip()
    except EOFError:
        return all_binaries

    if not response or response.lower() == "all":
        return all_binaries

    packages = [p.strip() for p in response.split(",")]
    packages = [p for p in packages if p in all_binaries]

    if not packages:
        print("No valid packages specified, defaulting to all.")
        return all_binaries

    return packages


# ---------------------------------------------------------------------------
# LXD guest teardown
# ---------------------------------------------------------------------------


def teardown_guest(ctx: RunContext, evidence_collection_result: int = 0) -> None:
    """Destroy or preserve the LXD guest based on --keep-guest and run outcome.

    Tri-state logic:
      - keep_guest=True:  always preserve the guest
      - keep_guest=False: always destroy the guest
      - keep_guest=None:  destroy on success (evidence_collection_result==0), prompt on failure
    """
    if not ctx.guest_name:
        return

    failure_summary = getattr(ctx, "failure_summary", None)
    if not failure_summary and evidence_collection_result != 0:
        failure_summary = "Evidence collection encountered adapter failures."

    def _confirm_keep_failed_guest() -> bool:
        """Ask whether to preserve a failed guest when keep behavior is unspecified."""
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            log.warning(
                "%s Keep behavior is unspecified, "
                "but no interactive terminal is available."
                "Use --keep-guest=false/true to always destroy/keep.",
                failure_summary or "The run failed.",
            )
            return False

        print(
            f"\n{failure_summary or 'The run failed.'} "
            f"LXD guest {ctx.guest_name} could be preserved for debugging."
        )
        print(
            "Warning: Keeping failed guests can consume significant memory, clean them up via LXD."
        )
        while True:
            response = input("Keep LXD guest for debugging? [y/n]: ").strip().lower()
            if response in {"y", "yes"}:
                return True
            if response in {"n", "no"}:
                return False
            print("Please answer y or n.")

    if ctx.keep_guest is True:
        should_keep = True
    elif ctx.keep_guest is False:
        should_keep = False
    else:
        should_keep = _confirm_keep_failed_guest() if evidence_collection_result != 0 else False

    if should_keep:
        log.info(
            "LXD guest %s preserved for debugging. To destroy: lxc delete --force %s",
            ctx.guest_name,
            ctx.guest_name,
        )
    else:
        log.info("Destroying LXD guest %s", ctx.guest_name)
        lxd_runner.destroy(ctx)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    ctx = RunContext(args)

    # Setup dual logging: colored console + JSON file
    _log_start_time = time.monotonic()

    class ColorFormatter(logging.Formatter):
        """Colored formatter for console output with H:M:S elapsed timing."""

        COLORS = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        RESET = "\033[0m"
        BOLD = "\033[1m"

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            levelname = f"{color}{self.BOLD}{record.levelname:8}{self.RESET}"
            name = f"\033[34m{record.name:32}{self.RESET}"
            elapsed = time.monotonic() - _log_start_time
            h, remainder = divmod(int(elapsed), 3600)
            m, s = divmod(remainder, 60)
            timing_str = f"\033[90m[{h:02d}:{m:02d}:{s:02d}]{self.RESET}"
            message = record.getMessage()
            return f"{levelname} {name} {timing_str} {message}"

    from pythonjsonlogger import jsonlogger

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_formatter = ColorFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with JSON (if output directory exists)
    if ctx.output_dir.exists():
        log_file = ctx.output_dir / "auto-mir.log"
        file_handler = logging.FileHandler(log_file)
        json_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
        log.info("JSON log file: %s", log_file)

    log.info(
        "auto-mir starting: bug=%s keep_guest=%s collect_only=%s",
        ctx.bug_id,
        ctx.keep_guest,
        ctx.collect_only,
    )
    log.debug(
        "LLM configuration for this run: provider=auto "
        "requested_small_model=%s requested_large_model=%s",
        ctx.llm_model_small or "(provider default)",
        ctx.llm_model_large or "(provider default)",
    )

    exit_code = 0
    evidence_result = 0
    current_stage = "startup"
    try:
        # Stage 0: Resolve provider auth and guest token export values
        # Skip auth if collect-only mode (no LLM needed)
        if not ctx.collect_only:
            current_stage = "Stage 0 (auth)"
            stage_auth(ctx)

        # Stage 1: Launchpad intake (hard-fails if reporter MIR content missing)
        current_stage = "Stage 1 (Launchpad intake)"
        stage_intake(ctx)

        # Stage 2: Spawn LXD guest
        current_stage = "Stage 2 (guest setup)"
        stage_spawn_guest(ctx)

        # Stage 3: Collect evidence in-guest
        current_stage = "Stage 3 (evidence collection)"
        evidence_result = stage_collect_evidence(ctx)
        if evidence_result != 0:
            ctx.failure_summary = "Evidence collection encountered adapter failures."

        # Resolve promotion scope when neither the reporter nor the CLI named
        # binaries (after evidence collection).
        if not ctx.requested_binaries:
            all_binaries = (
                ctx.evidence.get("adapters", {}).get("dep-analysis", {}).get("binary_packages", [])
            )
            ctx.requested_binaries = _resolve_requested_binaries(all_binaries)
            if ctx.requested_binaries:
                log.info("Requested binaries: %s", ", ".join(ctx.requested_binaries))

        # Handle early exit mode
        if ctx.collect_only:
            log.info("--collect-only: stopping after evidence collection")
            _save_test_artifacts(ctx)
        else:
            # Save evidence checkpoint for audit/debugging
            ctx.save_evidence()
            # Stage 4: Analyse against catalog checks
            current_stage = "Stage 4 (analysis)"
            stage_analyse(ctx)

            # Stage 5: Render output artefacts
            current_stage = "Stage 5 (rendering)"
            stage_render(ctx)

            log.info("Review draft written to: %s", ctx.review_draft_path)
            log.info("Structured report written to: %s", ctx.report_path)

    except SystemExit:
        raise
    except Exception as exc:
        if evidence_result != 0:
            ctx.failure_summary = (
                f"{current_stage} failed after evidence collection encountered adapter failures."
            )
        else:
            ctx.failure_summary = f"{current_stage} failed."
        log.error("Unexpected error: %s", exc, exc_info=args.verbose)
        exit_code = 1

    # Cleanup and final output (always runs)
    _log_artifact_locations(ctx)
    teardown_guest(ctx, evidence_result)
    _print_complete_banner(ctx)
    return exit_code


def _save_test_artifacts(ctx: RunContext) -> None:
    """Save test artifacts for debugging or regression testing.

    Artifacts are saved to ctx.output_dir. Includes context, evidence,
    deterministic findings, and metadata.
    """
    from dataclasses import asdict

    artifact_dir = ctx.output_dir

    context = {
        "bug_id": ctx.bug_id,
        "source_package": ctx.source_package,
        "series": ctx.series,
        "reporter_mir_content": ctx.reporter_mir_content,
        "bug": ctx.bug,
    }
    with (artifact_dir / "context.json").open("w") as f:
        json.dump(context, f, indent=2, default=str)

    with (artifact_dir / "evidence.json").open("w") as f:
        json.dump(ctx.evidence, f, indent=2, default=str)

    if not ctx.catalog:
        ctx.catalog = catalog.load_catalog(ctx.catalog_path, ctx.workspace_root)

    deterministic_catalog = {
        "checks": [c for c in ctx.catalog.get("checks", []) if c.get("mode") == "deterministic"]
    }
    ctx.catalog = deterministic_catalog

    findings = checks.evaluate_checks(ctx)

    findings_data = [asdict(f) for f in findings]
    with (artifact_dir / "deterministic_findings.json").open("w") as f:
        json.dump(findings_data, f, indent=2, default=str)

    try:
        git_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    except Exception:
        git_head = "unknown"

    meta = {
        "collected_at": datetime.now().isoformat(),
        "git_head": git_head,
        "tool_version": "0.1.0",
        "bug_id": ctx.bug_id,
        "source_package": ctx.source_package,
    }
    with (artifact_dir / "meta.json").open("w") as f:
        json.dump(meta, f, indent=2)

    log.info("Test artifacts saved to: %s", artifact_dir)
    log.info("  - context.json")
    log.info("  - evidence.json")
    log.info("  - deterministic_findings.json")
    log.info("  - meta.json")


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


def _print_complete_banner(ctx: RunContext) -> None:
    """Print a prominent end-of-run summary as the very last output."""
    # Print the LLM usage report immediately before the banner so it appears
    # together with the completion summary and artifact list.
    llm_report = _render_llm_usage_report(ctx)
    if llm_report:
        print("\n" + "\n".join(llm_report))

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
