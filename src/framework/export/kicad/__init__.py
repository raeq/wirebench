"""KiCad netlist adapter (format version "E").

S-expression-based netlist that imports into Eeschema / Pcbnew.
Output is *flat* — every component lives at the top level of
`(components ...)`. Hierarchy is expressed per-component via
`(sheetpath (names "/A1/") (tstamps "/<hash>/"))`. Cross-board
refdes collisions are resolved by qualifying with each ancestor
board's refdes: `A1.U1` becomes `A1_U1` in the emitted refdes.
"""
from __future__ import annotations

import hashlib

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.part import Part
from framework.port import Port

from framework.export.base import (
    ExporterContext, lookup_renderer, pin_number_of, register_net_namer,
)
from framework.export.nets import LogicalNet
from framework.export.kicad import renderers as _renderers  # noqa: F401


def name_kicad_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """KiCad conventions:
        Rail(False)  → 'GND'   (no SPICE-style numeric 0)
        Rail(True)   → 'vcc'
        otherwise    → 'Net-(<lowest_refdes>-Pad<lowest_pin_number>)'
    """
    from components.passives.rail import Rail
    if any(isinstance(o, Rail) and o.level is False for o, _ in net.ports):
        return 'GND'
    if any(isinstance(o, Rail) and o.level is True for o, _ in net.ports):
        return 'vcc'
    # Synthesise from the alphabetically-first refdes on the net.
    candidates: list[tuple[str, int]] = []
    for owner, port in net.ports:
        rd = getattr(owner, 'refdes', None)
        if not rd:
            continue
        pn = pin_number_of(owner, port.name)
        if pn is None:
            continue
        candidates.append((rd, pn))
    if not candidates:
        return f"Net-(unnamed-{net.id})"
    candidates.sort()
    rd, pn = candidates[0]
    return f"Net-({rd}-Pad{pn})"


register_net_namer('kicad', name_kicad_net)


