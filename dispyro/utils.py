from functools import wraps
from typing import Any, Callable, Dict, TypeVar

ReturnType = TypeVar("ReturnType")


def get_needed_kwargs(callable: Callable, **kwargs) -> Dict[str, Any]:
    """Helper function fetches needed `kwargs`.
    Returns only needed kwargs in a form of a `dict`.
    """

    if not getattr(callable, "__code__", None):
        # treating `callable` as non-function object with __call__ defined
        callable = callable.__call__

    # using internals to check needed arguments
    varnames: tuple[str, ...] = callable.__code__.co_varnames
    needed_kwargs = {k: v for k, v in kwargs.items() if k in varnames}

    return needed_kwargs


def safe_call(callable: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    """Helper function that makes new `callable` which feeds only needed `kwargs` to original."""

    @wraps(callable)
    def wrapper(*args, **kwargs) -> ReturnType:
        needed_kwargs = get_needed_kwargs(callable=callable, **kwargs)
        return callable(*args, **needed_kwargs)

    return wrapper
