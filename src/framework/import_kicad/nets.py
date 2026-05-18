"""Net reconstructor — joins parsed KiCad nodes back into wirebench
`wire()` calls.

Inputs:
  - The parsed `(net ...)` blocks from the netlist.
  - A `refdes → Part` dict produced by the resolver.

Output: a list of `(net_name, [(part, port_name), ...])` records the
caller can either feed to `wire(*ports)` (in-memory mode) or render
as `wire(self.a.ports['x'], self.b.ports['y'])` Python source.
"""
from __future__ import annotations

from typing import NamedTuple

from framework.errors import LoadError
from framework.part import Part

from framework.import_kicad.parser import SExpr, children, field_value


_POWER_RAIL_NAMES = frozenset({
    '+5v', '+5V', 'vcc', 'VCC', '+vcc', '+VCC',
    '+3v3', '+3.3v', '3v3', 'vdd', 'VDD',
    '+12v', '+12V', '+9v', '+9V',
})

_GROUND_RAIL_NAMES = frozenset({
    'gnd', 'GND', 'vss', 'VSS', 'agnd', 'AGND', 'dgnd', 'DGND', '0',
})


class NetRecord(NamedTuple):
    name: str
    code: int
    nodes: list[tuple[str, int]]  # (refdes, pin_number)


def parse_nets(nets_section: SExpr) -> list[NetRecord]:
    """Walk a `(nets ...)` section and yield one NetRecord per net."""
    result: list[NetRecord] = []
    for net in children(nets_section, 'net'):
        code_str = field_value(net, 'code', '0') or '0'
        name = field_value(net, 'name', '') or ''
        try:
            code = int(code_str)
        except ValueError:
            code = 0
        nodes: list[tuple[str, int]] = []
        for node in children(net, 'node'):
            ref = field_value(node, 'ref')
            pin = field_value(node, 'pin')
            if ref is None or pin is None:
                continue
            try:
                pin_number = int(pin)
            except ValueError:
                # KiCad sometimes emits non-numeric pin ids for
                # certain symbol types; skip rather than crash.
                continue
            nodes.append((ref, pin_number))
        result.append(NetRecord(name=name, code=code, nodes=nodes))
    return result


def looks_like_high_rail(net_name: str) -> bool:
    return net_name.strip() in _POWER_RAIL_NAMES


def looks_like_low_rail(net_name: str) -> bool:
    return net_name.strip() in _GROUND_RAIL_NAMES


def resolve_port(
    refdes_to_part: dict[str, Part], refdes: str, pin_number: int,
) -> tuple[Part, str] | None:
    """Map a netlist node `(ref, pin)` to a wirebench (part, pin-name).

    For chips and connectors, the wirebench instance carries a
    `ports_by_number` dict keyed by datasheet pin number — exactly
    the lookup KiCad's netlist uses.  For passives (Resistor,
    Capacitor, …) the ports are name-keyed (`t1`, `t2`); we map
    pin 1 → t1 and pin 2 → t2.  Diodes use `anode`/`cathode`.
    Returns None when the part doesn't expose a port at the
    requested pin number — caller may emit a warning."""
    part = refdes_to_part.get(refdes)
    if part is None:
        return None

    # Try the chip / connector path first.
    by_number = getattr(part, 'ports_by_number', None)
    if isinstance(by_number, dict):
        port = by_number.get(pin_number)
        if port is not None:
            return (part, port.name)

    # Passive 2-terminal parts: `t1`, `t2` (Resistor / Capacitor /
    # Inductor) or `anode`/`cathode` (LED, Diode).  Use the static
    # PIN_NUMBERS table the export adapter already relies on.
    pin_numbers = getattr(type(part), 'PIN_NUMBERS', {})
    for port_name, number in pin_numbers.items():
        if number == pin_number and port_name in part.ports:
            return (part, port_name)

    return None
