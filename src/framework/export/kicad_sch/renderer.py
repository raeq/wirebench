"""KiCad schematic renderer — Phase 2.5b.

Produces a `.kicad_sch` file (format version 20240618, KiCad 9) from any
wirebench `Part` (Circuit, Board, or leaf component).

Phase 2.5b upgrades over 2.5a:
  - Layered Signal Flow placement (power / signal / indicator bands,
    BFS layer assignment, generous 1500-mil spacing, cluster breakup).
  - Orthogonal wire routing between pin stub ends (Manhattan L-shapes),
    with junction emission at 3-way meeting points.
  - Page sized to fit the layout (A4 → A3 → A2 → A1).
  - Global labels retained at stub ends for net-name readability.
"""
from __future__ import annotations

import hashlib
import math
import warnings
from collections import defaultdict
from typing import Iterator

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export.base import ExporterContext
from framework.export.nets import LogicalNet, compute_logical_nets
from framework.part import Part
from framework.port import Port

from framework.export.kicad_sch.library_loader import (
    PinDef, collect_lib_symbols, get_pin_defs,
)
from framework.export.kicad_sch.placement import layered_place, sheet_size_for_layout
from framework.export.kicad_sch.routing import Segment, find_junctions, route_net
from framework.export.kicad_sch.symbol_map import SymbolEntry, connector_entry, lookup

_STUB_MM: float = 2.54
_SCH_VERSION: int = 20250114   # KiCad 9/10 schematic format version
_FONT_SIZE: str = '1.27 1.27'

_PAPER_NAMES: dict[tuple[int, int], str] = {
    (297, 210): 'A4',
    (420, 297): 'A3',
    (594, 420): 'A2',
    (841, 594): 'A1',
}


# ---------------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------------

def _uuid(seed: str) -> str:
    h = hashlib.md5(seed.encode()).hexdigest()
    return f'{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}'


# ---------------------------------------------------------------------------
# String building helpers
# ---------------------------------------------------------------------------

