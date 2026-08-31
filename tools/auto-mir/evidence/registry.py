from typing import Any, Callable

# Mapping from string adapter ID to its collector function. Dependency wiring
# is catalog-authoritative (see evidence._catalog_adapter_dependencies); this
# registry only associates an adapter ID with the function that collects it.
ADAPTER_REGISTRY: dict[str, Callable[[Any], dict[str, Any]]] = {}


def adapter(adapter_id: str) -> Callable:
    """Decorator to register an evidence adapter's collector function."""

    def decorator(func: Callable[[Any], dict[str, Any]]) -> Callable[[Any], dict[str, Any]]:
        ADAPTER_REGISTRY[str(adapter_id)] = func
        return func

    return decorator
