"""Credential redaction for logs and shareable Auto-MIR artifacts."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

_REDACTION_MARKER = "[REDACTED]"


class SecretRedactor:
    """Redact exact runtime secret values without provider-specific guesses.

    Secrets must be registered when they are resolved. Exact-value matching keeps
    public package and MIR evidence intact while supporting arbitrary current and
    future credential formats.
    """

    def __init__(self) -> None:
        self._secrets: set[str] = set()

    def register(self, value: str | None) -> None:
        """Register a non-empty secret value for subsequent redaction."""
        if value:
            self._secrets.add(value)

    def redact_text(self, value: str) -> str:
        """Replace every registered secret embedded in *value*."""
        redacted = value
        for secret in sorted(self._secrets, key=len, reverse=True):
            redacted = redacted.replace(secret, _REDACTION_MARKER)
        return redacted

    def sanitize(self, value: Any) -> Any:
        """Return a recursively redacted copy of JSON-compatible data."""
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, Mapping):
            return {self.sanitize(key): self.sanitize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.sanitize(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self.sanitize(item) for item in value)
        if isinstance(value, set):
            return {self.sanitize(item) for item in value}
        return value


def ensure_secret_redactor(ctx: Any, logger: logging.Logger | None = None) -> SecretRedactor:
    """Return a context-bound redactor, creating one if needed.

    Some code paths may operate on partially-populated context-like objects
    (for example tests or legacy serialized state). To keep redaction best-effort
    and avoid hard failures during rendering, ensure a usable redactor exists.
    """
    redactor = getattr(ctx, "secret_redactor", None)
    if isinstance(redactor, SecretRedactor):
        return redactor

    redactor = SecretRedactor()
    try:
        setattr(ctx, "secret_redactor", redactor)
    except Exception:
        # If the context is immutable, continue with an unbound redactor.
        pass

    if logger is not None:
        logger.warning(
            "Context %s missing valid secret_redactor; using a fallback redactor",
            type(ctx).__name__,
        )
    return redactor


class RedactingFormatter(logging.Formatter):
    """Apply exact-value redaction after another formatter has rendered a record."""

    def __init__(self, formatter: logging.Formatter, redactor: SecretRedactor) -> None:
        super().__init__()
        self._formatter = formatter
        self._redactor = redactor

    def format(self, record: logging.LogRecord) -> str:
        """Format normally, then redact messages, arguments, and tracebacks."""
        return self._redactor.redact_text(self._formatter.format(record))
