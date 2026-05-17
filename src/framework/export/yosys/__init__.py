"""Yosys JSON adapter.

Renders to the JSON format consumed by `netlistsvg` for
browser-friendly digital schematics. Each Board becomes its own
module; the assembly is a top-level module whose cells are board
instances.

Yosys nets are integer "bits": each logical net gets a unique
integer starting at 2 (Yosys reserves 0/1 for constants).
"""
from __future__ import annotations

__all__ = ['render', 'name_yosys_net']

import json
from typing import Any, Callable

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.errors import RendererNotFoundError
from framework.part import Part
from framework.node import Node
from framework.port import Direction, Port

from framework.export.base import (
    ExporterContext, pin_number_of, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.yosys import renderers as _renderers  # noqa: F401


def name_yosys_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Yosys nets are integer bit IDs (as strings; the adapter
    converts to int at JSON emission). Allocated sequentially
    starting at 2 — 0 and 1 are reserved constants."""
    return f"{net.id + 2}"


register_net_namer('yosys', name_yosys_net)


def _direction(d: Direction) -> str:
    if d is Direction.IN:
        return 'input'
    if d is Direction.OUT:
        return 'output'
    return 'inout'


def render(design: Part, ctx: ExporterContext) -> str:
    """Assemble a complete Yosys JSON document for `design`."""
    from framework.connector import Connector
    from framework.pin import Pin
    from components.passives.led import LED
    from components.passives.resistor import Resistor
    from components.passives.rail import Rail

    title = getattr(design, 'name', None) or type(design).__name__

    modules: dict[str, dict[str, Any]] = {}

    # Counter-based bit allocator: unconnected ports get sequential
    # IDs starting at a high base so they don't collide with the
    # logical-net IDs (which start at 2). Allocation order is
    # design-traversal order, which is deterministic.
    nc_base = 1 + max(
        (net.id + 2 for net in ctx.logical_nets),
        default=1,
    )
    nc_alloc: dict[int, int] = {}

    def bit_of(port: Port) -> int:
        if port.node is None:
            key = id(port)
            if key not in nc_alloc:
                nc_alloc[key] = nc_base + len(nc_alloc)
            return nc_alloc[key]
        return int(name_yosys_net(_node_to_net(ctx, port.node), ctx))

    def is_skip(n: Part) -> bool:
        return isinstance(n, (Pin, Rail))

    def build_module(name: str, owner: Part,
                     top_components: list[Part]) -> dict[str, Any]:
        module: dict[str, Any] = {
            'ports': {},
            'cells': {},
            'netnames': {},
        }
        # ports: from the owner's surface (if any).
        for pname, port in getattr(owner, 'ports', {}).items():
            module['ports'][pname] = {
                'direction': _direction(port.direction),
                'bits': [bit_of(port)],
            }
        # cells: every refdes-bearing top-level component on this module.
        for comp in top_components:
            cell = _cell_record(comp, bit_of)
            if cell is not None:
                module['cells'][comp.refdes] = cell
        # netnames: every logical net visible in this module.
        seen_bits: set[int] = set()
        for comp in top_components:
            for pname, port in comp.ports.items():
                b = bit_of(port)
                if b in seen_bits:
                    continue
                seen_bits.add(b)
                if port.node is None:
                    continue
                net = _node_to_net(ctx, port.node)
                net_label = _net_label(net, ctx)
                module['netnames'][net_label] = {
                    'hide_name': 0 if not net_label.startswith('$') else 1,
                    'bits': [b],
                    'attributes': {},
                }
        return module

    def gather_top_components(root: Part) -> list[Part]:
        """Refdes-bearing direct children, skipping pins/rails and
        descending into non-Chip / non-Board Circuit containers."""
        out: list[Part] = []

        def visit(node: Part) -> None:
            if is_skip(node):
                return
            if isinstance(node, Chip):
                out.append(node); return
            if isinstance(node, Board):
                # Boards become cell stubs at the parent level.
                out.append(node); return
            if isinstance(node, Connector):
                out.append(node); return
            # Refdes-bearing composite (e.g. a Diode-as-Circuit) —
            # emit as a single cell; don't descend.
            if isinstance(node, Circuit) and getattr(node, 'refdes', None):
                out.append(node); return
            if isinstance(node, Circuit):
                for c in node.parts:
                    visit(c)
                return
            if getattr(node, 'refdes', None):
                out.append(node)

        for c in (root.parts if isinstance(root, Circuit) else [root]):
            visit(c)
        return out

    # If the design contains Boards, emit one module per Board plus a
    # top-level module instantiating them as cells. Otherwise just one
    # top-level module.
    if isinstance(design, Circuit):
        boards = [c for c in design.parts if isinstance(c, Board)]
    else:
        boards = []

    if boards:
        # Per-board modules (only their internal contents).
        for b in boards:
            modules[type(b).__name__ + '_' + b.refdes] = build_module(
                type(b).__name__ + '_' + b.refdes,
                b,
                gather_top_components(b),
            )
        # Top-level module: every board becomes a cell.
        modules[title] = build_module(title, design, gather_top_components(design))
    else:
        modules[title] = build_module(title, design, gather_top_components(design))

    doc = {
        'creator': 'wirebench 0.x',
        'modules': modules,
    }
    ctx.emit(json.dumps(doc, indent=2, sort_keys=True))
    return ctx.output()


# --- Helpers ---------------------------------------------------------------

def _node_to_net(ctx: ExporterContext, node: Node) -> LogicalNet:
    """Find the LogicalNet that includes the given Node object."""
    for net in ctx.logical_nets:
        if id(node) in net.nodes:
            return net
    raise RendererNotFoundError(f"Node {node!r} not in any LogicalNet")


def _net_label(net: LogicalNet, ctx: ExporterContext) -> str:
    """Human-readable net name for the `netnames` map. Uses vcc/GND
    when the net has a Rail, otherwise the integer bit ID."""
    from components.passives.rail import Rail
    if any(isinstance(o, Rail) and o.level is False for o, _ in net.ports):
        return 'GND'
    if any(isinstance(o, Rail) and o.level is True for o, _ in net.ports):
        return 'vcc'
    return f"net_{net.id}"


def _cell_record(
    comp: Part,
    bit_of: Callable[[Port], int],
) -> dict[str, Any] | None:
    """Build the per-cell JSON record for one component. Returns None
    for components that shouldn't be emitted as cells."""
    from framework.connector import Connector
    from framework.board import Board

    if isinstance(comp, Connector):
        # Connectors are conductors; netlistsvg renders them as
        # transparent connection lines. Emit a small placeholder cell.
        return {
            'type': type(comp).__name__,
            'hide_name': 0,
            'parameters': {},
            'port_directions': {
                name: _direction(p.direction)
                for name, p in comp.ports.items()
                if not name.endswith('_inner')
            },
            'connections': {
                name: [bit_of(p)]
                for name, p in comp.ports.items()
                if not name.endswith('_inner')
            },
        }
    if isinstance(comp, Board):
        return {
            'type': type(comp).__name__,
            'hide_name': 0,
            'parameters': {},
            'port_directions': {
                name: _direction(p.direction)
                for name, p in comp.ports.items()
            },
            'connections': {
                name: [bit_of(p)] for name, p in comp.ports.items()
            },
        }
    # Chip or passive — use registered renderer for parameter set, but
    # the bulk of the record is uniform.
    parameters: dict[str, Any] = {}
    record: dict[str, Any] = {
        'type': type(comp).__name__,
        'hide_name': 0,
        'parameters': parameters,
        'port_directions': {
            name: _direction(p.direction) for name, p in comp.ports.items()
        },
        'connections': {
            name: [bit_of(p)] for name, p in comp.ports.items()
        },
    }
    from components.passives.led import LED
    from components.passives.resistor import Resistor
    if isinstance(comp, Resistor):
        parameters['ohms'] = f"{float(comp.ohms):g}"
    elif isinstance(comp, LED):
        parameters['color'] = comp.color
    return record