def _q(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _f(v: float) -> str:
    """Format a mm value with at most 6 significant digits, no trailing zeros."""
    return f'{v:.6g}'


def _xy(x: float, y: float) -> str:
    return f'{_f(x)} {_f(y)}'


def _effects(size: str = _FONT_SIZE, hide: bool = False, justify: str = '') -> str:
    h = ' (hide yes)' if hide else ''
    j = f' (justify {justify})' if justify else ''
    return f'(effects (font (size {size})){j}{h})'


# ---------------------------------------------------------------------------
# Part collection
# ---------------------------------------------------------------------------

def _collect_leaf_parts(design: Part) -> list[Part]:
    """Flat list of leaf components in the design (no Rails, no Pins)."""
    from components.passives.rail import Rail
    from framework.pin import Pin

    result: list[Part] = []
    seen: set[int] = set()

    def visit(node: Part) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        if isinstance(node, (Pin, Rail)):
            return
        if isinstance(node, Circuit):
            for child in node.parts:
                visit(child)
            if getattr(node, 'refdes', None) and not isinstance(node, Board):
                if node not in result:
                    result.append(node)
        else:
            result.append(node)

    if isinstance(design, Circuit):
        for child in design.parts:
            visit(child)
    else:
        visit(design)
    return result


# ---------------------------------------------------------------------------
# Net-name helpers
# ---------------------------------------------------------------------------

def _net_name_for_port(port: Port, nets: list[LogicalNet]) -> str:
    """Return the net name for `port`, or 'NC' if unconnected."""
    if port.node is None:
        return 'NC'
    nid = id(port.node)
    for net in nets:
        if nid in net.nodes:
            return _label_for_net(net)
    return f'net_{nid}'


def _label_for_net(net: LogicalNet) -> str:
    """Human-readable label from the net's first refdes/port pair."""
    from components.passives.rail import Rail
    for owner, port in net.ports:
        if isinstance(owner, Rail):
            return 'GND' if owner.level is False else 'VCC'
    candidates: list[tuple[str, str]] = []
    for owner, port in net.ports:
        rd = getattr(owner, 'refdes', None)
        if rd:
            candidates.append((str(rd), port.name))
    if candidates:
        candidates.sort()
        rd, pn = candidates[0]
        return f'Net-({rd}-{pn})'
    return f'N{net.id}'


def _is_power_net(net_name: str) -> bool:
    return net_name in ('GND', 'VCC') or net_name.startswith('+') or net_name.startswith('-')


# ---------------------------------------------------------------------------
# Pin stub + label / power-symbol helpers
# ---------------------------------------------------------------------------

def _abs_pin_pos(
    sx: float, sy: float, rotation_deg: float, pin: PinDef,
) -> tuple[float, float]:
    """Absolute pin connection-point position for a placed symbol."""
    r = math.radians(rotation_deg)
    ax = sx + pin.x * math.cos(r) + pin.y * math.sin(r)
    ay = sy - pin.x * math.sin(r) + pin.y * math.cos(r)
    return ax, ay


def _stub_end(px: float, py: float, pin_angle: float) -> tuple[float, float]:
    """Extend _STUB_MM from the pin connection point, pointing away from the
    symbol body.

    KiCad pin angles describe the direction FROM the connection point TOWARD
    the symbol body; the stub extends in the opposite direction (angle+180°).
    KiCad uses a Y-down coordinate system so sin increases downward.
    """
    outward = math.radians((pin_angle + 180) % 360)
    ex = px + _STUB_MM * math.cos(outward)
    ey = py + _STUB_MM * math.sin(outward)
    return ex, ey


def _snap(v: float) -> float:
    """Snap to 1.27 mm (50-mil) grid."""
    return round(v / 1.27) * 1.27


def _emit_stub_and_label(
    px: float, py: float,
    pin_angle: float,
    net_name: str,
    seed: str,
    lines: list[str],
) -> tuple[float, float]:
    """Emit a stub wire and a global_label (or power symbol) at its end.

    Returns the stub end position (ex, ey) so the caller can collect it
    for wire routing.
    """
    ex, ey = _stub_end(px, py, pin_angle)
    ex, ey = _snap(ex), _snap(ey)
    px_s, py_s = _snap(px), _snap(py)

    lines.append(
        f'  (wire\n'
        f'    (pts (xy {_xy(px_s, py_s)}) (xy {_xy(ex, ey)}))\n'
        f'    (stroke (width 0) (type default))\n'
        f'    (uuid {_q(_uuid(seed + "_wire"))})\n'
        f'  )'
    )

    if net_name == 'GND':
        _emit_power_symbol('GND', ex, ey, seed, lines)
    elif net_name in ('VCC', '+5V', '+3.3V', '+3V3', '+12V'):
        _emit_power_symbol('VCC', ex, ey, seed, lines)
    elif net_name != 'NC':
        lines.append(
            f'  (global_label {_q(net_name)}\n'
            f'    (shape input)\n'
            f'    (at {_xy(ex, ey)} 0)\n'
            f'    (fields_autoplaced yes)\n'
            f'    {_effects(justify="right")}\n'
            f'    (property "Intersheet References" "${{INTERSHEET_REFS}}"\n'
            f'      (at 0 0 0)\n'
            f'      {_effects(hide=True)}\n'
            f'    )\n'
            f'    (uuid {_q(_uuid(seed + "_label"))})\n'
            f'  )'
        )

    return ex, ey


def _emit_power_symbol(
    sym_name: str, x: float, y: float, seed: str, lines: list[str],
) -> None:
    angle = 270 if sym_name == 'GND' else 90
    lines.append(
        f'  (symbol\n'
        f'    (lib_id {_q("power:" + sym_name)})\n'
        f'    (at {_xy(x, y)} {angle})\n'
        f'    (unit 1)\n'
        f'    (exclude_from_sim no)\n'
        f'    (in_bom yes)\n'
        f'    (on_board yes)\n'
        f'    (dnp no)\n'
        f'    (uuid {_q(_uuid(seed + "_pwrsym"))})\n'
        f'    (property "Reference" "#PWR"\n'
        f'      (at {_xy(x, y)} 0)\n'
        f'      {_effects(hide=True)}\n'
        f'    )\n'
        f'    (property "Value" {_q(sym_name)}\n'
        f'      (at {_xy(x, y)} 0)\n'
        f'      {_effects()}\n'
        f'    )\n'
        f'    (pin "1" (uuid {_q(_uuid(seed + "_pwrpin"))}))\n'
        f'  )'
    )


# ---------------------------------------------------------------------------
# Symbol instance emission
# ---------------------------------------------------------------------------

def _part_value(part: Part) -> str:
    """Human-readable value string for the schematic property."""
    for attr in ('ohms', 'farads', 'henries', 'value', 'resistance',
                 'capacitance', 'inductance'):
        v = getattr(part, attr, None)
        if v is not None:
            return str(v)
    return type(part).__name__


def _emit_symbol_instance(
    part: Part,
    entry: SymbolEntry,
    x: float, y: float,
    refdes: str,
    nets: list[LogicalNet],
    lines: list[str],
    used_symbols: list[tuple[str, str]],
    net_stub_ends: dict[str, list[tuple[float, float]]],
) -> None:
    """Emit a `(symbol ...)` instance and the stub wires/labels for its pins.

    Stub end positions are collected into `net_stub_ends` for wire routing.
    """
    lib_id = f'{entry.lib}:{entry.name}'
    value = entry.value_template or _part_value(part)
    sym_uuid = _uuid(f'{refdes}_{lib_id}')

    lines.append(
        f'  (symbol\n'
        f'    (lib_id {_q(lib_id)})\n'
        f'    (at {_xy(x, y)} 0)\n'
        f'    (unit 1)\n'
        f'    (exclude_from_sim no)\n'
        f'    (in_bom yes)\n'
        f'    (on_board yes)\n'
        f'    (dnp no)\n'
        f'    (uuid {_q(sym_uuid)})\n'
        f'    (property "Reference" {_q(refdes)}\n'
        f'      (at {_xy(x + 2.54, y - 2.54)} 0)\n'
        f'      {_effects()}\n'
        f'    )\n'
        f'    (property "Value" {_q(value)}\n'
        f'      (at {_xy(x, y + 2.54)} 0)\n'
        f'      {_effects()}\n'
        f'    )'
    )

    pin_defs = get_pin_defs(entry.lib, entry.name)
    for pin in pin_defs:
        pin_uuid = _uuid(f'{refdes}_{lib_id}_pin{pin.number}')
        lines.append(f'    (pin {_q(pin.number)} (uuid {_q(pin_uuid)}))')

    lines.append('  )')

    if (entry.lib, entry.name) not in used_symbols:
        used_symbols.append((entry.lib, entry.name))

    # Emit stub wires + labels; collect stub ends for routing.
    all_ports = dict(part.ports) if hasattr(part, 'ports') else {}
    for pin in pin_defs:
        ax, ay = _abs_pin_pos(x, y, 0.0, pin)
        net_name = 'NC'
        for port_name, port in all_ports.items():
            pn = _port_pin_number(part, port_name)
            if pn is not None and str(pn) == str(pin.number):
                net_name = _net_name_for_port(port, nets)
                break
        pin_seed = f'{refdes}_{lib_id}_pin{pin.number}'
        ex, ey = _emit_stub_and_label(
            ax, ay, pin.angle, net_name, seed=pin_seed, lines=lines,
        )
        if net_name not in ('NC',) and not _is_power_net(net_name):
            net_stub_ends[net_name].append((ex, ey))


def _port_pin_number(part: Part, port_name: str) -> int | None:
    """Pin number for `port_name` on `part`, checking Pin.id and PIN_NUMBERS."""
    for pin in getattr(part, 'pins', ()):
        if pin.id.name == port_name:
            return int(pin.id.number)
    n = getattr(type(part), 'PIN_NUMBERS', {}).get(port_name)
    return None if n is None else int(n)


# ---------------------------------------------------------------------------
# Connector handling
# ---------------------------------------------------------------------------

def _connector_pin_count(part: Part) -> int:
    return len(part.ports)


# ---------------------------------------------------------------------------
# Wire routing emission
# ---------------------------------------------------------------------------

def _emit_routed_wires(
    net_stub_ends: dict[str, list[tuple[float, float]]],
    lines: list[str],
) -> None:
    """Route and emit wire segments connecting stub ends within each net."""
    all_segments: list[Segment] = []

    for net_name in sorted(net_stub_ends):
        ends = net_stub_ends[net_name]
        if len(ends) < 2:
            continue
        segs = route_net(ends)
        for seg in segs:
            (x1, y1), (x2, y2) = seg
            wire_seed = f'route_{net_name}_{x1:.3f}_{y1:.3f}_{x2:.3f}_{y2:.3f}'
            lines.append(
                f'  (wire\n'
                f'    (pts (xy {_xy(x1, y1)}) (xy {_xy(x2, y2)}))\n'
                f'    (stroke (width 0) (type default))\n'
                f'    (uuid {_q(_uuid(wire_seed))})\n'
                f'  )'
            )
        all_segments.extend(segs)

    for jx, jy in find_junctions(all_segments):
        lines.append(f'  (junction (at {_xy(jx, jy)}))')


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render(design: Part, ctx: ExporterContext) -> str:
    """Produce a complete `.kicad_sch` document for `design`."""
    from components.passives.rail import Rail
    from framework.export.kicad_sch.hierarchical import collect_boards, emit_top_level
    _boards = collect_boards(design)
    if len(_boards) > 1:
        return emit_top_level(_boards, type(design).__name__)

    logical_nets = compute_logical_nets(design)

    leaf_parts = _collect_leaf_parts(design)
    non_rail = [p for p in leaf_parts if not isinstance(p, Rail)]

    # Stage 1–8: layered placement
    positions = layered_place(non_rail, logical_nets)

    lines: list[str] = []
    symbol_lines: list[str] = []
    used_symbols: list[tuple[str, str]] = []
    net_stub_ends: dict[str, list[tuple[float, float]]] = defaultdict(list)

    refdes_counters: dict[str, int] = {}

    def next_refdes(prefix: str) -> str:
        n = refdes_counters.get(prefix, 1)
        refdes_counters[prefix] = n + 1
        return f'{prefix}{n}'

    def get_refdes(part: Part, entry: SymbolEntry) -> str:
        rd = getattr(part, 'refdes', None)
        if rd:
            return str(rd)
        return next_refdes(entry.refdes_prefix)

    for part in non_rail:
        if id(part) not in positions:
            continue
        x, y = positions[id(part)]

        resolved: SymbolEntry | None
        if isinstance(part, Connector):
            n = _connector_pin_count(part)
            resolved = connector_entry(n) if 1 <= n <= 40 else None
        else:
            resolved = lookup(part)

        if resolved is None:
            continue

        entry: SymbolEntry = resolved
        refdes = get_refdes(part, entry)
        _emit_symbol_instance(
            part, entry, x, y, refdes,
            logical_nets, symbol_lines, used_symbols, net_stub_ends,
        )

    # Stage 9: power symbols added to used list
    used_symbols.append(('power', 'GND'))
    used_symbols.append(('power', 'VCC'))

    # Routing wires between stub ends (signal nets only)
    _emit_routed_wires(net_stub_ends, symbol_lines)

    # lib_symbols section
    lib_map = collect_lib_symbols(used_symbols)

    # Page sizing
    sw, sh = sheet_size_for_layout(positions)
    paper = _PAPER_NAMES.get((int(sw), int(sh)), 'User')

    design_name = type(design).__name__
    lines.append('(kicad_sch')
    lines.append(f'  (version {_SCH_VERSION})')
    lines.append('  (generator "wirebench")')
    lines.append('  (generator_version "0.2")')
    lines.append(f'  (uuid {_q(_uuid(design_name))})')
    if paper == 'User':
        lines.append(f'  (paper "User" {_f(sw)} {_f(sh)})')
    else:
        lines.append(f'  (paper {_q(paper)})')

    if lib_map:
        lines.append('  (lib_symbols')
        for _qname, sym_text in sorted(lib_map.items()):
            normalised = '\n'.join(
                '    ' + ln.expandtabs(2).lstrip('\t')
                for ln in sym_text.splitlines()
            )
            lines.append(normalised)
        lines.append('  )')

    lines.extend(symbol_lines)

    lines.append(
        '  (sheet_instances\n'
        '    (path "/" (page "1"))\n'
        '  )'
    )
    lines.append(')')
    return '\n'.join(lines) + '\n'


def render_all(design: Part, ctx: ExporterContext) -> dict[str, str]:
    """Return all .kicad_sch files for `design` as {filename: content}."""
    from framework.export.kicad_sch.hierarchical import (
        collect_boards, sub_sheet_filename, emit_top_level,
    )

    design_name = type(design).__name__
    boards = collect_boards(design)
    if len(boards) < 2:
        return {f'{design_name}.kicad_sch': render(design, ctx)}

    result: dict[str, str] = {}
    result[f'{design_name}.kicad_sch'] = emit_top_level(boards, design_name)
    for board in boards:
        board_class_name = type(board).__name__
        filename = sub_sheet_filename(design_name, board_class_name)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            board_ctx = ExporterContext(board, 'kicad_sch', ctx.config)
        result[filename] = render(board, board_ctx)
    return result