def _esc_string(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"')


def _sheetpath_tstamp(parts: list[str]) -> str:
    """Deterministic SHA-1 of pipe-joined parts, truncated to 8 hex
    chars. Used for KiCad `tstamps`: stable across reruns and across
    machines because the input is fully derived from model state."""
    return hashlib.sha1('|'.join(parts).encode()).hexdigest()[:8]


def _board_path(board_stack: list[Board]) -> tuple[str, str]:
    """Return (names, tstamps) sheetpath strings for the given board
    stack (innermost first → outermost). Empty stack means top-level."""
    if not board_stack:
        return '/', '/'
    names = '/' + '/'.join(b.refdes for b in board_stack) + '/'
    tstamps = '/' + '/'.join(
        _sheetpath_tstamp([b.name, b.revision, b.refdes])
        for b in board_stack
    ) + '/'
    return names, tstamps


def _qualified_refdes(board_stack: list[Board], comp_refdes: str) -> str:
    """Per spec §5.1: qualify with each ancestor board's refdes so
    global uniqueness holds across boards. Standalone Circuit designs
    (no Board ancestor) skip qualification."""
    if not board_stack:
        return comp_refdes
    return '_'.join(b.refdes for b in board_stack) + '_' + comp_refdes


def render(design: Part, ctx: ExporterContext) -> str:
    """Assemble a complete KiCad netlist for `design`."""
    from framework.pin import Pin
    from components.passives.rail import Rail

    title = getattr(design, 'name', None) or type(design).__name__

    ctx.emit('(export (version "E")')
    ctx.emit(f'  (design')
    ctx.emit(f'    (source "{title}")')
    ctx.emit(f'    (tool "wirebench 0.x"))')

    # ----- components block ---------------------------------------------------
    ctx.emit('  (components')

    # Build a list of (qualified_refdes, board_stack, component) tuples.
    components: list[tuple[str, list[Board], Part]] = []

    def visit(board_stack: list[Board], node: Part) -> None:
        if isinstance(node, (Pin, Rail)):
            return
        if isinstance(node, Chip) or (
            isinstance(node, Connector) and not isinstance(node, Circuit)
        ):
            qrd = _qualified_refdes(board_stack, node.refdes)
            components.append((qrd, list(board_stack), node))
            return
        if isinstance(node, Board):
            # Board itself is not emitted as a component; only its
            # children, with the board prepended to the stack.
            new_stack = board_stack + [node]
            for c in node.parts:
                visit(new_stack, c)
            return
        # Refdes-bearing composite — a composite part that has
        # internal cells but is procured as a single component on
        # the netlist. Emit as one entry; don't descend.
        if isinstance(node, Circuit) and getattr(node, 'refdes', None):
            qrd = _qualified_refdes(board_stack, node.refdes)
            components.append((qrd, list(board_stack), node))
            return
        if isinstance(node, Circuit):
            for c in node.parts:
                visit(board_stack, c)
            return
        # Leaf passive.
        rd = getattr(node, 'refdes', None)
        if rd:
            qrd = _qualified_refdes(board_stack, rd)
            components.append((qrd, list(board_stack), node))

    if isinstance(design, Board):
        visit([], design)
    elif isinstance(design, Circuit):
        for c in design.parts:
            visit([], c)
    else:
        visit([], design)

    components.sort(key=lambda t: t[0])
    for qrd, stack, comp in components:
        names, tstamps = _board_path(stack)
        ctx.emit("    " + lookup_renderer(type(comp), 'kicad')(
            comp, ctx, qrd, names, tstamps,
        ))
    ctx.emit('  )')

    # ----- nets block ---------------------------------------------------------
    # Walk every chip/passive/connector port, group by its underlying
    # Node, then synthesise net names from the *qualified* refdeses on
    # each net. We bypass ctx.net_name() for synthesis because
    # net_kicad_net() can't see the board hierarchy from the LogicalNet
    # alone — its 'Net-(...)' synthesis uses unqualified refdes which
    # collides across boards.
    from components.passives.rail import Rail
    nodes_to_entries: dict[int, list[tuple[str, int, str, object, Part]]] = {}
    nodes_to_rails: dict[int, list[Rail]] = {}
    for qrd, stack, comp in components:
        for port_name, port in comp.ports.items():
            if port.node is None:
                continue
            pn = pin_number_of(comp, port_name)
            if pn is None:
                continue
            nid = id(port.node)
            nodes_to_entries.setdefault(nid, []).append(
                (qrd, pn, _kicad_pintype(comp, port), port, comp)
            )
    # Rails attach to nodes too — track them so the namer can use them.
    def collect_rails(node: Part) -> None:
        if isinstance(node, Rail):
            for p in node.ports.values():
                if p.node is not None:
                    nodes_to_rails.setdefault(id(p.node), []).append(node)
            return
        if isinstance(node, Circuit):
            for c in node.parts:
                collect_rails(c)
    collect_rails(design)

    def synth_name(nid: int) -> str:
        if any(r.level is False for r in nodes_to_rails.get(nid, [])):
            return 'GND'
        if any(r.level is True for r in nodes_to_rails.get(nid, [])):
            return 'vcc'
        # Net-(<qrd>-Pad<pn>) from the lowest qualified-refdes entry.
        entries = sorted(nodes_to_entries.get(nid, []),
                         key=lambda e: (e[0], e[1]))
        if entries:
            qrd, pn, *_ = entries[0]
            return f"Net-({qrd}-Pad{pn})"
        return f"Net-(unnamed-{nid})"

    nets_by_name: dict[str, list[tuple[str, int, str]]] = {}
    for nid, entries in nodes_to_entries.items():
        name = synth_name(nid)
        for qrd, pn, ptype, _, _ in entries:
            nets_by_name.setdefault(name, []).append((qrd, pn, ptype))

    ctx.emit('  (nets')
    for code, name in enumerate(sorted(nets_by_name.keys()), start=1):
        ctx.emit(f'    (net (code "{code}") (name "{_esc_string(name)}")')
        for qrd, pn, ptype in sorted(nets_by_name[name]):
            ctx.emit(f'      (node (ref "{qrd}") (pin "{pn}") (pintype "{ptype}"))')
        ctx.emit('    )')
    ctx.emit('  )')
    ctx.emit(')')
    return ctx.output()


def _kicad_pintype(owner: Part, port: Port) -> str:
    """Map a port's direction to a KiCad pintype string, per spec
    §5.1's table."""
    from framework.connector import Connector
    from framework.pin import Pin
    from framework.port import Direction
    from components.passives.rail import Rail

    # Rail OUT is power_out; but Rails are dropped before reaching
    # here. Defensive.
    if isinstance(owner, Rail):
        return 'power_out'
    if isinstance(owner, Pin):
        # Owner of pin's port is the pin itself (logical-net walker
        # records pins as owners). Use the pin's declared role.
        # In practice we only reach here through nets — but the
        # connector check below catches connector pins.
        pass
    if isinstance(owner, Connector):
        return 'passive'
    # Chip pin: use the port's declared direction.
    dirn = getattr(port, 'direction', None)
    if dirn is Direction.IN:
        return 'input'
    if dirn is Direction.OUT:
        return 'output'
    if dirn is Direction.BIDIR:
        # Resistors / LEDs use BIDIR for terminals → passive.
        # Chip pins genuinely-bidir → 'bidirectional'.
        from framework.chip import Chip
        if isinstance(owner, Chip):
            return 'bidirectional'
        return 'passive'
    return 'passive'
