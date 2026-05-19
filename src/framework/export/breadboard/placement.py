"""Breadboard placement layer.

Reuses `framework.export.assembly_guide.placement.place()` so component
positions are *identical* to those quoted in the assembly-guide build
steps (acceptance criterion 8). The breadboard renderer's only job at
this layer is to (a) walk the design into the same parts list the
assembly guide uses, (b) refuse SMD / multi-board designs, and (c)
hand the placement back as `(component, pin_name, position, row)`
tuples ready for the SVG layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from framework.board import Board
from framework.chip import Chip
from framework.errors import BreadboardIncompatibleError
from framework.part import Part

from framework.export.assembly_guide.placement import (
    ComponentPlacement, PinPlacement, place,
)
from framework.export.assembly_guide.recipe import _walk_top_parts, _is_rail


__all__ = [
    'ComponentPlacement', 'PinPlacement',
    'collect_parts', 'refuse_unsupported', 'place_design',
]


def collect_parts(design: Part) -> tuple[list[Part], list[Part]]:
    """Walk `design` and return (all_parts, placeable_parts).

    `all_parts` is every BOM-level part including Rails — the routing
    layer needs Rails so rail nets are detected.

    `placeable_parts` excludes Rails (which have no physical position;
    they map to the breadboard rail strips)."""
    all_parts = _walk_top_parts(design)
    placeable = [p for p in all_parts if not _is_rail(p)]
    return all_parts, placeable


def refuse_unsupported(design: Part, placeable: list[Part]) -> None:
    """Raise `BreadboardIncompatibleError` if `design` cannot be rendered.

    v1 refusals (matching assembly_guide §10):
      - Top-level design is a `Board` (one populated PCB, not a circuit).
      - Top-level design contains nested `Board`s (multi-board assembly).
      - Any part has `is_breadboard_compatible == False` (SMD).
    """
    if isinstance(design, Board):
        raise BreadboardIncompatibleError(
            "The breadboard visualiser renders single-circuit designs onto "
            "a standard solderless breadboard. The top-level design is a "
            f"Board ({type(design).__name__}) — a populated PCB. Render "
            "`board.circuit` directly, or use the `kicad_sch` exporter for "
            "the PCB schematic."
        )
    nested = [p for p in placeable if isinstance(p, Board)]
    if nested:
        raise BreadboardIncompatibleError(
            f"Multi-board design (top level is a {type(design).__name__} "
            f"containing {len(nested)} Boards). Multi-board assemblies "
            "aren't usefully built on a single breadboard. Render each "
            "Board's internal circuit separately, or use the `kicad_sch` "
            "hierarchical exporter for the system-level schematic."
        )
    incompat = [p for p in placeable if not p.is_breadboard_compatible]
    if incompat:
        lines = [
            f"{len(incompat)} part"
            f"{'s' if len(incompat) != 1 else ''} "
            "can't be assembled on a breadboard:"
        ]
        for p in incompat:
            refdes = getattr(p, 'refdes', '<no-refdes>')
            cls = type(p).__name__
            fp = getattr(p, 'FOOTPRINT', None) or '(no footprint)'
            lines.append(f"  - {refdes} ({cls}) — {fp}")
        lines.append("")
        lines.append(
            "Use `export(<design>, 'kicad', …)` for a PCB netlist, or rework "
            "the design with breadboard-friendly part variants (DIP packages, "
            "THT passives, 0.1\" headers)."
        )
        raise BreadboardIncompatibleError('\n'.join(lines))


@dataclass(frozen=True, slots=True)
class PlacementResult:
    """Bundle of everything the renderer needs after placement.

    components — every placed component (chips first, then passives), each
                 with its full pin placements.
    by_component — id(component) → ComponentPlacement, for O(1) lookup
                   from a port back to its pin's tie strip.
    """
    components: tuple[ComponentPlacement, ...]
    by_component: dict[int, ComponentPlacement]


def place_design(placeable: Iterable[Part]) -> PlacementResult:
    """Run the shared assembly_guide placement algorithm on `placeable`.

    The two artefacts (assembly guide + breadboard SVG) consume the same
    placement output so position references match across both."""
    placeable = list(placeable)
    chips = [p for p in placeable if isinstance(p, Chip)]
    passives = [p for p in placeable if not isinstance(p, Chip)]
    components = place(chips, passives)
    by_component = {id(p.component): p for p in components}
    return PlacementResult(components=components, by_component=by_component)
