"""Component registry — maps registered class names to FactorNode subclasses.

The `.circuitry` deserialiser looks up component classes by name in this
registry rather than importing arbitrary modules at runtime.  This is
the framework's security boundary: a malicious or accidental
`.circuitry` file can only construct classes that have been explicitly
registered at import time by the codebase itself.  No `eval`,
`importlib.import_module`, or pickle-style arbitrary-code surface.

Convention: every concrete FactorNode subclass that may appear in a
`.circuitry` file decorates itself with `@register("ClassName")`
(bare class name).  Uniqueness is checked at registration; collisions
raise at import time.
"""
from __future__ import annotations

from typing import Callable, TypeVar

from framework.factor import FactorNode

T = TypeVar('T', bound=FactorNode)

_REGISTRY: dict[str, type[FactorNode]] = {}


def register(name: str) -> Callable[[type[T]], type[T]]:
    """Class decorator: register a FactorNode subclass under `name`.

    Names must be unique across the codebase.  Use the bare class name
    by convention.
    """
    def decorator(cls: type[T]) -> type[T]:
        if name in _REGISTRY and _REGISTRY[name] is not cls:
            raise ValueError(
                f"Component name {name!r} already registered to "
                f"{_REGISTRY[name].__module__}.{_REGISTRY[name].__qualname__}"
            )
        _REGISTRY[name] = cls
        return cls
    return decorator


def lookup(name: str) -> type[FactorNode]:
    """Look up a component class by registered name.  Used by the
    `.circuitry` loader.  Raises KeyError if the name is unknown."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown component type {name!r}; not in the registry. "
            f"Known types: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]


def registered_names() -> list[str]:
    """Sorted list of every registered component name.

    Used by the format schema to build the discriminated-union of
    component records.
    """
    return sorted(_REGISTRY)


def is_registered(cls: type[FactorNode]) -> bool:
    """True if `cls` (or one of its parents) is in the registry."""
    return cls in _REGISTRY.values()
