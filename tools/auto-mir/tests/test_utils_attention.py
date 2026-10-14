"""Tests for idle-attention alerts (utils/attention.py)."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.attention import AttentionAlerter, make_alerter  # noqa: E402


class RecordingAlerter:
    """Duck-typed stand-in recording the alert lifecycle."""

    def __init__(self):
        self.started: list[tuple[object, str]] = []
        self.cancelled: list[object] = []
        self.rings: list[str] = []

    def start(self, message):
        handle = object()
        self.started.append((handle, message))
        return handle

    def cancel(self, handle):
        self.cancelled.append(handle)

    def ring(self, message):
        self.rings.append(message)


def test_alerter_fires_bell_and_notification_after_the_idle_delay():
    bells: list[int] = []
    notes: list[tuple[str, str]] = []
    alerter = AttentionAlerter(
        bell=lambda: bells.append(1),
        notify=lambda summary, body: notes.append((summary, body)),
        first_delay=0.05,
        repeat_delay=60.0,
    )

    handle = alerter.start("Why is it needed?")
    time.sleep(0.25)
    alerter.cancel(handle)

    assert bells == [1]
    assert notes == [("auto-mir needs input", "Why is it needed?")]


def test_alerter_stays_silent_when_input_arrives_in_time():
    bells: list[int] = []
    alerter = AttentionAlerter(
        bell=lambda: bells.append(1), notify=lambda *_args: None, first_delay=0.5
    )

    handle = alerter.start("Why is it needed?")
    alerter.cancel(handle)
    time.sleep(0.7)

    assert bells == []


def test_alerter_repeats_the_bell_while_input_is_still_missing():
    bells: list[int] = []
    notes: list[tuple[str, str]] = []
    alerter = AttentionAlerter(
        bell=lambda: bells.append(1),
        notify=lambda summary, body: notes.append((summary, body)),
        first_delay=0.02,
        repeat_delay=0.05,
    )

    handle = alerter.start("Why is it needed?")
    time.sleep(0.3)
    alerter.cancel(handle)

    assert len(bells) >= 2
    # The desktop notification fires once per wait; only the bell repeats.
    assert notes == [("auto-mir needs input", "Why is it needed?")]


def test_alerter_ring_raises_an_immediate_alert():
    bells: list[int] = []
    notes: list[tuple[str, str]] = []
    alerter = AttentionAlerter(
        bell=lambda: bells.append(1),
        notify=lambda summary, body: notes.append((summary, body)),
    )

    alerter.ring("Preparation finished - 12 questions ready")

    assert bells == [1]
    assert notes == [("auto-mir", "Preparation finished - 12 questions ready")]


def test_alerter_swallows_a_failing_notification_daemon():
    bells: list[int] = []

    def _explode(_summary, _body):
        raise OSError("no notification daemon")

    alerter = AttentionAlerter(
        bell=lambda: bells.append(1), notify=_explode, first_delay=0.05, repeat_delay=60.0
    )

    handle = alerter.start("Why is it needed?")
    time.sleep(0.2)
    alerter.cancel(handle)

    assert bells == [1]  # the bell still rang; the failure was swallowed


def test_alerter_truncates_long_notification_bodies():
    notes: list[tuple[str, str]] = []
    alerter = AttentionAlerter(
        bell=lambda: None, notify=lambda summary, body: notes.append((summary, body))
    )

    alerter.ring("x" * 500)

    assert len(notes[0][1]) == 120


def test_make_alerter_is_disabled_by_flag_or_missing_terminal(monkeypatch):
    assert make_alerter(alerts_enabled=False) is None

    # A piped/headless session must not raise bells into a pipe.
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert make_alerter(alerts_enabled=True) is None

    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert isinstance(make_alerter(alerts_enabled=True), AttentionAlerter)
