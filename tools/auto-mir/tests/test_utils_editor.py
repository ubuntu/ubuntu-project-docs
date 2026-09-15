"""Tests for utils/editor.py: external editor resolution and invocation."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from utils import editor  # noqa: E402


def test_resolve_editor_command_prefers_visual(monkeypatch):
    monkeypatch.setenv("VISUAL", "code --wait")
    monkeypatch.setenv("EDITOR", "vim")

    assert editor.resolve_editor_command() == ["code", "--wait"]


def test_resolve_editor_command_falls_back_to_editor_env(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "vim -f")

    assert editor.resolve_editor_command() == ["vim", "-f"]


def test_resolve_editor_command_falls_back_to_usr_bin_editor(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)

    with patch.object(editor.Path, "exists", return_value=True):
        assert editor.resolve_editor_command() == ["/usr/bin/editor"]


def test_resolve_editor_command_falls_back_to_nano(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)

    with patch.object(editor.Path, "exists", return_value=False):
        assert editor.resolve_editor_command() == ["nano"]


def test_edit_text_returns_none_without_interactive_terminal(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    assert editor.edit_text("hello", ["a comment"]) is None


def test_edit_text_strips_comment_lines_and_returns_edited_body(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("EDITOR", "fake-editor")

    def _fake_run(command, check=False):
        assert command[0] == "fake-editor"
        temp_path = Path(command[-1])
        temp_path.write_text("revised text\nsecond line\n# a comment\n#\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    with patch("utils.editor.subprocess.run", side_effect=_fake_run):
        result = editor.edit_text("original text", ["a comment"])

    assert result == "revised text\nsecond line"


def test_edit_text_prepopulates_initial_text_and_comment_lines(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("EDITOR", "fake-editor")
    seen_contents = []

    def _fake_run(command, check=False):
        temp_path = Path(command[-1])
        seen_contents.append(temp_path.read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(command, 0)

    with patch("utils.editor.subprocess.run", side_effect=_fake_run):
        editor.edit_text("prefilled body", ["Context: some rule", "Hint: some hint"])

    assert seen_contents[0].startswith("prefilled body\n\n")
    assert "# Context: some rule" in seen_contents[0]
    assert "# Hint: some hint" in seen_contents[0]


def test_edit_text_returns_none_on_nonzero_exit(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("EDITOR", "fake-editor")

    with patch("utils.editor.subprocess.run", return_value=subprocess.CompletedProcess([], 1)):
        assert editor.edit_text("", []) is None


def test_edit_text_returns_none_when_editor_binary_missing(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("EDITOR", "no-such-editor-binary")

    with patch("utils.editor.subprocess.run", side_effect=FileNotFoundError("not found")):
        assert editor.edit_text("", []) is None
