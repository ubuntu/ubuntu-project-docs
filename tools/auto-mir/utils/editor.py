"""External editor integration for the reporter terminal wizard.

Revisits an earlier "dependency-free terminal wizard" decision (see
``decisions.md``): real reporters found raw, line-by-line multi-line terminal
entry uncomfortable to compose or revise. This module resolves the user's
preferred editor the same way ``git`` does, and lets the wizard hand off a
temp file (pre-populated with ``git rebase``-style commented-out context) for
the user to edit, instead of demanding text be typed directly at the prompt.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

_FALLBACK_EDITOR = "nano"
_UPDATE_ALTERNATIVES_EDITOR = "/usr/bin/editor"


def resolve_editor_command() -> list[str]:
    """Return the editor command to launch, in the same spirit as ``git``.

    Resolution order: ``$VISUAL``, then ``$EDITOR``, then the Debian
    update-alternatives ``/usr/bin/editor``, then a hardcoded ``nano``
    fallback so an editor is always available.
    """
    for env_var in ("VISUAL", "EDITOR"):
        value = os.environ.get(env_var, "").strip()
        if value:
            return shlex.split(value)
    if Path(_UPDATE_ALTERNATIVES_EDITOR).exists():
        return [_UPDATE_ALTERNATIVES_EDITOR]
    return [_FALLBACK_EDITOR]


def edit_text(initial_text: str, comment_lines: list[str]) -> str | None:
    """Open the resolved editor on a temp file and return the edited text.

    The temp file is pre-populated with ``initial_text`` (may be empty),
    followed by ``comment_lines`` rendered as ``#``-prefixed lines, matching
    how ``git rebase --interactive`` presents commentary alongside editable
    content. Lines still starting with ``#`` after editing are stripped back
    out and never become part of the returned text.

    Returns ``None`` if there is no usable interactive terminal, the editor
    can't be launched, or it exits with a non-zero status, so callers can
    fall back to raw terminal entry.
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None

    command = resolve_editor_command()
    body = initial_text.rstrip("\n")
    lines = [body, ""] if body else [""]
    lines.extend(f"# {line}" if line else "#" for line in comment_lines)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="auto-mir-", delete=False, encoding="utf-8"
        ) as handle:
            handle.write("\n".join(lines) + "\n")
            temp_path = Path(handle.name)

        result = subprocess.run([*command, str(temp_path)], check=False)
        if result.returncode != 0:
            return None
        edited = temp_path.read_text(encoding="utf-8")
    except OSError:
        return None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    kept = [line for line in edited.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(kept).strip()
