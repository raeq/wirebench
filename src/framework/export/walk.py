"""Hierarchical walking helpers for export adapters.

Exporters often need to visit each composite (Assembly / Board / Chip)
and emit a corresponding bracket in the output (`.SUBCKT` in SPICE,
hierarchical sheet in KiCad). This module provides the walker plus a
small `Path` value object that tracks the dotted refdes path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterator

from framework.circuit import Circuit
from framework.factor import FactorNode


@dataclass(frozen=True, slots=True)
class Path:
    """Hierarchical refdes path to a composite. Immutable."""
    segments: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def empty(cls) -> 'Path':
        return cls(segments=())

    def with_child(self, refdes: str) -> 'Path':
        return Path(segments=self.segments + (refdes,))

    def qualified_refdes(self) -> str:
        return '.'.join(self.segments)

    def __str__(self) -> str:
        return self.qualified_refdes() or '<root>'


def _is_composite(fn: FactorNode) -> bool:
    """Composites get .SUBCKT-like brackets in hierarchical outputs."""
    return isinstance(fn, Circuit)


def walk_hierarchy(
    design: FactorNode,
    visitor: Callable[[FactorNode, Path], None],
) -> None:
    """Depth-first walk of composite components.

    `visitor(composite, path)` is invoked for every Circuit composite
    encountered (Boards, Chips, Assemblies). The root is visited with
    `Path.empty()`; children are visited with the path qualified by
    each enclosing composite's refdes (when refdes-bearing).

    Leaf components (passives, connectors) are not visited — adapters
    handle them through per-component renderers.
    """
    def descend(node: FactorNode, path: Path) -> None:
        visitor(node, path)
        if isinstance(node, Circuit):
            for child in node._factor_nodes:
                if _is_composite(child):
                    child_refdes = getattr(child, 'refdes', None)
                    child_path = (
                        path.with_child(child_refdes)
                        if child_refdes else path
                    )
                    descend(child, child_path)

    descend(design, Path.empty())


def iter_composites(design: FactorNode) -> Iterator[tuple[FactorNode, Path]]:
    """Generator form of `walk_hierarchy`."""
    items: list[tuple[FactorNode, Path]] = []
    walk_hierarchy(design, lambda c, p: items.append((c, p)))
    return iter(items)
