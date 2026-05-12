"""Property-based tests using hypothesis.

Each `@given`-decorated test asserts an invariant that should hold
for any input from a valid strategy.  When hypothesis finds a
counterexample, it pickles it into `.hypothesis/examples` and
replays on subsequent runs — the persisted counterexample becomes
a permanent regression test.  Don't hide flaky strategies with
`@settings(suppress_health_check=...)`; fix the strategy or fix
the implementation.
"""
from __future__ import annotations

import warnings
from collections import Counter

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError

from framework.errors import AmbiguousPinNameError

import components.chips        # noqa: F401  (trigger registration)
import components.connectors   # noqa: F401
import components.passives     # noqa: F401
import framework.export.bom      # noqa: F401
import framework.export.dot      # noqa: F401
import framework.export.kicad    # noqa: F401
import framework.export.mermaid  # noqa: F401
import framework.export.spice    # noqa: F401
import framework.export.yosys    # noqa: F401

from framework.circuit import Circuit
from framework.connector import Connector
from framework.export import export_to_string
from framework.export.nets import compute_logical_nets
from framework.format import load_circuitry, save_circuitry
from framework.ground import ELECTRICAL
from framework.mate import mate
from framework.pin import Pin, PinId
from framework.port import Direction, Port
from framework.port_map import PortMap
from framework.refdes import IEEE_315_PREFIXES, validate_refdes
from framework.signals import Analog, Digital
from framework.wire import wire

from components.connectors.headers import (
    Header2xNFemale, Header2xNMale,
)
from components.chips.sn74hc04 import SN74HC04

from strategies import (
    bjt_transistors, connectors, diodes, leds, mosfets,
    pin_counts_for_2xn, pin_id_sets, pitches_mm, rails,
    refdes_numbers, resistors, simple_chips,
)


_any_component = st.one_of(
    resistors(), leds(), rails(), simple_chips(), connectors(),
    bjt_transistors(), mosfets(), diodes(),
)


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


# 1.  PortMap dispatch correctness ------------------------------------

def _make_portmap(pin_id_pairs: list[tuple[int, str]]) -> PortMap:
    """Construct a PortMap from a `[(number, name), ...]` sequence."""
    by_number: dict[int, Port] = {}
    for number, name in pin_id_pairs:
        port = Port(name, Direction.BIDIR, ELECTRICAL,
                    mandatory=False, signal_type=Digital)
        by_number[number] = port
    return PortMap(by_number)


@given(pin_id_sets())
def test_portmap_dispatch_correctness(pins):
    pm = _make_portmap(pins)

    # (a) len matches the number of distinct pin numbers in the input.
    distinct_numbers = {n for n, _ in pins}
    assert len(pm) == len(distinct_numbers)

    # (b)+(c) For each canonical name: unique names resolve, duplicated
    # names raise.
    name_counts = Counter(name for _, name in pins)
    for name, count in name_counts.items():
        if count == 1:
            assert pm[name].name == name
        else:
            with pytest.raises(AmbiguousPinNameError) as ei:
                _ = pm[name]
            msg = str(ei.value)
            # Disambiguated alternatives all appear in the message.
            for i in range(1, count + 1):
                assert f'{name}_{i}' in msg

    # (d) Every disambiguated key (<name>_<ordinal>) resolves.
    for name, count in name_counts.items():
        if count > 1:
            for i in range(1, count + 1):
                key = f'{name}_{i}'
                assert pm[key].name == name

    # (e) Iteration yields every pin exactly once.
    iterated = list(pm)
    assert len(iterated) == len(distinct_numbers)
    assert len(set(iterated)) == len(iterated)


# 2.  Round-trip identity for any component ---------------------------

# Slower than the rest because of file I/O; cap at 50 examples.
@given(component=_any_component)
@settings(max_examples=50, deadline=None)
def test_roundtrip_identity_for_any_component(component, tmp_path_factory):
    tmp = tmp_path_factory.mktemp('hyp_rt')
    wrapper = Circuit(factor_nodes=[component], ports=dict(component.ports))
    p = tmp / 'a.circuitry'
    _silently(save_circuitry, wrapper, p)
    loaded = _silently(load_circuitry, p)
    loaded_part = loaded._factor_nodes[0]
    assert type(loaded_part).__name__ == type(component).__name__
    if hasattr(component, 'refdes') and hasattr(loaded_part, 'refdes'):
        assert loaded_part.refdes == component.refdes
    assert set(loaded_part.ports.keys()) == set(component.ports.keys())


# 3.  Save determinism ------------------------------------------------

@given(component=_any_component)
@settings(max_examples=50, deadline=None)
def test_save_is_deterministic(component, tmp_path_factory):
    tmp = tmp_path_factory.mktemp('hyp_det')
    wrapper = Circuit(factor_nodes=[component], ports=dict(component.ports))
    p1 = tmp / 'a.circuitry'
    p2 = tmp / 'b.circuitry'
    _silently(save_circuitry, wrapper, p1)
    _silently(save_circuitry, wrapper, p2)
    assert p1.read_text() == p2.read_text()


# 4.  wire() rules are symmetric --------------------------------------

