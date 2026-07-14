"""lxd_runner.py — LXD guest lifecycle for auto-mir.

The tool is host-orchestrated: this module creates a fresh LXD guest
from the target Ubuntu release image (falling back to Ubuntu devel when the
series is unknown), provisions tooling in-guest, dispatches commands
there, and handles cleanup.

This is explicitly NOT meant to be run from inside an existing LXD guest.
"""

import logging
import re
import shlex
import subprocess
import sys
import time
from typing import TYPE_CHECKING

from utils.retry import is_transient_command_failure, retry_guest_command

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.lxd_runner")

# Fallback Ubuntu devel image aliases, tried when the target series is unknown.
_UBUNTU_DEVEL_FALLBACK_IMAGES = [
    "ubuntu-daily:devel",
    "images:ubuntu/devel",
    "ubuntu:devel",
]

# Packages required inside the guest for the full pipeline.
# Note: sbuild is installed separately (from backports for Noble) to support unshare backend.
_REQUIRED_PACKAGES = [
    "lintian",
    "git-ubuntu",
    "ubuntu-dev-tools",  # provides seeded-in-ubuntu
    "dpkg-dev",
    "apt-utils",
    "python3-launchpadlib",
    "python3-yaml",
    "curl",
    "wget",
    "git",
    "germinate",  # prerequisite for component-mismatches
    "python3-apt",
    "python3-requests",
    "uidmap",  # required for sbuild unshare backend
    "mmdebstrap",  # required for sbuild unshare auto-create backend
]

# Remote for ubuntu-archive-tools
_ARCHIVE_TOOLS_REPO = "https://git.launchpad.net/ubuntu-archive-tools"
_ARCHIVE_TOOLS_DIR = "/opt/ubuntu-archive-tools"


def run_command(
    cmd: list[str], log_prefix: str, check: bool = True, capture: bool = False, **kwargs
) -> subprocess.CompletedProcess:
    """Run a subprocess and handle uniform error logging and checking."""
    log.debug("%s$ %s", log_prefix, shlex.join(cmd))
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        **kwargs,
    )
    if check and result.returncode != 0:
        log.error(
            "Command failed (exit %d): %s",
            result.returncode,
            shlex.join(cmd),
        )
        if capture:
            log.error("stdout: %s\nstderr: %s", result.stdout.strip(), result.stderr.strip())
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )
    return result


def _lxc(*args, check: bool = True, capture: bool = False, **kwargs):
    """Wrapper around lxc CLI."""
    return run_command(
        ["lxc"] + list(args),
        log_prefix="host",
        check=check,
        capture=capture,
        **kwargs,
    )


def _check_lxd_available() -> None:
    """Verify lxc is available on the host; exit with guidance if not."""
    result = subprocess.run(["which", "lxc"], capture_output=True, text=True)
    if result.returncode != 0:
        log.error("lxc command not found. Install LXD with: sudo snap install lxd && lxd init")
        sys.exit(1)

    # Quick connectivity check
    result = _lxc("version", capture=True, check=False)
    if result.returncode != 0:
        log.error("LXD is installed but not responding. Try: lxd init --auto")
        sys.exit(1)
    client_version = next(
        (
            line.split(": ", 1)[1]
            for line in result.stdout.splitlines()
            if line.startswith("Client version")
        ),
        "unknown",
    )
    server_version = next(
        (
            line.split(": ", 1)[1]
            for line in result.stdout.splitlines()
            if line.startswith("Server version")
        ),
        "unknown",
    )
    log.debug("LXD client version: %s", client_version)
    log.debug("LXD server version: %s", server_version)


