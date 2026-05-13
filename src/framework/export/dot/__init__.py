"""Graphviz DOT adapter.

Bipartite circuit graph: components are box nodes, nets are small
circle nodes, edges connect each component port to the net it sits on.
The output is consumed by `dot -Tsvg|png|pdf` for documentation.

Per-component renderers emit the component's `node` declaration.
Edges are emitted at the net-walker level by iterating each
`LogicalNet`'s ports — that's where the port-name annotation comes
from.
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.part import Part

from framework.export.base import (
    ExporterContext, lookup_renderer, pin_number_of, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.dot import renderers as _renderers  # noqa: F401


def name_dot_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """DOT net names: vcc / gnd / net_<n>. Short and readable."""
    from components.passives.rail import Rail
    if any(isinstance(o, Rail) and o.level is False for o, _ in net.ports):
        return 'gnd'
    if any(isinstance(o, Rail) and o.level is True for o, _ in net.ports):
        return 'vcc'
    return f"net_{net.id}"


register_net_namer('dot', name_dot_net)


def _dot_id(refdes: str) -> str:
    """DOT identifiers can contain alphanumerics and underscore. Refdes
    already follows this convention (R1, A1, etc.) — passthrough."""
    return refdes


def _dot_string(s: str) -> str:
    """Escape a string for DOT label syntax: backslashes and quotes."""
    return s.replace('\\', '\\\\').replace('"', '\\"')


def render(design: Part, ctx: ExporterContext) -> str:
    """Assemble a complete DOT graph for `design`."""
    from framework.pin import Pin
    from framework.connector import Connector
    from components.passives.rail import Rail

    title = getattr(design, 'name', None) or type(design).__name__
    ctx.emit(f'digraph "{_dot_string(title)}" {{')
    ctx.emit('  rankdir=LR;')
    ctx.emit('  node [shape=box, fontname="monospace"];')
    ctx.emit('')

    # Collect the leaves we'll render as boxes: chips + passives. Per
    # spec §5.2, connectors are conductors and emit nothing in DOT —
    # they're already collapsed at the logical-net level. Boards
    # become DOT subgraph clusters; their internal components are
    # rendered inside.
    boards: list[Board] = []
    top_components: list[Part] = []
    board_components: dict[str, list[Part]] = {}

    def is_box_leaf(node: Part) -> bool:
        # Skip conductors (Pin, Connector), Rails, and anything
        # without a refdes. Chips, Resistors, LEDs qualify.
        if isinstance(node, (Pin, Connector, Rail)):
            return False
        return getattr(node, 'refdes', None) is not None and not isinstance(node, Circuit)

    def collect(parent_board: str, node: Part) -> None:
        if isinstance(node, Chip):
            target = (board_components.setdefault(parent_board, [])
                      if parent_board else top_components)
            target.append(node)
            return
        if isinstance(node, Board):
            boards.append(node)
            board_components.setdefault(node.refdes, [])
            for c in node.parts:
                collect(node.refdes, c)
            return
        # Refdes-bearing composite — emit as a single box, don't
        # descend into its private cells.
        if isinstance(node, Circuit) and getattr(node, 'refdes', None):
            target = (board_components.setdefault(parent_board, [])
                      if parent_board else top_components)
            target.append(node)
            return
        if isinstance(node, Circuit):
            for c in node.parts:
                collect(parent_board, c)
            return
        if is_box_leaf(node):
            target = (board_components.setdefault(parent_board, [])
                      if parent_board else top_components)
            target.append(node)

    if isinstance(design, Board):
        boards.append(design)
        for c in design.parts:
            collect(design.refdes, c)
    else:
        for c in (design.parts if isinstance(design, Circuit)
                  else [design]):
            collect("", c)

    # Top-level component box declarations.
    for comp in top_components:
        ctx.emit("  " + lookup_renderer(type(comp), 'dot')(comp, ctx))

    # Per-board subgraph clusters.
    for b in boards:
        ctx.emit('')
        ctx.emit(f'  subgraph cluster_{_dot_id(b.refdes)} {{')
        label = f"{b.refdes}: {b.name} Rev {b.revision}"
        ctx.emit(f'    label="{_dot_string(label)}";')
        ctx.emit('    style=rounded;')
        for comp in board_components.get(b.refdes, []):
            ctx.emit("    " + lookup_renderer(type(comp), 'dot')(comp, ctx))
        ctx.emit('  }')

    # Collect the (component, port, net_name) triples used for edges.
    # Walk each box leaf, query ctx.net_name for each port; only emit
    # an edge when the port is on a real (non-nc) net.
    all_components = list(top_components)
    for cs in board_components.values():
        all_components.extend(cs)
    triples: list[tuple[str, str, str]] = []
    for comp in all_components:
        rd = comp.refdes
        for name, port in comp.ports.items():
            if port.node is None:
                continue  # unconnected — skip
            triples.append((rd, name, ctx.net_name(port)))

    # Emit the net circle nodes, sorted by name for determinism.
    net_names = sorted({n for _, _, n in triples})
    if net_names:
        ctx.emit('')
        ctx.emit('  // Nets')
        ctx.emit('  node [shape=circle, label="", width=0.15, fixedsize=true];')
        ctx.emit('  ' + '; '.join(net_names) + ';')

    # Edges. Sort for determinism.
    ctx.emit('')
    ctx.emit('  // Edges (component -- net, taillabel = port name)')
    ctx.emit('  edge [arrowhead=none, fontname="monospace", fontsize=9];')
    for refdes, port_name, net_name in sorted(triples):
        ctx.emit(f'  {_dot_id(refdes)} -> {net_name} [taillabel="{port_name}"];')

    ctx.emit('}')
    return ctx.output()