@given(
    sig1=st.sampled_from([Analog, Digital]),
    sig2=st.sampled_from([Analog, Digital]),
    dir1=st.sampled_from([Direction.IN, Direction.OUT, Direction.BIDIR]),
    dir2=st.sampled_from([Direction.IN, Direction.OUT, Direction.BIDIR]),
)
def test_wire_is_symmetric_about_argument_order(sig1, sig2, dir1, dir2):
    """wire(a, b) succeeds ↔ wire(b, a) succeeds (commutativity)."""
    def make(sig, dr, name):
        return Port(name, dr, ELECTRICAL, mandatory=False, signal_type=sig)

    p1 = make(sig1, dir1, 'p1')
    p2 = make(sig2, dir2, 'p2')
    p3 = make(sig1, dir1, 'p3')  # fresh copies for the swapped call
    p4 = make(sig2, dir2, 'p4')

    forward_ok = True
    try:
        wire(p1, p2)
    except Exception as e:
        forward_ok = False
        fwd_msg = str(e)

    reverse_ok = True
    try:
        wire(p4, p3)
    except Exception as e:
        reverse_ok = False
        rev_msg = str(e)

    assert forward_ok == reverse_ok, (
        f'asymmetric wire() result: '
        f'(sig1={sig1}, sig2={sig2}, dir1={dir1}, dir2={dir2}) '
        f'forward={forward_ok}, reverse={reverse_ok}'
    )


# 5.  compute_logical_nets is deterministic ---------------------------

@given(ohms_values=st.lists(
    st.floats(min_value=10.0, max_value=1e6,
              allow_nan=False, allow_infinity=False),
    min_size=3, max_size=8,
))
def test_compute_logical_nets_is_deterministic(ohms_values):
    """A fixed-shape circuit (Rail → resistor chain → Rail) with
    randomised resistor values: compute_logical_nets must yield the
    same net structure on every call."""
    from components.passives.rail import Rail
    from components.passives.resistor import Resistor

    vcc = Rail(level=True)
    gnd = Rail(level=False)
    resistors_ = [
        Resistor(ohms=v, refdes_number=i + 1)
        for i, v in enumerate(ohms_values)
    ]
    # Wire every resistor in parallel between VCC and GND so each net
    # has a driver and ERC validation passes — chains aren't valid
    # under this framework's two-rail topology constraint.
    for r in resistors_:
        wire(vcc.ports['out'], r.ports['t1'])
        wire(r.ports['t2'], gnd.ports['out'])

    circuit = Circuit(factor_nodes=[vcc, gnd, *resistors_], ports={})

    n1 = compute_logical_nets(circuit)
    n2 = compute_logical_nets(circuit)

    assert len(n1) == len(n2)
    for a, b in zip(n1, n2):
        assert {id(p) for _, p in a.ports} == {id(p) for _, p in b.ports}


# 6.  PortMap iteration order is pin-number-ascending ----------------

@given(pin_id_sets())
def test_portmap_iteration_is_pin_number_ascending(pins):
    pm = _make_portmap(pins)
    # The disambiguated keys are inserted in ascending pin-number
    # order; iteration walks that insertion order.
    keys = list(pm)
    by_key: dict[str, int] = {}
    for n, name in pins:
        siblings = [n2 for n2, nm in pins if nm == name]
        if len(siblings) == 1:
            by_key[name] = n
        else:
            ordinal = sorted(siblings).index(n) + 1
            by_key[f'{name}_{ordinal}'] = n
    iterated_pin_numbers = [by_key[k] for k in keys]
    assert iterated_pin_numbers == sorted(iterated_pin_numbers)


# 7.  Refdes validation rejects invalid prefixes / non-positive numbers

@given(
    prefix=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                   min_size=1, max_size=3),
    number=st.integers(min_value=-50, max_value=999),
)
def test_refdes_validation_rules(prefix, number):
    # Valid prefix (in IEEE 315) AND positive number → no raise.
    # Otherwise (unknown prefix OR non-positive number) → raise.
    if prefix in IEEE_315_PREFIXES and number > 0:
        validate_refdes(prefix, number)
    else:
        with pytest.raises((ValueError, TypeError, ValidationError)):
            validate_refdes(prefix, number)


# 8.  Mated 2xN connectors preserve pin count -------------------------

@given(pin_count=pin_counts_for_2xn(), pitch=pitches_mm())
def test_mated_2xn_connectors_preserve_pin_count(pin_count, pitch):
    male = Header2xNMale(refdes_number=1, pin_count=pin_count, pitch_mm=pitch)
    female = Header2xNFemale(refdes_number=2, pin_count=pin_count, pitch_mm=pitch)
    mate(male, female)
    circuit = Circuit(
        factor_nodes=[male, female],
        ports={**{f'M_{k}': p for k, p in male.ports.items()}},
    )
    nets = compute_logical_nets(circuit)
    # Each mated pair becomes one logical net.
    assert len(nets) == pin_count


# 9.  Renderer determinism -------------------------------------------

@given(component=simple_chips())
@settings(max_examples=50, deadline=None)  # six format passes per example
def test_renderer_is_deterministic(component):
    wrapper = Circuit(factor_nodes=[component], ports=dict(component.ports))
    for fmt in ('spice', 'kicad', 'dot', 'mermaid', 'yosys', 'bom'):
        a = _silently(export_to_string, wrapper, fmt)
        b = _silently(export_to_string, wrapper, fmt)
        assert a == b, f'non-deterministic {fmt} render'


# 10. @validate_call rejects invalid refdes types --------------------

@given(bad=st.one_of(
    st.text(min_size=1, max_size=8),
    st.floats(min_value=-1e6, max_value=0, allow_nan=False),
    st.none(),
))
def test_validate_call_rejects_invalid_refdes(bad):
    with pytest.raises((ValueError, TypeError, ValidationError)):
        SN74HC04(refdes_number=bad)