def spawn(ctx: "RunContext") -> None:
    """Create a new LXD guest from the target Ubuntu release image and provision it.

    Populates ctx.guest_name.
    """
    _check_lxd_available()

    name = ctx.run_name
    ctx.guest_name = name
    image = _resolve_image(ctx)
    ctx.lxd_image = image

    # Parse LXD options from ctx.lxd_options
    # (default: "--vm -c limits.cpu=4 -c limits.memory=8GiB -d root,size=20GiB")
    lxd_opts = ctx.lxd_options.split() if ctx.lxd_options else []

    log.info(
        "Creating LXD guest %s from %s with options: %s",
        name,
        image,
        " ".join(lxd_opts),
    )

    # Build launch command: lxc launch <image> <name> [options...]
    launch_cmd = ["launch", image, name] + lxd_opts
    result = _lxc(*launch_cmd, capture=True, check=False)
    if result.returncode != 0:
        log.error("lxc launch failed (exit %d): %s", result.returncode, result.stderr.strip())
        raise subprocess.CalledProcessError(result.returncode, ["lxc"] + launch_cmd)

    # Wait for network to be available inside the guest
    _wait_for_network(name)

    log.info("Provisioning guest %s", name)
    _provision(name, ctx)

    log.info("Guest %s is ready", name)


def _resolve_image(ctx: "RunContext") -> str:
    """Resolve the image alias to use for this run.

    If the user provided --lxd-image, use that as-is.
    If the target series is known, probe series-specific aliases first
    (``ubuntu-daily:SERIES``, ``ubuntu:SERIES``) for reproducibility.
    Falls back to the Ubuntu devel aliases when the series is unknown or when
    no series-specific image is found.
    """
    explicit = getattr(ctx, "lxd_image", None)
    if explicit:
        return explicit

    series = getattr(ctx, "series", None)
    candidates: list[str] = []
    if series and series != "devel":
        candidates = [
            f"ubuntu-daily:{series}",
            f"ubuntu:{series}",
        ]

    for alias in candidates + _UBUNTU_DEVEL_FALLBACK_IMAGES:
        result = _lxc("image", "info", alias, check=False, capture=True)
        if result.returncode == 0:
            return alias

    tried = candidates + _UBUNTU_DEVEL_FALLBACK_IMAGES
    log.error(
        "Could not find a suitable LXD image for series %r. Tried: %s",
        series or "devel",
        ", ".join(tried),
    )
    sys.exit(1)


def _wait_for_network(name: str, timeout: int = 60) -> None:
    """Wait until the LXD guest has network connectivity."""
    log.debug("Waiting for network in %s", name)
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = exec_in(
            name,
            ["systemctl", "is-system-running", "--wait"],
            check=False,
            capture=True,
        )
        # systemd states: running, degraded are both acceptable
        if result.returncode in (0, 1):
            # Double-check network by pinging apt mirror
            check = exec_in(
                name,
                ["ping", "-c1", "-W3", "archive.ubuntu.com"],
                check=False,
                capture=True,
            )
            if check.returncode == 0:
                log.debug("Network available in guest %s", name)
                return
        time.sleep(2)
    log.warning(
        "Network did not become available in %s within %ds; continuing anyway",
        name,
        timeout,
    )


