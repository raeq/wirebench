"""BOM CSV adapter.

Bill of materials — one row per refdes-bearing component. Suitable for
procurement, assembly, and stocking. Sorted by refdes for human
readability.

Per spec §5.5: Connectors appear on the BOM (they're real parts);
Rails and conductors (Pins) do not. Boards appear as their own row;
their internal components are also listed, with a `Parent` column
naming the enclosing board.
"""
from __future__ import annotations

from framework.factor import FactorNode

from framework.export.base import (
    ExporterContext, lookup_renderer, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.bom import renderers as _renderers  # noqa: F401


def name_bom_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """BOM doesn't reference net names. Return a stable placeholder."""
    return f"net_{net.id}"


register_net_namer('bom', name_bom_net)


def _sort_key(refdes: str) -> tuple[str, int]:
    """Natural sort: alphabetic prefix first, then numeric suffix.

    `'C2'` sorts before `'C10'` (numerical within prefix), and `'C9'`
    sorts before `'D1'` (alphabetical across prefixes).  This produces
    the canonical BOM ordering seen in industry CAD tools: every C
    grouped together, every D grouped together, etc., with the groups
    appearing in alphabetical order."""
    prefix = refdes.rstrip('0123456789')
    number_part = refdes[len(prefix):]
    return (prefix, int(number_part) if number_part else 0)


def render(design: FactorNode, ctx: ExporterContext) -> str:
    """Assemble a complete BOM CSV for `design`."""
    from framework.board import Board
    from framework.chip import Chip
    from framework.circuit import Circuit
    from framework.pin import Pin
    from components.passives.rail import Rail

    rows: list[tuple[str, str]] = []  # (refdes_for_sort, csv_line)

    def visit(node: FactorNode, parent_refdes: str) -> None:
        if isinstance(node, (Pin, Rail)):
            return
        # Chip is a Circuit subclass but is a *part*, not a hierarchy
        # to descend into for BOM purposes (its cells are private
        # implementation, not separately procurable). Check Chip
        # before Board / Circuit.
        if isinstance(node, Chip):
            refdes = node.refdes
            line = lookup_renderer(type(node), 'bom')(node, ctx, parent_refdes)
            if line:
                rows.append((refdes, line))
            return
        if isinstance(node, Board):
            line = lookup_renderer(type(node), 'bom')(node, ctx, parent_refdes)
            if line:
                rows.append((node.refdes, line))
            for child in node._factor_nodes:
                visit(child, node.refdes)
            return
        # Refdes-bearing Circuit that isn't a Chip or Board — a
        # composite part that models itself as a small sub-design but
        # appears on the BOM as one procurable item.  Treat it as a
        # single row; don't descend into its private internal cells.
        if isinstance(node, Circuit) and getattr(node, 'refdes', None):
            line = lookup_renderer(type(node), 'bom')(node, ctx, parent_refdes)
            if line:
                rows.append((node.refdes, line))
            return
        if isinstance(node, Circuit):
            # Non-refdes raw Circuit composite — transparent: recurse
            # into children, attribute them to the same parent.
            for child in node._factor_nodes:
                visit(child, parent_refdes)
            return
        # Leaf: passive or connector.
        refdes = getattr(node, 'refdes', None)
        if not refdes:
            return
        line = lookup_renderer(type(node), 'bom')(node, ctx, parent_refdes)
        if line:
            rows.append((refdes, line))

    visit(design, "")

    # Header + sorted rows.
    ctx.emit("Refdes,Value,Footprint,Quantity,Parent,Description")
    for _, line in sorted(rows, key=lambda r: _sort_key(r[0])):
        ctx.emit(line)
    return ctx.output()
