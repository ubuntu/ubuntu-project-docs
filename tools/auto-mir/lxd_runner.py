"""lxd_runner.py — LXD container lifecycle for auto-mir.

The tool is host-orchestrated: this module creates a fresh LXD container
from Ubuntu devel images, provisions tooling in-container, dispatches
commands there, and handles cleanup.

This is explicitly NOT meant to be run from inside an existing container.
"""

import logging
import shlex
import subprocess
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.lxd_runner")

# Preferred Ubuntu devel image aliases in priority order.
_UBUNTU_DEVEL_IMAGES = [
    "ubuntu-daily:devel",
    "images:ubuntu/devel",
    "ubuntu:devel",
]

# Packages required inside the container for the full pipeline.
_REQUIRED_PACKAGES = [
    "sbuild",
    "lintian",
    "git-ubuntu",
    "ubuntu-dev-tools",   # provides seeded-in-ubuntu
    "dpkg-dev",
    "apt-utils",
    "python3-launchpadlib",
    "python3-yaml",
    "curl",
    "wget",
    "git",
    "germinate",          # prerequisite for component-mismatches
    "python3-apt",
    "python3-requests",
]

# Remote for ubuntu-archive-tools
_ARCHIVE_TOOLS_REPO = "https://git.launchpad.net/ubuntu-archive-tools"
_ARCHIVE_TOOLS_DIR = "/opt/ubuntu-archive-tools"


def _run_host(cmd: list[str], check: bool = True, capture: bool = False, **kwargs):
    """Run a command on the host. Raise on failure unless check=False."""
    log.debug("host$ %s", shlex.join(cmd))
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        **kwargs,
    )
    if check and result.returncode != 0:
        log.error(
            "Command failed (exit %d): %s\nstdout: %s\nstderr: %s",
            result.returncode,
            shlex.join(cmd),
            result.stdout if capture else "(not captured)",
            result.stderr if capture else "(not captured)",
        )
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def _lxc(*args, check: bool = True, capture: bool = False, **kwargs):
    """Wrapper around lxc CLI."""
    return _run_host(["lxc"] + list(args), check=check, capture=capture, **kwargs)


def _container_name(bug_id: str) -> str:
    """Generate a deterministic, human-readable container name."""
    # Format: auto-mir-<bugid>-<timestamp-seconds>
    # Deterministic prefix allows easy identification; timestamp avoids collisions.
    ts = str(int(time.time()))
    return f"auto-mir-{bug_id}-{ts}"


def _check_lxd_available() -> None:
    """Verify lxc is available on the host; exit with guidance if not."""
    result = subprocess.run(["which", "lxc"], capture_output=True, text=True)
    if result.returncode != 0:
        log.error(
            "lxc command not found. Install LXD with: sudo snap install lxd && lxd init"
        )
        sys.exit(1)

    # Quick connectivity check
    result = _lxc("version", capture=True, check=False)
    if result.returncode != 0:
        log.error(
            "LXD is installed but not responding. Try: lxd init --auto"
        )
        sys.exit(1)
    log.debug("LXD version: %s", result.stdout.strip())


def spawn(ctx: "RunContext") -> None:
    """Create a new LXD container from Ubuntu devel and provision it.

    Populates ctx.container_name.
    """
    _check_lxd_available()

    name = _container_name(ctx.bug_id)
    ctx.container_name = name
    image = _resolve_image(ctx)
    ctx.lxd_image = image

    log.info("Creating LXD container %s from %s", name, image)
    _lxc("launch", image, name)

    # Wait for network to be available inside the container
    _wait_for_network(name)

    log.info("Provisioning container %s", name)
    _provision(name, ctx)

    log.info("Container %s is ready", name)


def _resolve_image(ctx: "RunContext") -> str:
    """Resolve the image alias to use for this run.

    If the user provided --lxd-image, use that as-is.
    Otherwise probe common Ubuntu devel aliases and choose the first available.
    """
    explicit = getattr(ctx, "lxd_image", None)
    if explicit:
        return explicit

    for alias in _UBUNTU_DEVEL_IMAGES:
        result = _lxc("image", "info", alias, check=False, capture=True)
        if result.returncode == 0:
            return alias

    log.error(
        "Could not find an Ubuntu devel LXD image. Tried: %s",
        ", ".join(_UBUNTU_DEVEL_IMAGES),
    )
    sys.exit(1)


def _wait_for_network(name: str, timeout: int = 60) -> None:
    """Wait until the container has network connectivity."""
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
                log.debug("Network available in container %s", name)
                return
        time.sleep(2)
    log.warning("Network did not become available in %s within %ds; continuing anyway", name, timeout)


