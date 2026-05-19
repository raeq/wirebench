"""Jumper routing for the breadboard visualiser.

Every wirebench `wire()` becomes either (a) the tie strip itself when
the connected pins land in the same position+bank — no jumper drawn,
the breadboard's internal copper does the connection — or (b) an
orthogonal Manhattan jumper between the two tie strips.

Rail wires (a pin connected to a `Rail.out`) become a jumper from the
pin's tie strip to the nearest tie point on the rail strip.

Colour coding follows the locked palette in `colors.py`:
  - red for + rail jumpers (or jumpers between a passive and the + rail)
  - black for − rail jumpers
  - analog signals cycle through the analog palette by a stable hash
  - digital signals cycle through the digital palette by a stable hash
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from framework.chip import Chip
from framework.part import Part
from framework.pin import Pin
from framework.port import Port
from framework.signals import Analog, Digital

from framework.export.assembly_guide.placement import ComponentPlacement, PinPlacement

from framework.export.breadboard.colors import (
    RAIL_PLUS_JUMPER, RAIL_MINUS_JUMPER,
    analog_color, digital_color,
)


__all__ = ['Jumper', 'JumperKind', 'route_jumpers']


class JumperKind:
    """Enum-ish set of jumper categories used to choose drawing
    parameters (colour, detour direction, label)."""
    RAIL_PLUS:  str = 'rail_plus'
    RAIL_MINUS: str = 'rail_minus'
    ANALOG:     str = 'analog'
    DIGITAL:    str = 'digital'


@dataclass(frozen=True, slots=True)
class Jumper:
    """One jumper to render.

    src_position / src_row / dst_position / dst_row identify the two
    tie strips. For rail jumpers, dst_row is one of '+TOP', '-TOP',
    '+BOT', '-BOT' — the routing layer chooses which side of the board
    based on the source row.

    color is the locked hex string. kind is a JumperKind tag for the
    SVG layer's class attribute. net_label is a stable string for
    debugging (rendered as an SVG title element if desired).
    """
    src_position: int
    src_row: str
    dst_position: int
    dst_row: str
    color: str
    kind: str
    net_label: str


# ----------------------------------------------------------- net walking

def _resolve_rail_polarity(node: object,
                           rail_port_ids: dict[int, bool]) -> bool | None:
    """Return True / False if the node has a Rail port at high / low
    polarity, or None if it's a signal net."""
    if node is None:
        return None
    for face in getattr(node, 'ports', ()):
        pol = rail_port_ids.get(id(face))
        if pol is not None:
            return pol
    return None


def _net_signal_kind(node: object) -> str:
    """Return 'analog' if any port on the net carries an Analog signal
    type, else 'digital'. Pure-rail nets are handled separately by the
    caller before this is called."""
    if node is None:
        return 'digital'
    for face in getattr(node, 'ports', ()):
        st = getattr(face, 'signal_type', None)
        if st is Analog:
            return 'analog'
    return 'digital'


def _net_label(node: object, port_endpoints: list[tuple[int, int, str]]) -> str:
    """Stable label for a net used as the colour-cycle hash key.

    Uses the lowest (refdes, port_name) tuple of the net's non-rail
    endpoints — deterministic across runs and across redraws."""
    endpoints = sorted(
        (f"{rd}.{pn}" for _, _, pn in port_endpoints
         for rd in ['']),  # placeholder; real label assembled below
    )
    if not endpoints:
        return f"net_{id(node)}"
    return endpoints[0]


def _build_indexes(all_parts: Iterable[Part]) -> tuple[dict[int, bool], dict[int, Part]]:
    """Return (rail_port_id → polarity, port_id → owning Part)."""
    from components.passives.rail import Rail
    rail_polarity: dict[int, bool] = {}
    port_owner: dict[int, Part] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        ports = getattr(part, 'ports', None)
        if ports is None:
            continue
        for port in ports.values():
            port_owner[id(port)] = part
            if isinstance(part, Rail):
                rail_polarity[id(port)] = bool(part.level)
    return rail_polarity, port_owner


