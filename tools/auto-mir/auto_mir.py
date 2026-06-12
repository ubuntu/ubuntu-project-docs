#!/usr/bin/env python3
"""auto_mir.py — MIR reviewer assistant entrypoint.

Usage:
    auto_mir.py <launchpad-bug-id> [options]

Options:
    --series SERIES          Target Ubuntu series (default: devel)
    --lxd-image IMAGE        LXD image alias for isolated execution (default: Ubuntu devel)
    --keep-container         Keep LXD container after run for debugging (default: off)
    --pin-uat-tooling COMMIT Pin ubuntu-archive-tools to specific commit for reproducible runs
    --llm-model MODEL        LLM model to request from provider (default: gpt-4o-mini)
    --run-name NAME          Base name for both the LXD container and /tmp output directory
                             (default: mir-<bugid>-<YYYYMMDD-HHMMSS>; auto-bumped with -1/-2
                              suffix on collision; explicit name refuses if already in use)
    --dry-run                Fetch and collect evidence only; skip AI synthesis and rendering

Exits 0 on successful run (even if review has required findings).
Exits 1 on hard stop conditions (missing reporter MIR content, tool errors).
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Internal modules
import catalog
import checks
from evidence import collect_from_catalog
import lp_intake
import lxd_runner
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
                user_name, user_name,
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
                base, candidate,
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
    p.add_argument("--series", default="devel", help="Target Ubuntu series (default: devel)")
    p.add_argument(
        "--lxd-image",
        default=None,
        help="LXD image alias to run checks in (default: first available Ubuntu devel alias)",
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
        default="gpt-4o-mini",
        help="Model name for the selected LLM provider (default: gpt-4o-mini)",
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
        "--dry-run",
        action="store_true",
        default=False,
        help="Collect evidence only; skip AI synthesis and rendering",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    return p


# ---------------------------------------------------------------------------
# Run context
# ---------------------------------------------------------------------------

class RunContext:
    """Holds all runtime parameters and accumulated evidence for one review run."""

    def __init__(self, args: argparse.Namespace):
        self.bug_id: str = str(args.bug_id)
        self.series: str | None = args.series
        self.keep_container: bool = args.keep_container
        self.pin_uat_tooling: str | None = args.pin_uat_tooling
        self.lxd_image: str | None = args.lxd_image
        self.llm_model: str = args.llm_model
        self.dry_run: bool = args.dry_run
        self.tool_root = Path(__file__).resolve().parent
        self.workspace_root = self.tool_root.parent.parent
        self.catalog_path = self.tool_root / "catalog.yaml"

        self.run_name: str = _resolve_run_name(
            bug_id=self.bug_id,
            user_name=getattr(args, "run_name", None),
        )
        self.output_dir = Path("/tmp") / self.run_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Populated by lp_intake
        self.bug: dict = {}
        self.source_package: str = ""
        self.reporter_mir_content: str = ""

        # Populated by evidence collectors
        self.evidence: dict = {}

        # Populated by catalog loader
        self.catalog: dict = {}

        # Populated by analysis layer
        self.findings: list[dict] = []

        # Populated by renderer
        self.report_path: Path | None = None
        self.review_draft_path: Path | None = None

        # Metadata recorded in report
        self.policy_hashes: dict = {}
        self.container_name: str = ""
        self.auth_source: str = ""
        self.container_env: dict[str, str] = {}

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
    - Detect target Ubuntu series if not specified.
    """
    log.info("Stage 1: Launchpad intake for bug %s", ctx.bug_id)
    lp_intake.run(ctx)
    # lp_intake.run() populates ctx.bug, ctx.source_package, ctx.reporter_mir_content
    # and raises SystemExit(1) with a clear message if reporter content is missing.


def stage_spawn_container(ctx: RunContext) -> None:
    """Stage 2: Spawn LXD container and provision tooling.

    - Create new container from Ubuntu devel image alias.
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
        ctx.policy_hashes = ctx.catalog.get("metadata", {}).get("policy_hashes", {})
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
        ctx.policy_hashes = ctx.catalog.get("metadata", {}).get("policy_hashes", {})

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
    """Stage 0: Resolve authentication for copilot provider.

    Priority:
    1) Host env vars: COPILOT_GITHUB_TOKEN, GH_TOKEN, GITHUB_TOKEN
    2) GitHub CLI login token: `gh auth token`
    """
    token, source = _resolve_copilot_token()
    if not token:
        log.error(
            "No GitHub authentication token found for copilot provider.\n"
            "Provide one of: COPILOT_GITHUB_TOKEN, GH_TOKEN, GITHUB_TOKEN\n"
            "or login with GitHub CLI so `gh auth status` succeeds."
        )
        raise SystemExit(1)

    ctx.auth_source = source
    ctx.container_env = {
        "COPILOT_GITHUB_TOKEN": token,
        "GH_TOKEN": token,
        "GITHUB_TOKEN": token,
    }
    ctx.evidence["auth"] = {
        "provider": "copilot",
        "source": source,
    }
    log.info("Copilot auth resolved from %s", source)


def _resolve_copilot_token() -> tuple[str | None, str]:
    for name in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value, f"host-env:{name}"

    try:
        gh_status = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None, ""
    if gh_status.returncode != 0:
        return None, ""

    gh_token = subprocess.run(
        ["gh", "auth", "token"],
        capture_output=True,
        text=True,
        check=False,
    )
    if gh_token.returncode != 0:
        return None, ""

    token = gh_token.stdout.strip()
    if not token:
        return None, ""

    return token, "gh-auth"


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
        format="%(levelname)s  %(name)s  %(message)s",
    )

    ctx = RunContext(args)

    log.info(
        "auto-mir starting: bug=%s keep_container=%s dry_run=%s",
        ctx.bug_id,
        ctx.keep_container,
        ctx.dry_run,
    )
    log.debug(
        "LLM configuration for this run: provider=copilot requested_model=%s",
        ctx.llm_model,
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

        if ctx.dry_run:
            log.info("--dry-run: stopping after evidence collection")
            _log_artifact_locations(ctx)
            return 0

        # Stage 4: Analyse against catalog checks
        stage_analyse(ctx)

        # Stage 5: Render output artefacts
        stage_render(ctx)

        log.info("Review draft written to: %s", ctx.review_draft_path)
        log.info("Structured report written to: %s", ctx.report_path)
        _log_artifact_locations(ctx)

    except SystemExit as exc:
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


if __name__ == "__main__":
    sys.exit(main())