def _provision(name: str, ctx: "RunContext") -> None:
    """Install required tools and bootstrap upstream tooling inside the container."""

    # Update package lists
    exec_in(name, ["apt-get", "update", "-qq"])

    # Install required packages
    log.info("Installing required packages in container")
    exec_in(
        name,
        ["apt-get", "install", "-qq", "-y", "--no-install-recommends"] + _REQUIRED_PACKAGES,
        env={"DEBIAN_FRONTEND": "noninteractive"},
    )

    # Bootstrap ubuntu-archive-tools (component-mismatches and prerequisites)
    _bootstrap_archive_tools(name, ctx.pin_uat_tooling)


def _bootstrap_archive_tools(name: str, pin_commit: str | None) -> None:
    """Clone ubuntu-archive-tools at the requested revision."""
    log.info(
        "Bootstrapping ubuntu-archive-tools (%s)",
        f"pinned to {pin_commit}" if pin_commit else "latest HEAD",
    )
    exec_in(
        name,
        ["git", "clone", "--depth=1", _ARCHIVE_TOOLS_REPO, _ARCHIVE_TOOLS_DIR],
    )
    if pin_commit:
        # Deepen clone just enough to reach the pinned commit, then check it out.
        exec_in(
            name,
            ["git", "-C", _ARCHIVE_TOOLS_DIR, "fetch", "--depth=1", "origin", pin_commit],
            check=False,  # May fail on shallow; fall back to full fetch if needed
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
            exec_in(
                name,
                ["git", "-C", _ARCHIVE_TOOLS_DIR, "fetch", "--unshallow", "origin"],
            )
            exec_in(
                name,
                ["git", "-C", _ARCHIVE_TOOLS_DIR, "checkout", pin_commit],
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
    env: dict | None = None,
    workdir: str | None = None,
) -> subprocess.CompletedProcess:
    """Run a command inside the named LXD container.

    Args:
        name: Container name
        cmd: Command and arguments to run in the container
        check: Raise CalledProcessError on non-zero exit
        capture: Capture stdout/stderr and return them
        env: Additional environment variables to pass (merged with container env)
        workdir: Working directory inside the container

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    lxc_cmd = ["lxc", "exec", name]

    if workdir:
        lxc_cmd += ["--cwd", workdir]

    if env:
        for key, value in env.items():
            lxc_cmd += ["--env", f"{key}={value}"]

    lxc_cmd += ["--"] + cmd

    log.debug("container(%s)$ %s", name, shlex.join(cmd))
    result = subprocess.run(
        lxc_cmd,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        log.error(
            "In-container command failed (exit %d): %s",
            result.returncode,
            shlex.join(cmd),
        )
        if capture:
            log.error("stdout: %s", result.stdout)
            log.error("stderr: %s", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def push_file(name: str, local_path: str, container_path: str) -> None:
    """Copy a file from the host into the container."""
    log.debug("push %s -> %s:%s", local_path, name, container_path)
    _lxc("file", "push", local_path, f"{name}{container_path}")


def pull_file(name: str, container_path: str, local_path: str) -> None:
    """Copy a file from the container to the host."""
    log.debug("pull %s:%s -> %s", name, container_path, local_path)
    _lxc("file", "pull", f"{name}{container_path}", local_path)


def destroy(ctx: "RunContext") -> None:
    """Destroy the LXD container unconditionally."""
    if not ctx.container_name:
        return
    log.info("Destroying container %s", ctx.container_name)
    result = _lxc("delete", "--force", ctx.container_name, check=False, capture=True)
    if result.returncode != 0:
        log.warning(
            "Could not destroy container %s: %s",
            ctx.container_name,
            result.stderr.strip(),
        )
    else:
        log.info("Container %s destroyed", ctx.container_name)
        ctx.container_name = ""


def collect_runtime_facts(ctx: "RunContext") -> dict:
    """Collect core in-container facts proving isolated execution context."""
    if not ctx.container_name:
        return {}

    os_release = exec_in(
        ctx.container_name,
        ["bash", "-lc", "cat /etc/os-release"],
        capture=True,
        check=False,
    ).stdout.strip()

    kernel = exec_in(
        ctx.container_name,
        ["uname", "-a"],
        capture=True,
        check=False,
    ).stdout.strip()

    apt_policy = exec_in(
        ctx.container_name,
        ["bash", "-lc", "apt-cache policy | sed -n '1,40p'"],
        capture=True,
        check=False,
    ).stdout.strip()

    return {
        "container_name": ctx.container_name,
        "image": getattr(ctx, "lxd_image", None),
        "os_release": os_release,
        "kernel": kernel,
        "apt_policy_excerpt": apt_policy,
    }
