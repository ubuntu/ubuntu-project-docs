"""Idle-attention alerts: terminal bell plus best-effort desktop notification.

Feedback item 1: a reporter runs the tool next to other work, so a question
that sits unanswered earns a bell after a minute of idleness - not
immediately, someone watching the screen should not be annoyed - plus a
best-effort desktop notification, so the generic "something needs
attention" sound becomes "auto-mir needs input" with the question text.
The bell repeats while input is still pending so a walk-away reporter is
reached again.

Everything here is best-effort: a missing notification daemon or a piped
output stream never disturbs the actual question flow.
"""

from __future__ import annotations

import logging
import subprocess
import sys
import threading
from typing import Callable

log = logging.getLogger("auto_mir.attention")

# A wait for input idle this long earns the first alert; the bell then
# repeats at this interval while input is still pending. The desktop
# notification fires once per wait.
IDLE_ALERT_SECONDS = 60.0
REPEAT_SECONDS = 300.0

_BELL = "\a"

# Notifications must stay short: desktop daemons truncate long bodies.
_NOTIFICATION_BODY_LIMIT = 120


class AlertHandle:
    """Cancellation token for one active alert wait."""

    def __init__(self) -> None:
        self.cancel_event = threading.Event()


class AttentionAlerter:
    """Ring the bell and raise a desktop notification when a wait goes idle.

    ``start(message)`` arms one wait and returns its handle; ``cancel`` stops
    it when the input arrived. ``ring(message)`` raises an immediate alert
    (used when a long preparation phase finishes and questions begin).
    The bell sink and notification callable are injectable so tests stay
    synchronous.
    """

    def __init__(
        self,
        *,
        bell: Callable[[], None] | None = None,
        notify: Callable[[str, str], None] | None = None,
        first_delay: float = IDLE_ALERT_SECONDS,
        repeat_delay: float = REPEAT_SECONDS,
    ) -> None:
        self._bell = bell or _default_bell
        self._notify = notify or _notify_send
        self._first_delay = first_delay
        self._repeat_delay = repeat_delay

    def start(self, message: str) -> AlertHandle:
        """Arm the idle alert for one wait for input."""
        handle = AlertHandle()
        thread = threading.Thread(target=self._wait_and_alert, args=(handle, message), daemon=True)
        thread.start()
        return handle

    def cancel(self, handle: AlertHandle) -> None:
        """Stop an armed wait (input arrived)."""
        handle.cancel_event.set()

    def ring(self, message: str) -> None:
        """Raise one immediate bell + notification."""
        self._ring_bell()
        self._deliver("auto-mir", message)

    def _wait_and_alert(self, handle: AlertHandle, message: str) -> None:
        if handle.cancel_event.wait(self._first_delay):
            return
        self._ring_bell()
        self._deliver("auto-mir needs input", message)
        while not handle.cancel_event.wait(self._repeat_delay):
            self._ring_bell()

    def _ring_bell(self) -> None:
        try:
            self._bell()
        except Exception:
            log.debug("Bell emission failed", exc_info=True)

    def _deliver(self, summary: str, body: str) -> None:
        try:
            self._notify(summary, body[:_NOTIFICATION_BODY_LIMIT])
        except Exception:
            log.debug("Desktop notification failed", exc_info=True)


def _default_bell() -> None:
    """Write the terminal bell character to the controlling stream."""
    sys.stdout.write(_BELL)
    sys.stdout.flush()


def _notify_send(summary: str, body: str) -> None:
    """Raise a freedesktop desktop notification, best-effort.

    ``notify-send`` is the standard Linux desktop hook; a missing daemon,
    a headless session, or a binary that is not installed is a normal
    condition, never an error.
    """
    subprocess.run(
        ["notify-send", "--expire-time=10000", "--", summary, body],
        check=False,
        capture_output=True,
        timeout=10,
    )


def make_alerter(*, alerts_enabled: bool) -> AttentionAlerter | None:
    """Build the runtime alerter, or ``None`` when alerts cannot work.

    ``None`` (instead of an inert object) is deliberate: the wizard and the
    recovery prompts then skip the timer entirely, so a headless run pays
    nothing and unit tests stay silent by default.
    """
    if not alerts_enabled:
        return None
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    return AttentionAlerter()
