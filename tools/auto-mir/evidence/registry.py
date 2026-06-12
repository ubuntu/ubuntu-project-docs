from typing import Any, Callable

from catalog_enums import AdapterID

# Mapping from string adapter ID to a tuple of (collector_function, list_of_dependencies)
ADAPTER_REGISTRY: dict[str, tuple[Callable[[Any], dict[str, Any]], list[str]]] = {}


def adapter(adapter_id: AdapterID, depends_on: list[AdapterID] | None = None) -> Callable:
    """Decorator to register an evidence adapter and its dependencies."""
    if depends_on is None:
        depends_on = []

    def decorator(func: Callable[[Any], dict[str, Any]]) -> Callable[[Any], dict[str, Any]]:
        id_str = str(adapter_id)
        deps_str = [str(dep) for dep in depends_on]
        ADAPTER_REGISTRY[id_str] = (func, deps_str)
        return func

    return decorator
