"""Mermaid flowchart adapter.

Browser-renderable flowchart syntax — works natively in GitHub /
GitLab / Notion READMEs and via the `mmdc` CLI. Same bipartite shape
as the DOT adapter: components as rectangle nodes, nets as
double-circle nodes, edges with port-name labels.
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.factor import FactorNode

from framework.export.base import (
    ExporterContext, lookup_renderer, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.mermaid import renderers as _renderers  # noqa: F401


def name_mermaid_net(net: LogicalNet, ctx: ExporterContext) -> str:
    from components.passives.rail import Rail
    if any(isinstance(o, Rail) and o.level is False for o, _ in net.ports):
        return 'gnd'
    if any(isinstance(o, Rail) and o.level is True for o, _ in net.ports):
        return 'vcc'
    return f"net_{net.id}"


register_net_namer('mermaid', name_mermaid_net)


def render(design: FactorNode, ctx: ExporterContext) -> str:
    """Assemble a complete Mermaid flowchart for `design`."""
    from framework.connector import Connector
    from framework.pin import Pin
    from components.passives.rail import Rail

    ctx.emit('%%{init: {"theme": "neutral"}}%%')
    ctx.emit('flowchart LR')

    boards: list[Board] = []
    top: list[FactorNode] = []
    by_board: dict[str, list[FactorNode]] = {}

    def collect(parent_board: str, node: FactorNode) -> None:
        if isinstance(node, (Pin, Connector, Rail)):
            return
        if isinstance(node, Chip):
            (by_board.setdefault(parent_board, []) if parent_board else top).append(node)
            return
        if isinstance(node, Board):
            boards.append(node)
            by_board.setdefault(node.refdes, [])
            for c in node._factor_nodes:
                collect(node.refdes, c)
            return
        if isinstance(node, Circuit):
            for c in node._factor_nodes:
                collect(parent_board, c)
            return
        if getattr(node, 'refdes', None):
            (by_board.setdefault(parent_board, []) if parent_board else top).append(node)

    if isinstance(design, Board):
        boards.append(design)
        for c in design._factor_nodes:
            collect(design.refdes, c)
    else:
        children = design._factor_nodes if isinstance(design, Circuit) else [design]
        for c in children:
            collect("", c)

    # Top-level boxes.
    for comp in top:
        ctx.emit("    " + lookup_renderer(type(comp), 'mermaid')(comp, ctx))

    # Per-board subgraphs.
    for b in boards:
        label = f"{b.refdes}: {b.name} Rev {b.revision}"
        ctx.emit(f'    subgraph {b.refdes}["{label}"]')
        for comp in by_board.get(b.refdes, []):
            ctx.emit("        " + lookup_renderer(type(comp), 'mermaid')(comp, ctx))
        ctx.emit('    end')

    # Triples (refdes, port, net_name) used for nets + edges.
    all_components = list(top)
    for cs in by_board.values():
        all_components.extend(cs)
    triples: list[tuple[str, str, str]] = []
    for comp in all_components:
        for name, port in comp.ports.items():
            if port.node is None:
                continue
            triples.append((comp.refdes, name, ctx.net_name(port)))
    triples.sort()

    # Net nodes (double-circle).
    seen: set[str] = set()
    for _, _, net in triples:
        if net in seen:
            continue
        seen.add(net)
        ctx.emit(f'    {net}(("{net}"))')

    # Edges.
    for rd, port_name, net in triples:
        ctx.emit(f'    {rd} ---|"{port_name}"| {net}')

    return ctx.output()
