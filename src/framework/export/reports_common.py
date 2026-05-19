"""Shared helpers for the three Markdown reports (net / domain / interface).

The net report, domain report, and interface report all derive their
content from the same model — logical nets, parts, ports, ground
domains.  This module centralises the formatting primitives so the
three renderers stay consistent in voice and the format-specific
modules can focus on layout.
"""
from __future__ import annotations

from typing import Iterable

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.drive_type import DriveType
from framework.part import Part
from framework.pin import Pin
from framework.port import Direction, Port


def refdes_or_class(part: Part) -> str:
    """Refdes for refdes-bearing parts, falling back to class name."""
    refdes = getattr(part, 'refdes', None)
    if refdes:
        return str(refdes)
    return type(part).__name__


def part_description(part: Part) -> str:
    """One-line description suitable for a report bullet.

    Resistor → 'Resistor 4.7 kΩ'.  Capacitor → 'Capacitor 100 nF'.
    LED → 'LED red'.  Chips and connectors → class name.  The output
    avoids quoting so the calling renderer can wrap it in backticks.

    Value formatting is delegated to the unit class's `__str__`
    (`Ohms`, `Farads`, `Henries`) so every consumer of an engineering
    quantity sees the same canonical notation.
    """
    cls = type(part).__name__
    ohms = getattr(part, 'ohms', None)
    if ohms is not None:
        return f"{cls} {ohms}"
    farads = getattr(part, 'farads', None)
    if farads is not None:
        return f"{cls} {farads}"
    henries = getattr(part, 'henries', None)
    if henries is not None:
        return f"{cls} {henries}"
    color = getattr(part, 'color', None) or getattr(part, 'colour', None)
    if color is not None:
        return f"{cls} {color}"
    return cls


def direction_label(port: Port) -> str:
    """Upper-case direction name: 'IN' / 'OUT' / 'BIDIR'."""
    return port.direction.name


def drive_type_for(part: Part, port_name: str) -> DriveType | None:
    """Drive type of `port_name` on `part`, if `part` is a Chip and the
    drive type isn't the default PUSH_PULL.  Returns None otherwise —
    callers omit the annotation in that case so the report stays
    uncluttered."""
    if not isinstance(part, Chip):
        return None
    dt = type(part).pin_drive_type(port_name)
    if dt is DriveType.PUSH_PULL:
        return None
    return dt


def port_qualifier(part: Part, port: Port) -> str:
    """`Refdes.PinName` — the canonical port reference shape used
    across all three reports."""
    return f"{refdes_or_class(part)}.{port.name}"


def port_descriptor(part: Part, port: Port) -> str:
    """Full one-line port descriptor:

        U1.SDA (`ATmega328P`, BIDIR + OPEN_DRAIN)

    The descriptor stays the same shape across drivers, readers, and
    BIDIR rows so consumers can grep one regex.
    """
    qualifier = port_qualifier(part, port)
    description = part_description(part)
    direction = direction_label(port)
    dt = drive_type_for(part, port.name)
    drive_suffix = f" + {dt.name}" if dt is not None else ""
    return f"{qualifier} (`{description}`, {direction}{drive_suffix})"


def classify_ports(
    ports: Iterable[tuple[Part, Port]],
) -> tuple[
    list[tuple[Part, Port]],   # drivers   (Direction.OUT)
    list[tuple[Part, Port]],   # readers   (Direction.IN)
    list[tuple[Part, Port]],   # bidirs    (Direction.BIDIR)
]:
    """Partition a port list into three buckets by Direction.

    The bucketing is purely structural; OPEN_DRAIN buses on BIDIR pins
    aren't recoded into drivers because the framework's model treats
    them as bidir.  The drive-type annotation on each line is what
    surfaces that nuance to a reader."""
    drivers:  list[tuple[Part, Port]] = []
    readers:  list[tuple[Part, Port]] = []
    bidirs:   list[tuple[Part, Port]] = []
    for owner, port in ports:
        # Skip Pin internal/external duplication — the walker's
        # `real_ports` filter already excludes IS_CONDUCTOR carriers
        # (Pin), so a (part, port) pair here always describes a real
        # endpoint.  Belt-and-braces: ignore Pin-owned bookkeeping
        # leftovers if any sneak through.
        if isinstance(owner, Pin):
            continue
        if port.direction is Direction.OUT:
            drivers.append((owner, port))
        elif port.direction is Direction.IN:
            readers.append((owner, port))
        else:
            bidirs.append((owner, port))
    return drivers, readers, bidirs


def collect_surface_parts(design: Part) -> list[Part]:
    """Every Part on the design's *external* surface — what a reviewer
    sees when reading the schematic, not the internal cell mesh of any
    Chip.

    Discipline:
      - Pins (IS_CONDUCTOR) are dropped — they're the bond wires the
        external view treats as transparent.
      - Chips are surfaced *as* the chip; we don't descend into their
        internal cells, per the spec's external-view scope.
      - Circuit / Board composites are descended through so a nested
        Board's parts contribute to the parent design's surface.

    The walk is iterative for testability; order matches the source's
    auto-collect order so reports stay deterministic across re-runs.
    """
    result: list[Part] = []
    if isinstance(design, Circuit):
        roots = list(design.parts)
    else:
        roots = [design]
    stack = list(roots)
    while stack:
        part = stack.pop(0)
        if isinstance(part, Pin):
            continue
        if isinstance(part, Chip):
            result.append(part)
            continue
        if isinstance(part, (Board, Circuit)):
            # Descend — Board's connectors / inner passives become
            # surface elements of the enclosing design.
            stack[0:0] = list(part.parts)
            continue
        result.append(part)
    return result


def surface_ports_on_net(
    surface_parts: list[Part], net_node_ids: frozenset[int],
) -> list[tuple[Part, Port]]:
    """Every (part, port) on the external surface whose port touches
    the given net.  Sorted by `(refdes, port_name)` for determinism.

    For Connectors, only external faces are surfaced — the internal
    `<pin>_inner` faces are board-internal wiring detail and would
    clutter the report.  Chips already surface externals only via
    their `ports` accessor."""
    found: list[tuple[Part, Port]] = []
    for part in surface_parts:
        if isinstance(part, Connector):
            ports_iter = part.external_ports.values()
        else:
            ports_iter = part.ports.values()
        for port in ports_iter:
            node = port.node
            if node is None or id(node) not in net_node_ids:
                continue
            found.append((part, port))
    found.sort(key=lambda op: (str(getattr(op[0], 'refdes', '')), op[1].name))
    return found


def domain_label(domain: object) -> str:
    """The displayable form of a GroundDomain: its `.name` attribute
    upper-cased ('ELECTRICAL', 'ISOLATED_A') so the three reports
    speak the same vocabulary.  The framework normalises everything
    through interned `GroundDomain` instances so identity is preserved
    across this transform."""
    name = getattr(domain, 'name', str(domain))
    return name.upper()
