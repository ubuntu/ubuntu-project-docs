"""Unit tests for shared HTTP helpers."""

import io
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import http


def test_default_user_agent_carries_ubuntu_prefix():
    # The ``ubuntu/`` prefix unlocks more generous rate limits on some services.
    assert http._DEFAULT_USER_AGENT == "ubuntu/auto-mir/0.1"


def test_get_bytes_sends_ubuntu_user_agent_header():
    captured = {}

    class _FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def _fake_urlopen(req, timeout=None):
        captured["user_agent"] = req.get_header("User-agent")
        return _FakeResponse(b"payload")

    with patch("utils.http.urllib.request.urlopen", _fake_urlopen):
        assert http.get_bytes("https://example.test/data") == b"payload"

    assert captured["user_agent"] == "ubuntu/auto-mir/0.1"
