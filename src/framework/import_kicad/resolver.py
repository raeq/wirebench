"""KiCad part → wirebench class resolver.

Five-tier fallback (spec §6):

  1. Exact-name lookup against the registry (case-insensitive).
  2. Suffix-stripping retry (LM7805_TO220 → LM7805).
  3. libsource map (`Device.R` → Resistor).
  4. value map (`R` → Resistor) as last-resort generic lookup.
  5. Fallback to UnknownPart (default) or raise UnknownPartError
     (--strict mode).

The `UnknownPart` synthesised classes are kept in a session-level
cache keyed by `(name, pins)` so two refdes-distinct parts that
collapse to the same shape share a single class.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Trigger every component registration before resolving anything.
import components.chips        # noqa: F401
import components.connectors   # noqa: F401
import components.diodes       # noqa: F401
import components.passives     # noqa: F401
import components.relays       # noqa: F401
import components.transistors  # noqa: F401
import framework.board         # noqa: F401

from framework.chip import Chip
from framework.errors import UnknownPartError
from framework.part import Part
from framework.registry import _REGISTRY

from framework.import_kicad.part_map import (
    LIBSOURCE_MAP, SUFFIX_STRIPS, VALUE_MAP,
)
from framework.import_kicad.unknown_part import make_unknown_part_class


@dataclass(frozen=True, slots=True)
class KiCadComponent:
    """One `(comp ...)` block from a netlist, post-parsing."""
    ref:           str
    value:         str
    footprint:     str | None
    libsource_lib: str | None
    libsource_part: str | None
    pin_specs:    tuple[tuple[int, str], ...]  # (number, name) per pin


def resolve_part_class(
    comp: KiCadComponent,
    *,
    strict: bool = False,
    unknown_cache: dict[tuple[Any, ...], type[Part]] | None = None,
) -> type[Part]:
    """Return the wirebench Part subclass that matches `comp`.

    `unknown_cache` is mutated to collect synthesised UnknownPart
    classes so subsequent components that fall into the same bucket
    re-use the class rather than minting new ones per refdes.
    """
    registry_by_lowercase = {
        name.lower(): cls for name, cls in _REGISTRY.items()
    }

    # Tier 1: exact-name match against the registry.
    by_value = registry_by_lowercase.get(comp.value.lower())
    if by_value is not None:
        return by_value

    # Tier 2: strip known KiCad suffixes and retry.
    for suffix in SUFFIX_STRIPS:
        if comp.value.endswith(suffix):
            stripped = comp.value[:-len(suffix)]
            hit = registry_by_lowercase.get(stripped.lower())
            if hit is not None:
                return hit

    # Tier 3: libsource map (most specific KiCad-side hint).
    if comp.libsource_lib and comp.libsource_part:
        mapped = LIBSOURCE_MAP.get((comp.libsource_lib, comp.libsource_part))
        if mapped is not None:
            cls = _REGISTRY.get(mapped)
            if cls is not None:
                return cls

    # Tier 4: value map (last-resort generic).
    mapped = VALUE_MAP.get(comp.value)
    if mapped is not None:
        cls = _REGISTRY.get(mapped)
        if cls is not None:
            return cls

    # Tier 5: fallback.
    if strict:
        raise UnknownPartError(
            f"Could not resolve KiCad part {comp.ref!r} "
            f"(value={comp.value!r}, "
            f"libsource={comp.libsource_lib!r}.{comp.libsource_part!r}) "
            f"to a wirebench class.  Re-run without --strict to "
            f"substitute UnknownPart placeholders."
        )

    class_name = _unknown_class_name(comp)
    key = (class_name, comp.pin_specs)
    if unknown_cache is not None and key in unknown_cache:
        return unknown_cache[key]
    cls = make_unknown_part_class(
        class_name,
        list(comp.pin_specs),
        refdes_prefix=_refdes_prefix_for(comp.ref) or 'U',
        footprint=comp.footprint,
    )
    if unknown_cache is not None:
        unknown_cache[key] = cls
    return cls


def _unknown_class_name(comp: KiCadComponent) -> str:
    """Synthesise a placeholder class name from the KiCad value."""
    base = comp.value or comp.libsource_part or 'KiCadPart'
    safe = ''.join(c if c.isalnum() else '_' for c in base)
    if not safe or not safe[0].isalpha():
        safe = 'U' + safe
    return f"UnknownPart_{safe}"


def _refdes_prefix_for(refdes: str) -> str | None:
    """Extract the alphabetic prefix from a refdes like 'U12'."""
    prefix = ''
    for c in refdes:
        if c.isalpha():
            prefix += c
        else:
            break
    return prefix or None


def is_chip(cls: type) -> bool:
    return isinstance(cls, type) and issubclass(cls, Chip)