# ----------------------------------------------------- placement lookups

def _pin_by_port(
    placements: dict[int, ComponentPlacement],
    port_owner: dict[int, Part],
    port: Port,
) -> tuple[int, str] | None:
    """Return (position, row) for the tie strip of `port`'s pin, or
    None if the port has no placement (e.g. it's a Rail port)."""
    owner = port_owner.get(id(port))
    if owner is None:
        return None
    placement = placements.get(id(owner))
    if placement is None:
        # Possibly a pin face inside a chip — chase up to the chip via
        # the port's _owner backref.
        backref = getattr(port, '_owner', None)
        if backref is None:
            return None
        # The Pin's owning Chip is the Pin's `chip` attribute set at
        # construction. Walk up.
        chip = getattr(backref, 'chip', None) or getattr(backref, '_chip', None)
        if chip is None:
            return None
        placement = placements.get(id(chip))
        if placement is None:
            return None
        # The pin's logical name on the chip:
        pin_name = port.name
        pp = placement.pin(pin_name)
        if pp is None:
            return None
        return pp.position, pp.row
    pp_name = port.name
    pp = placement.pin(pp_name)
    if pp is None:
        return None
    return pp.position, pp.row


# ---------------------------------------------- chip pin → port resolution

def _chip_port_to_pin_placement(
    chip: Chip,
    port: Port,
    placement: ComponentPlacement,
) -> PinPlacement | None:
    """Find the pin placement on `chip` for `port`. A chip's external
    ports are exposed through its `Pin` instances; the port's `name`
    is the chip-level pin name (e.g. 'PD3')."""
    return placement.pin(port.name)


# ----------------------------------------------------------- main entry

