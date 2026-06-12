from typing import Callable, Any
from models import Finding

EVALUATORS: dict[str, Callable[[dict, Any, Finding], Finding]] = {}
DETERMINISTIC_CHECKS: dict[str, Callable[[Any, Finding], Finding]] = {}


def evaluator(mode: str) -> Callable:
    def decorator(
        func: Callable[[dict, Any, Finding], Finding],
    ) -> Callable[[dict, Any, Finding], Finding]:
        EVALUATORS[mode] = func
        return func

    return decorator


def deterministic_check(check_id: str) -> Callable:
    def decorator(func: Callable[[Any, Finding], Finding]) -> Callable[[Any, Finding], Finding]:
        DETERMINISTIC_CHECKS[check_id] = func
        return func

    return decorator
