"""Phase 2.7 — Node.dynamically_driven annotation.

Construction-time tests for the designer assertion that a net is driven
through a feedback loop, opting it out of Circuit._validate's
multi-BIDIR-no-driver rule.  Also covers round-tripping through the
.wirebench save/load path.
"""
from __future__ import annotations

import warnings

import pytest

from components.passives.rail import Rail
from components.passives.resistor import Resistor
from framework.circuit import Circuit
from framework.errors import FloatingNetError, ShortCircuitError
from framework.format import load_wirebench, save_wirebench
from framework.signals import Analog
from framework.wire import wire


# ---------------------------------------------------------------------------
# Positive cases — the annotation suppresses the floating-net rule
# ---------------------------------------------------------------------------


def _two_resistor_divider(*, annotate: bool) -> Circuit:
    """Rail → R1 → mid → R2 → GND.  Mid-node is multi-BIDIR-no-driver."""
    vcc = Rail(True,  signal_type=Analog)
    gnd = Rail(False, signal_type=Analog)
    r1  = Resistor(10_000, refdes_number=1)
    r2  = Resistor(10_000, refdes_number=2)
    wire(vcc.out, r1.t1)
    wire(r1.t2, r2.t1, dynamically_driven=annotate)
    wire(r2.t2, gnd.out)
    return Circuit(parts=[vcc, gnd, r1, r2], ports={})


def test_annotated_mid_node_constructs():
    """Two-resistor divider with the mid-node annotated constructs cleanly."""
    circuit = _two_resistor_divider(annotate=True)
    assert isinstance(circuit, Circuit)


def test_unannotated_mid_node_raises():
    """Same circuit, no annotation → FloatingNetError as before."""
    with pytest.raises(FloatingNetError):
        _two_resistor_divider(annotate=False)


def test_three_resistor_two_annotated_mid_nodes_constructs():
    """A longer divider with two annotated mid-nodes constructs cleanly."""
    vcc = Rail(True,  signal_type=Analog)
    gnd = Rail(False, signal_type=Analog)
    r1  = Resistor(10_000, refdes_number=1)
    r2  = Resistor(10_000, refdes_number=2)
    r3  = Resistor(10_000, refdes_number=3)
    wire(vcc.out, r1.t1)
    wire(r1.t2, r2.t1, dynamically_driven=True)
    wire(r2.t2, r3.t1, dynamically_driven=True)
    wire(r3.t2, gnd.out)
    Circuit(parts=[vcc, gnd, r1, r2, r3], ports={})


def test_annotation_persists_across_extending_wire_calls():
    """A later `wire()` call that omits the kwarg does not clear a
    previously-set annotation on the same Node."""
    vcc = Rail(True,  signal_type=Analog)
    gnd = Rail(False, signal_type=Analog)
    r1  = Resistor(10_000, refdes_number=1)
    r2  = Resistor(10_000, refdes_number=2)
    r3  = Resistor(10_000, refdes_number=3)
    wire(vcc.out, r1.t1)
    # First call sets the annotation on the mid-node.
    wire(r1.t2, r2.t1, dynamically_driven=True)
    # Extending the same node *without* the kwarg must leave the
    # annotation in place.
    wire(r2.t1, r3.t1)
    wire(r3.t2, gnd.out)
    wire(r2.t2, gnd.out)
    # No exception → the annotation persisted across the second call.
    Circuit(parts=[vcc, gnd, r1, r2, r3], ports={})
    # Direct assertion on the Node attribute.
    assert r1.t2.node.dynamically_driven is True
    assert r3.t1.node.dynamically_driven is True


# ---------------------------------------------------------------------------
# Negative cases — strictness preserved
# ---------------------------------------------------------------------------


def test_dynamically_driven_does_not_suppress_short_circuit():
    """Annotation must not suppress ShortCircuitError on multi-OUT nets."""
    vcc1 = Rail(True, signal_type=Analog)
    vcc2 = Rail(True, signal_type=Analog)
    r1   = Resistor(10_000, refdes_number=1)
    with pytest.raises(ShortCircuitError):
        wire(vcc1.out, vcc2.out, r1.t1, dynamically_driven=True)


# ---------------------------------------------------------------------------
# Misuse hint — UserWarning when annotation is unnecessary
# ---------------------------------------------------------------------------


