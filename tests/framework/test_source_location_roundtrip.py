"""`.wirebench` save / load preserves the `source_location` recorded
on each WireRecord, so a reconstructed design still attributes errors
back to the user's original `wire()` call site rather than to the
loader.  When no source was captured, the field is omitted from the
emitted JSON.
"""
from __future__ import annotations

import json

from framework.circuit import Circuit
from framework.format import load_wirebench, save_wirebench
from framework.signals import Analog
from framework.wire import wire
from components.passives.rail import Rail
from components.passives.resistor import Resistor


class PlainDivider(Circuit):
    """Minimal 2-wire divider for round-trip tests."""

    def __init__(self) -> None:
        self.vcc = Rail(True,  signal_type=Analog)
        self.gnd = Rail(False, signal_type=Analog)
        self.r1  = Resistor(10_000, refdes_number=1)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2,   self.gnd.out)
        super().__init__()


def _node_for_port(circuit: Circuit, refdes: str, port_name: str):
    for part in circuit.parts:
        if getattr(part, 'refdes', None) == refdes:
            return part.ports[port_name].node
    raise AssertionError(f"No port {refdes}.{port_name} found")


def test_source_location_round_trips_through_wirebench(tmp_path) -> None:
    """Save a circuit then load it back; each reconstructed node carries
    the same `source_location` it had when saved."""
    original = PlainDivider()
    saved_locs = {
        ('R1', 't1'): _node_for_port(original, 'R1', 't1').source_locations,
        ('R1', 't2'): _node_for_port(original, 'R1', 't2').source_locations,
    }
    # Sanity: capture actually happened for both wires.
    assert all(saved_locs.values())

    path = tmp_path / 'plain.wirebench'
    save_wirebench(original, path)

    reloaded = load_wirebench(path)
    assert isinstance(reloaded, Circuit)
    reloaded_locs = {
        ('R1', 't1'): _node_for_port(reloaded, 'R1', 't1').source_locations,
        ('R1', 't2'): _node_for_port(reloaded, 'R1', 't2').source_locations,
    }
    for key, original_value in saved_locs.items():
        # The loader preserves at least the first saved location.
        assert reloaded_locs[key], (
            f"source_locations vanished after round-trip for {key}"
        )
        assert original_value[0] in reloaded_locs[key], (
            f"original location {original_value[0]} missing after "
            f"round-trip for {key}; got {reloaded_locs[key]}"
        )


def test_source_location_omitted_when_none(tmp_path) -> None:
    """When no source_location is attached to a node, the field stays
    out of the emitted JSON — keeps the format compact for inputs that
    were constructed outside the user-facing wire() path."""
    # Build a divider, then manually clear source locations to simulate
    # nodes that the framework couldn't attribute.
    circuit = PlainDivider()
    for part in circuit.parts:
        for port in part.ports.values():
            if port.node is not None:
                port.node._source_locations.clear()
    path = tmp_path / 'unattributed.wirebench'
    save_wirebench(circuit, path)
    text = path.read_text()
    assert '"source_location"' not in text


def test_source_location_appears_in_emitted_json_when_present(
    tmp_path,
) -> None:
    """The field shows up as a JSON list of [filename, lineno] for every
    wire that has an attributed call site."""
    path = tmp_path / 'attributed.wirebench'
    save_wirebench(PlainDivider(), path)
    obj = json.loads(path.read_text())
    wires = obj['root']['wires']
    assert wires
    for w in wires:
        assert 'source_location' in w
        loc = w['source_location']
        assert isinstance(loc, list) and len(loc) == 2
        filename, lineno = loc
        assert filename.endswith('test_source_location_roundtrip.py')
        assert isinstance(lineno, int)
