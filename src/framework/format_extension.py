"""Helpers for the generic-fallback save/load path.

A class that wants to roundtrip through `.circuitry` without a
dedicated record declares two things on itself:

    @register('MyClass')
    class MyClass(Chip):
        SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('threshold', 'domain')

`SERIALIZE_KWARGS` lists the keyword arguments that must be supplied
when the loader reconstructs an instance.  The save path reads each
value from the instance — by default looking up `_<kwarg>` (matching
the established `__slots__` convention), falling back to `<kwarg>`,
and finally to any public property of the same name.  Each value is
then encoded through the registered codec for its Python type.

`refdes_number` is implicit: classes inheriting from `RefdesBearing`
always get their refdes-number serialised, regardless of whether
it appears in `SERIALIZE_KWARGS`.
"""
from __future__ import annotations

from typing import Any, ClassVar, get_type_hints

from framework.factor import FactorNode
from framework.ground import GroundDomain


# Marker for "no value found by any introspection strategy"; lets us
# distinguish "kwarg deliberately set to None" from "kwarg missing".
_MISSING = object()


def serialize_kwargs(instance: FactorNode) -> dict[str, Any]:
    """Read the SERIALIZE_KWARGS values back off a live instance and
    encode each for JSON storage.

    Lookup order for each kwarg name `k`:
        1. `instance._<k>`   (slots convention used throughout the
                              codebase; matches the `__init__` save)
        2. `instance.<k>`    (occasional public-attribute fallback)
        3. `getattr(instance, k)` raises — re-raise with a clearer
                                  message that names the offending
                                  class.

    Values are encoded by Python type:
        - int / float / bool / str: as-is.
        - GroundDomain: by its `.name`.
        - tuple / list of str: as a list of strings.
        - Other types: raise; only the listed kinds are supported.

    Lists / tuples of strings cover the only collection kwarg in the
    codebase today (DiodeOR's `input_names`).  Extend here when a
    new collection type shows up.
    """
    kwarg_names: tuple[str, ...] = getattr(type(instance), 'SERIALIZE_KWARGS', ())
    out: dict[str, Any] = {}
    for name in kwarg_names:
        value = _read_kwarg(instance, name)
        out[name] = _encode_value(value, owner_class=type(instance), kwarg_name=name)
    return out


def deserialize_kwargs(
    cls: type[FactorNode],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Decode the kwargs payload back into Python values suitable for
    passing to `cls(**kwargs)`.

    Uses `typing.get_type_hints(cls.__init__)` to determine what type
    each kwarg should be, so a `name: str` payload can be reconstructed
    into a `GroundDomain` (or whatever else) without the record
    schema needing per-class hints.
    """
    try:
        hints = get_type_hints(cls.__init__)
    except Exception:
        hints = {}
    out: dict[str, Any] = {}
    for name, raw in payload.items():
        out[name] = _decode_value(raw, hints.get(name))
    return out


# ---------------------------------------------------------------- helpers

def _read_kwarg(instance: FactorNode, name: str) -> Any:
    """Find the live value of `name` on `instance`.  See module
    docstring for the lookup order.

    Classes whose internal attribute name differs from the kwarg
    name (e.g. `BackupSupervisor` storing `bulk_capacitance_uf` as
    `_bulk_uf`) declare an explicit mapping via
    `_SERIALIZE_ATTRS: ClassVar[dict[str, str]]` — kwarg name →
    attribute name.  Checked first; the default lookups fall through
    after."""
    sentinel = _MISSING
    overrides: dict[str, str] = getattr(type(instance), '_SERIALIZE_ATTRS', {})
    if name in overrides:
        return getattr(instance, overrides[name])
    value = getattr(instance, f'_{name}', sentinel)
    if value is not sentinel:
        return value
    value = getattr(instance, name, sentinel)
    if value is not sentinel:
        return value
    raise AttributeError(
        f"{type(instance).__name__} declares {name!r} as a "
        f"SERIALIZE_KWARGS but has no `_{name}`, `{name}`, or property "
        f"of that name to read it back from.  Either add the "
        f"attribute, or declare `_SERIALIZE_ATTRS = "
        f"{{'{name}': '_actual_attr_name'}}` on the class."
    )


def _encode_value(value: Any, *, owner_class: type, kwarg_name: str) -> Any:
    if isinstance(value, bool):           # bool BEFORE int (bool is an int subclass)
        return value
    if isinstance(value, (int, float, str)):
        return value
    if isinstance(value, GroundDomain):
        return value.name
    if isinstance(value, (tuple, list)):
        items = list(value)
        if all(isinstance(x, str) for x in items):
            return items
    if value is None:
        return None
    raise TypeError(
        f"Cannot serialise {owner_class.__name__}.{kwarg_name} = "
        f"{value!r} (type {type(value).__name__}); supported types are "
        f"int, float, bool, str, GroundDomain, and list/tuple[str]"
    )


def _decode_value(raw: Any, hint: type | None) -> Any:
    """Reverse of `_encode_value`.  The annotation `hint` tells us what
    to reconstruct; if absent we pass through the raw JSON value."""
    if hint is GroundDomain and isinstance(raw, str):
        return GroundDomain(raw)
    return raw