def _provision(name: str, ctx: "RunContext") -> None:
    """Install required tools and bootstrap upstream tooling inside the guest."""

    # Ensure source repositories are enabled before any `apt-get source` usage.
    _enable_source_repositories(name)

    # Enable the -proposed pocket so `apt-get source` (and sbuild) can resolve
    # the proposed-pocket version, which is what a MIR review should analyse
    # when the maintainer has staged fixes there. Skipped when the operator
    # explicitly pinned the release pocket.
    if getattr(ctx, "source_pocket", "auto") != "release":
        _enable_proposed_pocket(name)

    # Update package lists
    exec_in_retry(
        name,
        ["apt-get", "update", "-qq"],
        operation="apt-get update",
    )

    # Install required packages
    log.info("Installing required packages in guest")
    exec_in_retry(
        name,
        ["apt-get", "install", "-qq", "-y", "--no-install-recommends"] + _REQUIRED_PACKAGES,
        env={"DEBIAN_FRONTEND": "noninteractive"},
        operation="apt-get install required packages",
    )

    # Install sbuild (from backports for Noble to get unshare backend support)
    series = getattr(ctx, "series", None)
    if series == "noble":
        log.info("Installing sbuild from noble-backports")
        exec_in_retry(
            name,
            [
                "apt-get",
                "install",
                "-qq",
                "-y",
                "-t",
                "noble-backports",
                "--no-install-recommends",
                "sbuild",
                "mmdebstrap",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
            operation="apt-get install sbuild from backports",
        )
    else:
        log.info("Installing sbuild")
        exec_in_retry(
            name,
            [
                "apt-get",
                "install",
                "-qq",
                "-y",
                "--no-install-recommends",
                "sbuild",
                "mmdebstrap",
            ],
            env={"DEBIAN_FRONTEND": "noninteractive"},
            operation="apt-get install sbuild",
        )

    # Bootstrap ubuntu-archive-tools (component-mismatches and prerequisites)
    _bootstrap_archive_tools(name, ctx.pin_uat_tooling)


def _enable_source_repositories(name: str) -> None:
    """Enable deb-src in both legacy .list and deb822 .sources formats.

    Reads each apt sources file from the guest, applies Python regex
    substitutions to uncomment deb-src entries (legacy format) or expand
    Types: deb to Types: deb deb-src (deb822 format), then writes it back.
    """

    def _patch_legacy(text: str) -> str:
        """Uncomment '#deb-src' lines in a legacy .list file."""
        return re.sub(r"^#\s*deb-src\s+", "deb-src ", text, flags=re.MULTILINE)

    def _patch_deb822(text: str) -> str:
        """Expand 'Types: deb' to 'Types: deb deb-src' in a deb822 .sources file."""
        return re.sub(r"^(Types:\s*deb)\s*$", r"\1 deb-src", text, flags=re.MULTILINE)

    def _patch_file(guest_path: str, patcher) -> None:
        """Pull a file from the guest, patch it in Python, push it back."""
        result = exec_in(name, ["cat", guest_path], check=False, capture=True)
        if result.returncode != 0:
            return
        patched = patcher(result.stdout)
        if patched == result.stdout:
            return
        # Write patched content back via stdin
        _lxc("exec", name, "--", "tee", guest_path, capture=True, input=patched)

    # Discover relevant files inside the guest with a single listing.
    result = exec_in(
        name,
        [
            "find",
            "/etc/apt",
            "-maxdepth",
            "2",
            "-name",
            "*.list",
            "-o",
            "-name",
            "*.sources",
        ],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        log.warning("Could not list /etc/apt sources files; skipping deb-src enable")
        return

    for path in result.stdout.splitlines():
        path = path.strip()
        if not path:
            continue
        if path.endswith(".sources"):
            _patch_file(path, _patch_deb822)
        elif path.endswith(".list"):
            _patch_file(path, _patch_legacy)


def _enable_proposed_pocket(name: str) -> None:
    """Add the ``<codename>-proposed`` pocket (deb + deb-src) to the guest.

    MIR maintainers frequently stage test/lintian/packaging fixes in -proposed
    before they migrate to the release pocket, so a faithful review should be
    able to fetch, build and analyse that version. We derive a proposed deb822
    stanza from the existing ubuntu.sources (reusing its URIs, components and
    signing key) with the suite replaced by ``<codename>-proposed``, and write
    it to a dedicated file so the base configuration is left untouched.
    """
    codename = exec_in(
        name,
        ["bash", "-lc", ". /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"],
        capture=True,
        check=False,
    ).stdout.strip()
    if not codename:
        log.warning("Could not resolve guest codename; skipping -proposed enable")
        return

    base = exec_in(
        name,
        ["cat", "/etc/apt/sources.list.d/ubuntu.sources"],
        capture=True,
        check=False,
    )
    if base.returncode != 0 or not base.stdout.strip():
        log.warning("Could not read ubuntu.sources; skipping -proposed enable")
        return

    stanza = _build_proposed_stanza(base.stdout, codename)
    if not stanza:
        log.warning("Could not derive a -proposed stanza; skipping -proposed enable")
        return

    proposed_path = "/etc/apt/sources.list.d/auto-mir-proposed.sources"
    _lxc("exec", name, "--", "tee", proposed_path, capture=True, input=stanza)
    log.info("Enabled %s-proposed pocket for source fetch and build", codename)


def _build_proposed_stanza(ubuntu_sources: str, codename: str) -> str | None:
    """Return a deb822 stanza enabling ``<codename>-proposed`` (deb + deb-src).

    Reuses the primary archive stanza from ``ubuntu.sources`` (the one whose
    Suites reference the release codename, not the security archive) and rewrites
    its Suites to ``<codename>-proposed`` and Types to include deb-src.
    """
    # Split the deb822 file into blank-line-separated stanzas.
    stanzas = [s for s in re.split(r"\n\s*\n", ubuntu_sources) if s.strip()]
    primary = None
    for stanza in stanzas:
        suites = ""
        for line in stanza.splitlines():
            if line.lower().startswith("suites:"):
                suites = line.split(":", 1)[1]
                break
        # The primary stanza carries the plain release suite (codename) and is
        # not the security-only archive.
        if codename in suites and "security" not in suites.lower():
            primary = stanza
            break
    if primary is None:
        return None

    out_lines: list[str] = []
    for line in primary.splitlines():
        low = line.lower()
        if low.startswith("types:"):
            out_lines.append("Types: deb deb-src")
        elif low.startswith("suites:"):
            out_lines.append(f"Suites: {codename}-proposed")
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def _bootstrap_archive_tools(name: str, pin_commit: str | None) -> None:
    """Clone ubuntu-archive-tools at the requested revision."""
    log.info(
        "Bootstrapping ubuntu-archive-tools (%s)",
        f"pinned to {pin_commit}" if pin_commit else "latest HEAD",
    )
    exec_in_retry(
        name,
        ["git", "clone", "--depth=1", _ARCHIVE_TOOLS_REPO, _ARCHIVE_TOOLS_DIR],
        operation="clone ubuntu-archive-tools",
    )
    if pin_commit:
        # Deepen clone just enough to reach the pinned commit, then check it out.
        exec_in_retry(
            name,
            [
                "git",
                "-C",
                _ARCHIVE_TOOLS_DIR,
                "fetch",
                "--depth=1",
                "origin",
                pin_commit,
            ],
            check=False,  # May fail on shallow; fallback path below handles it
            operation="fetch pinned ubuntu-archive-tools commit",
        )
        result = exec_in(
            name,
            ["git", "-C", _ARCHIVE_TOOLS_DIR, "checkout", pin_commit],
            check=False,
            capture=True,
        )
        if result.returncode != 0:
            # Shallow clone may not have the commit; do a full unshallow fetch
            log.debug("Shallow fetch missed commit; unshallowing")
            exec_in_retry(
                name,
                ["git", "-C", _ARCHIVE_TOOLS_DIR, "fetch", "--unshallow", "origin"],
                operation="unshallow ubuntu-archive-tools",
            )
            exec_in_retry(
                name,
                ["git", "-C", _ARCHIVE_TOOLS_DIR, "checkout", pin_commit],
                operation="checkout pinned ubuntu-archive-tools commit",
            )
        log.info("Pinned ubuntu-archive-tools to %s", pin_commit)
    else:
        log.info("Using latest ubuntu-archive-tools HEAD")


def exec_in(
    name: str,
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
    workdir: str | None = None,
    user: int | None = None,
    group: int | None = None,
) -> subprocess.CompletedProcess:
    """Run a command inside the named LXD guest.

    Args:
        name: LXD guest name
        cmd: Command and arguments to run in the guest
        check: Raise CalledProcessError on non-zero exit
        capture: Capture stdout/stderr and return them
        env: Additional environment variables to pass (merged with guest env)
        workdir: Working directory inside the guest
        user: Optional numeric uid to run the command as
        group: Optional numeric gid to run the command as

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    lxc_cmd = ["lxc", "exec", name]

    if workdir:
        lxc_cmd += ["--cwd", workdir]

    if user is not None:
        lxc_cmd += ["--user", str(user)]

    if group is not None:
        lxc_cmd += ["--group", str(group)]

    if env:
        for key, value in env.items():
            lxc_cmd += ["--env", f"{key}={value}"]

    lxc_cmd += ["--"] + cmd

    return run_command(lxc_cmd, log_prefix=f"guest({name})", check=check, capture=capture)


@retry_guest_command(max_attempts=4, base_delay=6.0, max_delay=60.0)
def _exec_in_retry_internal(
    name: str,
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    workdir: str | None = None,
    user: int | None = None,
    group: int | None = None,
) -> subprocess.CompletedProcess:
    """Internal function that executes with retry logic.

    This function is decorated with tenacity retry and will automatically
    retry on transient failures (503 errors, DNS failures, connection timeouts).
    """
    return exec_in(
        name,
        cmd,
        check=False,
        capture=True,
        env=env,
        workdir=workdir,
        user=user,
        group=group,
    )


def exec_in_retry(
    name: str,
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
    workdir: str | None = None,
    user: int | None = None,
    group: int | None = None,
    operation: str = "command",
) -> subprocess.CompletedProcess:
    """Run an in-guest command with retries on transient failures.

    Intended for network/server-sensitive steps (apt, git clone/fetch, source
    downloads). Retries are attempted only when stderr/stdout indicate transient
    infrastructure issues (503, temporary DNS/connection errors, timeouts).

    Args:
        name: LXD guest name
        cmd: Command to execute
        check: Raise exception on non-zero exit (after retries exhausted)
        capture: Capture stdout/stderr
        env: Environment variables
        workdir: Working directory
        user: Optional numeric uid to run the command as
        group: Optional numeric gid to run the command as
        operation: Operation name for logging

    Returns:
        CompletedProcess result

    Raises:
        RuntimeError: If command fails after all retries (when check=True)
    """
    result = _exec_in_retry_internal(
        name,
        cmd,
        env=env,
        workdir=workdir,
        user=user,
        group=group,
    )

    if result.returncode != 0 and not check:
        # Caller doesn't want exceptions, just return the result
        return result

    if result.returncode != 0:
        # Retries exhausted and check=True, raise error
        transient = is_transient_command_failure(result.stdout, result.stderr)
        hint = (
            "\nHard stop: command failed after retries due to non-transient error."
            if not transient
            else ("\nHard stop: transient upstream/server issue did not recover after retries.")
        )
        raise RuntimeError(
            f"{operation} failed (exit {result.returncode})."
            f"\nCommand: {shlex.join(cmd)}"
            f"\nstdout:\n{(result.stdout or '').strip()}"
            f"\nstderr:\n{(result.stderr or '').strip()}"
            f"{hint}"
        )

    # Success - if capture was False, clear the output
    if not capture:
        result.stdout = None
        result.stderr = None

    return result


def push_file(name: str, local_path: str, guest_path: str) -> None:
    """Copy a file from the host into the LXD guest."""
    log.debug("push %s -> %s:%s", local_path, name, guest_path)
    _lxc("file", "push", local_path, f"{name}{guest_path}")


def pull_file(name: str, guest_path: str, local_path: str) -> None:
    """Copy a file from the LXD guest to the host."""
    log.debug("pull %s:%s -> %s", name, guest_path, local_path)
    _lxc("file", "pull", f"{name}{guest_path}", local_path)


def destroy(ctx: "RunContext") -> None:
    """Destroy the LXD guest unconditionally."""
    if not ctx.guest_name:
        return
    log.info("Destroying LXD guest %s", ctx.guest_name)
    result = _lxc("delete", "--force", ctx.guest_name, check=False, capture=True)
    if result.returncode != 0:
        log.warning(
            "Could not destroy LXD guest %s: %s",
            ctx.guest_name,
            result.stderr.strip(),
        )
    else:
        log.info("LXD guest %s destroyed", ctx.guest_name)
        ctx.guest_name = ""


def collect_runtime_facts(ctx: "RunContext") -> dict:
    """Collect core in-guest facts proving isolated execution context."""
    if not ctx.guest_name:
        return {}

    os_release = exec_in(
        ctx.guest_name,
        ["bash", "-lc", "cat /etc/os-release"],
        capture=True,
        check=False,
    ).stdout.strip()

    kernel = exec_in(
        ctx.guest_name,
        ["uname", "-a"],
        capture=True,
        check=False,
    ).stdout.strip()

    apt_policy = exec_in(
        ctx.guest_name,
        ["bash", "-lc", "apt-cache policy | sed -n '1,40p'"],
        capture=True,
        check=False,
    ).stdout.strip()

    return {
        "guest_name": ctx.guest_name,
        "image": getattr(ctx, "lxd_image", None),
        "os_release": os_release,
        "kernel": kernel,
        "apt_policy_excerpt": apt_policy,
    }
