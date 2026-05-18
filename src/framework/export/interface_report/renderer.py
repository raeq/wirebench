"""Markdown rendering for the interface report.

One section per `Board` in the design.  For every connector on the
board, render a table of its pins: pin number, name, direction,
internal connections (other surface ports on the same logical net via
the pin's internal face), and best-effort role hints (rail tap,
open-drain bus member).
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.drive_type import DriveType
from framework.export.base import ExporterContext
from framework.export.nets import LogicalNet
from framework.export.reports_common import (
    collect_surface_parts,
    direction_label,
    port_qualifier,
    surface_ports_on_net,
)
from framework.part import Part
from framework.pin import Pin
from components.passives.rail import Rail


def build_report(design: Part, ctx: ExporterContext) -> str:
    nets = ctx.logical_nets
    node_to_net = _build_node_index(nets)
    surface = collect_surface_parts(design)
    boards = _find_boards(design)

    title = type(design).__name__
    lines: list[str] = [
        f"# Interface Report — {title}",
        "",
    ]
    if not boards:
        lines.append(
            "This design contains no `Board` subclasses; there are no "
            "public connector interfaces to enumerate.  See "
            "`<Design>.net-report.md` for the topology view of a "
            "standalone Circuit."
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.append(f"{len(boards)} board(s) in this design: " +
                 ', '.join(f"{b.refdes} (`{type(b).__name__}`)" for b in boards) +
                 ".")
    lines.append("")

    mate_pairs = _mated_pairs(boards, node_to_net)
    if mate_pairs:
        lines.append("Mating pairs:")
        for (a_ref, b_ref) in mate_pairs:
            lines.append(f"- {a_ref} mates with {b_ref}")
        lines.append("")

    for board in boards:
        lines.extend(_render_board(board, surface, node_to_net))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_node_index(nets: list[LogicalNet]) -> dict[int, LogicalNet]:
    """Map every node id in every net to its enclosing LogicalNet so
    we can look up by `id(port.node)`."""
    index: dict[int, LogicalNet] = {}
    for net in nets:
        for nid in net.nodes:
            index[nid] = net
    return index


def _find_boards(design: Part) -> list[Board]:
    """All Boards in the design (top-level or nested).  Order is
    deterministic per the auto-collect traversal of `parts`."""
    if isinstance(design, Board):
        return [design]
    boards: list[Board] = []
    if not isinstance(design, Circuit):
        return boards
    stack: list[Part] = list(design.parts)
    while stack:
        part = stack.pop(0)
        if isinstance(part, Board):
            boards.append(part)
            # Don't descend into a Board's parts to find nested boards;
            # the spec scope is one report level per Board.
            continue
        if isinstance(part, (Chip,)):
            continue
        if isinstance(part, Circuit):
            stack[0:0] = list(part.parts)
    return boards


def _mated_pairs(
    boards: list[Board], node_to_net: dict[int, LogicalNet],
) -> list[tuple[str, str]]:
    """Pairs of `(board_refdes.connector_refdes, …)` whose external
    faces share a logical net — i.e. boards that have been `mate()`d
    together inside the parent assembly."""
    pairs: set[tuple[str, str]] = set()
    seen_refs: list[str] = []
    seen_nets: dict[int, str] = {}
    for board in boards:
        for connector in board.connectors:
            ref = f"{board.refdes}.{connector.refdes}"
            for pin in connector.pins:
                node = pin.external.node
                if node is None:
                    continue
                net = node_to_net.get(id(node))
                if net is None:
                    continue
                key = id(net)
                if key in seen_nets and seen_nets[key] != ref:
                    pair = tuple(sorted([seen_nets[key], ref]))
                    pairs.add(pair)  # type: ignore[arg-type]
                else:
                    seen_nets[key] = ref
            seen_refs.append(ref)
    return sorted(pairs)


def _render_board(
    board: Board,
    surface: list[Part],
    node_to_net: dict[int, LogicalNet],
) -> list[str]:
    """Markdown section for one Board: its connectors and their pins."""
    header = (
        f"## Board: `{type(board).__name__}` ({board.refdes})"
    )
    info_bits = []
    if getattr(board, 'name', None):
        info_bits.append(f"name {board.name!r}")
    if getattr(board, 'revision', None):
        info_bits.append(f"rev {board.revision}")
    info_line = ', '.join(info_bits)
    lines = [header, ""]
    if info_line:
        lines.extend([info_line + ".", ""])

    if not board.connectors:
        lines.append("No public connectors on this board.")
        return lines

    lines.append(f"Public connectors ({len(board.connectors)}):")
    lines.append("")
    for connector in board.connectors:
        lines.extend(_render_connector(connector, surface, node_to_net))
        lines.append("")
    return lines


def _render_connector(
    connector: Connector,
    surface: list[Part],
    node_to_net: dict[int, LogicalNet],
) -> list[str]:
    header = (
        f"### {connector.refdes} — `{type(connector).__name__}`, "
        f"{connector.pin_count}-pin @ {connector.pitch_mm} mm"
    )
    lines = [
        header,
        "",
        "| Pin | Name | Direction | Connects to (internal) | Notes |",
        "|-----|------|-----------|------------------------|-------|",
    ]
    for pin in sorted(connector.pins, key=lambda p: p.id.number):
        internal_node = pin.internal.node
        internal_refs = ""
        notes = ""
        if internal_node is not None:
            net = node_to_net.get(id(internal_node))
            if net is not None:
                internal_refs = _format_internal_connections(
                    net, surface, connector,
                )
                notes = _classify_pin_notes(net, surface, pin)
        lines.append(
            f"| {pin.id.number} | {pin.id.name} | "
            f"{direction_label(pin.external)} | "
            f"{internal_refs} | {notes} |"
        )
    return lines


def _format_internal_connections(
    net: LogicalNet, surface: list[Part], own_connector: Connector,
) -> str:
    """Surface ports on `net` (excluding the connector itself), joined
    with ' + '.  Chip-level surface views collapse all cell-port
    activity into a single `Chip.pin_name` reference."""
    surface_views = surface_ports_on_net(surface, net.nodes)
    seen: set[str] = set()
    deduped: list[str] = []
    for owner, port in surface_views:
        if owner is own_connector:
            continue
        text = port_qualifier(owner, port)
        if text in seen:
            continue
        seen.add(text)
        deduped.append(text)
    return ' + '.join(deduped)


def _classify_pin_notes(
    net: LogicalNet, surface: list[Part], this_pin: Pin,
) -> str:
    """Best-effort role hint for the Notes column."""
    surface_views = surface_ports_on_net(surface, net.nodes)
    for owner, _ in surface_views:
        if isinstance(owner, Rail):
            if owner.level is True:
                return "+ supply"
            return "− supply"
    for owner, port in surface_views:
        if isinstance(owner, Chip):
            dt = type(owner).pin_drive_type(port.name)
            if dt in (DriveType.OPEN_DRAIN, DriveType.OPEN_COLLECTOR):
                return f"open-drain bus ({port.name})"
    return ""
