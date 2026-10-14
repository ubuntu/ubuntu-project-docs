"""llm_sanitize.py — spotlighting helpers for untrusted LLM input.

Launchpad bug text (description, title, comments) is attacker-controllable:
anyone with a Launchpad account can post content that later becomes part of an
LLM prompt. That makes it an attack surface for prompt-injection.

This module implements lightweight "spotlighting" — the standard, dependency-free
process for reducing prompt-injection risk:

- ``scan_for_injection`` detects instruction-like patterns (read-only) so the
  intake stage can warn the reviewer and gate the run.
- ``neutralize`` defangs role markers and special tokens and strips control
  characters so untrusted text cannot easily forge chat structure.
- ``wrap_untrusted`` wraps untrusted text in a per-run, nonce'd envelope so the
  model can reliably tell data from instructions and cannot forge the closing
  delimiter.

There is no complete defence against prompt injection. These measures lower the
likelihood and impact; the final, authoritative safeguard remains the mandatory
human review of the generated draft. See ``decisions.md`` for the rationale and
the accepted residual risk.
"""

from __future__ import annotations

import re
import secrets

# Patterns that indicate an attempt to instruct the model rather than provide
# data. Matched case-insensitively. The labels are surfaced to the reviewer, so
# keep them short and descriptive.
_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "override-instructions",
        re.compile(
            r"\b(ignore|disregard|forget|override)\b.{0,40}\b"
            r"(previous|prior|above|earlier|all)\b.{0,20}"
            r"(instruction|prompt|context|rule|direction)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "system-prompt-reference",
        re.compile(r"\b(system|developer)\s+(prompt|message|instruction)", re.IGNORECASE),
    ),
    (
        "reveal-instructions",
        re.compile(
            r"\b(reveal|print|repeat|show|output|disclose|leak)\b.{0,30}"
            r"(prompt|instruction|system message|your rules)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "role-reassignment",
        re.compile(
            r"\byou\s+are\s+now\b|\bact\s+as\b|\bpretend\s+to\s+be\b|"
            r"\bfrom\s+now\s+on\b|\bnew\s+instructions?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "chat-role-marker",
        re.compile(r"(?im)^\s*(system|assistant|developer|user)\s*:"),
    ),
    (
        "special-token",
        re.compile(
            r"<\|.*?\|>|<\s*/?\s*(system|assistant|user|im_start|im_end)\s*>", re.IGNORECASE
        ),
    ),
    (
        "verdict-steering",
        re.compile(
            r"\b(approve|ack|pass|mark)\b.{0,30}\b(mir|review|this)\b|"
            r"\bset\s+(status|severity|confidence)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "untrusted-envelope-spoof",
        re.compile(r"END_UNTRUSTED_DATA|BEGIN_UNTRUSTED_DATA|UNTRUSTED_DATA", re.IGNORECASE),
    ),
]

# Control characters except tab (\t), newline (\n) and carriage return (\r).
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Role markers at the start of a line are defanged by inserting a zero-width
# breaker; special tokens are escaped so they cannot be interpreted as control
# tokens by the model's tokenizer.
_LINE_ROLE_MARKER = re.compile(r"(?im)^(\s*)(system|assistant|developer|user)(\s*):")
_SPECIAL_TOKEN = re.compile(r"<\|(.*?)\|>")

# Zero-width space used to break up chat-protocol tokens while keeping the text
# human-readable.
_ZWSP = "\u200b"


def make_nonce() -> str:
    """Return a short random nonce for delimiting an untrusted envelope."""
    return secrets.token_hex(8)


def _snippet(text: str, start: int, end: int, context: int = 30) -> str:
    """Return a one-line excerpt of ``text[start:end]`` with surrounding context.

    The matched span is wrapped in ``»…«`` markers so the reviewer can see what
    triggered the indicator. The original line breaks within the excerpt are
    preserved, and the excerpt is bounded so the warning stays readable.
    """
    lead = text[max(0, start - context) : start]
    match = text[start:end]
    trail = text[end : end + context]
    prefix = "…" if start - context > 0 else ""
    suffix = "…" if end + context < len(text) else ""
    return f"{prefix}{lead}»{match}«{trail}{suffix}"


def scan_for_injection_matches(text: str) -> list[tuple[str, str]]:
    """Return ``(label, snippet)`` pairs for each injection pattern found.

    Like :func:`scan_for_injection`, but also reports the matched text (with a
    little surrounding context) so callers can show the reviewer *what* tripped
    each indicator. Read-only; never mutates input. At most one snippet per
    label is returned (the first match), and the result is sorted by label.
    """
    if not text:
        return []
    matches: dict[str, str] = {}
    for label, pattern in _INJECTION_PATTERNS:
        if label in matches:
            continue
        found = pattern.search(text)
        if found:
            matches[label] = _snippet(text, found.start(), found.end())
    return sorted(matches.items())


def neutralize(text: str) -> str:
    """Return ``text`` with chat structure defanged for safe prompt embedding.

    - Strips control characters that could confuse the model or terminal.
    - Defangs leading role markers (``System:``) so they cannot mimic turns.
    - Escapes ``<|...|>`` special tokens so they are read literally.

    Content/meaning is preserved as far as practical; this only disrupts tokens
    that carry chat-protocol significance.
    """
    if not text:
        return ""
    cleaned = _CONTROL_CHARS.sub("", text)
    cleaned = _LINE_ROLE_MARKER.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}{_ZWSP}:", cleaned
    )
    cleaned = _SPECIAL_TOKEN.sub(lambda m: f"<{_ZWSP}|{m.group(1)}|{_ZWSP}>", cleaned)
    return cleaned


def wrap_untrusted(label: str, text: str, nonce: str) -> str:
    """Wrap ``text`` in a nonce'd untrusted-data envelope.

    The model is instructed (via the system prompt) to treat everything between
    the delimiters as data only. The per-run ``nonce`` is included in both
    delimiters so injected content cannot forge a convincing closing marker to
    "escape" the envelope. ``text`` is neutralized before wrapping.
    """
    safe = neutralize(text or "")
    open_tag = f"<<UNTRUSTED_DATA nonce={nonce} label={label}>>"
    close_tag = f"<<END_UNTRUSTED_DATA nonce={nonce}>>"
    return f"{open_tag}\n{safe}\n{close_tag}"