def test_annotation_on_already_driven_net_warns():
    """`dynamically_driven=True` on a net with an OUT driver produces a
    UserWarning but the design still constructs."""
    vcc = Rail(True, signal_type=Analog)
    r1  = Resistor(10_000, refdes_number=1)
    with pytest.warns(UserWarning, match='has no effect'):
        wire(vcc.out, r1.t1, dynamically_driven=True)


def test_no_warning_when_annotation_is_meaningful():
    """A 3-port passive-only net is exactly the case the annotation is
    designed for; no warning should fire."""
    r1 = Resistor(10_000, refdes_number=1)
    r2 = Resistor(10_000, refdes_number=2)
    r3 = Resistor(10_000, refdes_number=3)
    with warnings.catch_warnings():
        warnings.simplefilter('error')   # any warning → test fails
        wire(r1.t1, r2.t1, r3.t1, dynamically_driven=True)


# ---------------------------------------------------------------------------
# Default behaviour unchanged
# ---------------------------------------------------------------------------


def test_unannotated_wire_call_does_not_set_flag():
    """A normal wire() call leaves dynamically_driven=False on the Node."""
    r1 = Resistor(10_000, refdes_number=1)
    r2 = Resistor(10_000, refdes_number=2)
    wire(r1.t1, r2.t1)
    assert r1.t1.node.dynamically_driven is False


# ---------------------------------------------------------------------------
# Save/load round-trip
# ---------------------------------------------------------------------------


def _annotated_divider_circuit_class() -> type[Circuit]:
    class AnnotatedDivider(Circuit):
        def __init__(self) -> None:
            self.vcc = Rail(True,  signal_type=Analog)
            self.gnd = Rail(False, signal_type=Analog)
            self.r1  = Resistor(10_000, refdes_number=1)
            self.r2  = Resistor(10_000, refdes_number=2)
            self.r3  = Resistor(10_000, refdes_number=3)
            wire(self.vcc.out, self.r1.t1)
            wire(self.r1.t2,   self.r2.t1, self.r3.t1,
                 dynamically_driven=True)
            wire(self.r2.t2,   self.gnd.out)
            wire(self.r3.t2,   self.gnd.out)
            super().__init__()
    return AnnotatedDivider


def test_save_load_roundtrip_preserves_annotation(tmp_path):
    AnnotatedDivider = _annotated_divider_circuit_class()
    original = AnnotatedDivider()
    path = tmp_path / 'annotated.wirebench'
    save_wirebench(original, path)
    loaded = load_wirebench(path)

    # The loaded design must construct without FloatingNetError, which
    # implicitly proves the annotation survived the round-trip.
    assert isinstance(loaded, Circuit)

    # The annotated wire connected R1.t2, R2.t1, R3.t1.  Find any of
    # those ports and verify the underlying node carries the flag.
    annotated_nodes = [
        p.t2.node for p in loaded.parts
        if isinstance(p, Resistor) and getattr(p, 'refdes', '') == 'R1'
    ]
    assert annotated_nodes and annotated_nodes[0] is not None
    assert annotated_nodes[0].dynamically_driven is True


def test_save_load_roundtrip_byte_identical(tmp_path):
    """Saving twice produces identical bytes — the annotation field
    serialises deterministically."""
    AnnotatedDivider = _annotated_divider_circuit_class()
    p1 = tmp_path / '1.wirebench'
    p2 = tmp_path / '2.wirebench'
    save_wirebench(AnnotatedDivider(), p1)
    save_wirebench(AnnotatedDivider(), p2)
    assert p1.read_text() == p2.read_text()


def test_save_omits_dynamically_driven_when_false(tmp_path):
    """A circuit with no annotated wires must not write the field —
    keeps the format compact for the common case."""
    class PlainDivider(Circuit):
        def __init__(self) -> None:
            self.vcc = Rail(True,  signal_type=Analog)
            self.gnd = Rail(False, signal_type=Analog)
            self.r1  = Resistor(10_000, refdes_number=1)
            wire(self.vcc.out, self.r1.t1)
            wire(self.r1.t2,   self.gnd.out)
            super().__init__()
    path = tmp_path / 'plain.wirebench'
    save_wirebench(PlainDivider(), path)
    text = path.read_text()
    assert 'dynamically_driven' not in text


def test_save_includes_dynamically_driven_when_true(tmp_path):
    """An annotated wire records the field in the JSON."""
    AnnotatedDivider = _annotated_divider_circuit_class()
    path = tmp_path / 'annotated.wirebench'
    save_wirebench(AnnotatedDivider(), path)
    text = path.read_text()
    assert '"dynamically_driven": true' in text