def route_jumpers(
    all_parts: list[Part],
    placements: dict[int, ComponentPlacement],
) -> list[Jumper]:
    """Compute every jumper to draw on the breadboard.

    Walks every logical net (one per Node), discards same-tie-strip
    nets (the tie strip itself does the connection), and emits one
    Jumper per remaining pin-pair (or pin-to-rail).
    """
    from components.passives.rail import Rail

    rail_polarity, port_owner = _build_indexes(all_parts)

    # Collapse ports by Node so each logical net is walked once.
    node_to_ports: dict[int, list[Port]] = {}
    node_obj: dict[int, object] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        ports = getattr(part, 'ports', None)
        if ports is None:
            continue
        for port in ports.values():
            if port.node is None:
                continue
            nid = id(port.node)
            node_to_ports.setdefault(nid, []).append(port)
            node_obj.setdefault(nid, port.node)

    jumpers: list[Jumper] = []

    # Deterministic net order: sort by the leftmost placed endpoint
    # column on the board, ties broken by lowest endpoint label.
    #
    # Sorting by physical column matters for the colour-assignment
    # pass below — adjacent nets along the board get adjacent palette
    # ordinals, which keeps two visually-adjacent jumpers from landing
    # on the same colour. Label sort would lead to occasional adjacent
    # collisions when two unrelated chips happen to wire into nearby
    # tie strips.
    def _net_sort_key(nid: int) -> tuple[int, int, str]:
        ps = node_to_ports[nid]
        labels: list[str] = []
        leftmost = 10_000
        for p in ps:
            owner = port_owner.get(id(p))
            rd = getattr(owner, 'refdes', None) if owner else None
            if rd:
                labels.append(f"{rd}.{p.name}")
            if isinstance(owner, Rail) or owner is None:
                continue
            placement = placements.get(id(owner))
            if placement is None:
                continue
            pp = placement.pin(p.name)
            if pp is not None and pp.position < leftmost:
                leftmost = pp.position
        label = min(labels) if labels else f"net_{nid}"
        return (leftmost, 0 if labels else 1, label)

    # Track per-kind ordinal counters so analog/digital colour cycles
    # run independently: net visit order N becomes palette index
    # (N mod palette_size). Adjacent nets along the board get
    # different colours unless we wrap the palette.
    analog_counter = 0
    digital_counter = 0

    for nid in sorted(node_to_ports.keys(), key=_net_sort_key):
        ports = node_to_ports[nid]

        # Skip nets with only one connected port — nothing to wire.
        if len(ports) < 2:
            continue

        # Determine net character.
        net_polarity = None
        for p in ports:
            pol = rail_polarity.get(id(p))
            if pol is not None:
                net_polarity = pol
                break

        # Collect every placed (position, row) endpoint on this net,
        # remembering which port each came from for endpoint labels.
        placed_endpoints: list[tuple[int, str, str]] = []
        for p in ports:
            owner = port_owner.get(id(p))
            if isinstance(owner, Rail):
                continue
            placement = placements.get(id(owner)) if owner else None
            if placement is None:
                continue
            pp = placement.pin(p.name)
            if pp is None:
                continue
            rd = getattr(owner, 'refdes', '') or ''
            placed_endpoints.append((pp.position, pp.row, f"{rd}.{p.name}"))

        # Deduplicate by tie strip (position, top-vs-bottom-bank). Two
        # pins on the same tie strip don't need a jumper — the strip
        # itself is one logical node.
        def _bank(row: str) -> str:
            return 'top' if row.upper() in 'ABCDE' else 'bot'

        seen_strip: dict[tuple[int, str], tuple[int, str, str]] = {}
        for ep in placed_endpoints:
            pos, row, label = ep
            key = (pos, _bank(row))
            seen_strip.setdefault(key, ep)
        unique_endpoints = sorted(
            seen_strip.values(), key=lambda e: (e[0], e[1], e[2])
        )

        # Stable net label for the colour-cycle hash.
        net_label = (
            min(ep[2] for ep in unique_endpoints)
            if unique_endpoints else f"net_{nid}"
        )

        if net_polarity is True:
            color = RAIL_PLUS_JUMPER
            kind = JumperKind.RAIL_PLUS
            # Always route to the TOP rails. The shared assembly
            # guide instructs builders to wire only the top `+`/`-`
            # rails to the supply; a standard breadboard's top and
            # bottom rail strips are electrically isolated, so
            # sending a bot-bank pin to a `+BOT`/`-BOT` rail would
            # show an unpowered connection unless the renderer also
            # drew rail-bridge jumpers. Sending every rail jumper to
            # the top rails matches the assembly-guide narrative —
            # bot-bank pins cross the trough via the standard
            # cross-bank double-detour, terminating at the powered
            # top rail.
            rail_marker_top = '+TOP'
            rail_marker_bot = '+TOP'
        elif net_polarity is False:
            color = RAIL_MINUS_JUMPER
            kind = JumperKind.RAIL_MINUS
            rail_marker_top = '-TOP'
            rail_marker_bot = '-TOP'
        else:
            kind_str = _net_signal_kind(node_obj.get(nid))
            if kind_str == 'analog':
                color = analog_color(analog_counter)
                kind = JumperKind.ANALOG
                analog_counter += 1
            else:
                color = digital_color(digital_counter)
                kind = JumperKind.DIGITAL
                digital_counter += 1
            rail_marker_top = rail_marker_bot = ''

        if net_polarity is not None:
            # Rail net: one jumper per non-rail endpoint to the
            # powered top rail (see comment above).
            for pos, row, label in unique_endpoints:
                rail_marker = rail_marker_top if _bank(row) == 'top' else rail_marker_bot
                jumpers.append(Jumper(
                    src_position=pos, src_row=row,
                    dst_position=pos, dst_row=rail_marker,
                    color=color, kind=kind, net_label=net_label,
                ))
        else:
            # Signal net: chain consecutive endpoints (a→b, b→c, …) so
            # every endpoint has at least one neighbour and the chain
            # walks through every tie strip on the net.
            for i in range(len(unique_endpoints) - 1):
                p1, r1, _ = unique_endpoints[i]
                p2, r2, _ = unique_endpoints[i + 1]
                jumpers.append(Jumper(
                    src_position=p1, src_row=r1,
                    dst_position=p2, dst_row=r2,
                    color=color, kind=kind, net_label=net_label,
                ))

    return jumpers
