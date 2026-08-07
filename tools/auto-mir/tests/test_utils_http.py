"""Unit tests for shared HTTP helpers."""

import io
import sys
import urllib.error
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


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_check_url_exists_returns_false_for_empty_url():
    with patch("utils.http.urllib.request.urlopen") as fake_urlopen:
        assert http.check_url_exists("") is False
    fake_urlopen.assert_not_called()


def test_check_url_exists_true_on_successful_head():
    with patch(
        "utils.http.urllib.request.urlopen",
        return_value=_FakeResponse(b""),
    ) as fake_urlopen:
        assert http.check_url_exists("https://example.test/project") is True
    request = fake_urlopen.call_args[0][0]
    assert request.get_method() == "HEAD"


def test_check_url_exists_false_on_404():
    def _fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    with patch("utils.http.urllib.request.urlopen", _fake_urlopen):
        assert http.check_url_exists("https://example.test/gone") is False


def test_check_url_exists_falls_back_to_get_on_405():
    calls = []

    def _fake_urlopen(req, timeout=None):
        calls.append(req.get_method())
        if req.get_method() == "HEAD":
            raise urllib.error.HTTPError(req.full_url, 405, "Method Not Allowed", {}, None)
        return _FakeResponse(b"ok")

    with patch("utils.http.urllib.request.urlopen", _fake_urlopen):
        assert http.check_url_exists("https://example.test/head-blocked") is True
    assert calls == ["HEAD", "GET"]


def test_check_url_exists_false_on_timeout():
    def _fake_urlopen(req, timeout=None):
        raise TimeoutError("timed out")

    with patch("utils.http.urllib.request.urlopen", _fake_urlopen):
        assert http.check_url_exists("https://example.test/slow") is False


def test_check_url_exists_false_on_url_error():
    def _fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("no route to host")

    with patch("utils.http.urllib.request.urlopen", _fake_urlopen):
        assert http.check_url_exists("https://example.test/unreachable") is False
