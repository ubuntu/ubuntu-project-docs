"""Message template rendering helpers for check evaluators.

Templates are declared in catalog entries under ``checks[].messages`` and
rendered by evaluators with strict ``str.format`` substitution.
"""

from __future__ import annotations


def render_check_message(check: dict, key: str, **kwargs) -> str:
    """Render ``checks[].messages[key]`` with strict ``str.format``.

    Raises:
        ValueError: if the check has no messages map, the key is missing,
            or required placeholders are not provided.
    """
    check_id = check.get("id", "<unknown>")
    messages = check.get("messages")
    if not isinstance(messages, dict):
        raise ValueError(f"Check {check_id} does not define a messages map")

    template = messages.get(key)
    if not isinstance(template, str):
        raise ValueError(f"Check {check_id} is missing required message template: {key}")

    try:
        return template.format(**kwargs)
    except KeyError as exc:
        missing = exc.args[0]
        raise ValueError(
            f"Check {check_id} template '{key}' is missing placeholder value: {missing}"
        ) from exc
    except ValueError as exc:
        raise ValueError(f"Check {check_id} template '{key}' format error: {exc}") from exc


def render_check_message_or_default(check: dict, key: str, default: str, **kwargs) -> str:
    """Render message template when a messages map exists, else return default.

    This enables phased migration without changing behavior for checks that are
    not migrated yet. If a messages map exists, rendering is strict.
    """
    messages = check.get("messages")
    if messages is None:
        return default
    return render_check_message(check, key, **kwargs)
