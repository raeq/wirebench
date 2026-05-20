"""Framework errors that fire from `wire()` or `Circuit._validate`
carry source locations attributing the defect to the user's `wire()`
call site(s).  The locations render as a `Wired at:` line in the
exception's `str(...)` output.
"""
from __future__ import annotations

import inspect

import pytest

from framework.ground import ELECTRICAL, GroundDomain
from framework.port import Direction, Port
from framework.signals import Analog, Digital
from framework.wire import wire
from framework.errors import (
    DomainCrossingError, EmptyWireError, FloatingNetError, NodeMergeError,
    ShortCircuitError, SignalTypeMismatchError,
)


def _next_line() -> int:
    """Return the line number that immediately follows the caller's
    call to this helper — i.e. the line the next statement occupies."""
    frame = inspect.currentframe()
    assert frame is not None and frame.f_back is not None
    return frame.f_back.f_lineno + 1


# --------------------------------------------------- wire-time errors


def test_short_circuit_error_records_call_site() -> None:
    out1 = Port('o1', Direction.OUT, ELECTRICAL, signal_type=Digital)
    out2 = Port('o2', Direction.OUT, ELECTRICAL, signal_type=Digital)
    with pytest.raises(ShortCircuitError) as exc_info:
        expected_line = _next_line()
        wire(out1, out2)
    locs = exc_info.value.source_locations
    assert len(locs) == 1
    filename, lineno = locs[0]
    assert filename.endswith('test_error_with_source_location.py')
    assert lineno == expected_line
    assert 'Wired at:' in str(exc_info.value)


def test_empty_wire_error_records_call_site() -> None:
    with pytest.raises(EmptyWireError) as exc_info:
        expected_line = _next_line()
        wire()
    locs = exc_info.value.source_locations
    assert len(locs) == 1
    _, lineno = locs[0]
    assert lineno == expected_line


def test_domain_crossing_error_records_call_site() -> None:
    iso = GroundDomain('test_iso_xc_dom')
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.IN,  iso,        signal_type=Digital)
    with pytest.raises(DomainCrossingError) as exc_info:
        expected_line = _next_line()
        wire(a, b)
    _, lineno = exc_info.value.source_locations[0]
    assert lineno == expected_line


def test_floating_net_error_records_call_site() -> None:
    """All-IN ports → wire() refuses immediately with source attribution."""
    a = Port('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.IN, ELECTRICAL, signal_type=Digital)
    with pytest.raises(FloatingNetError) as exc_info:
        expected_line = _next_line()
        wire(a, b)
    _, lineno = exc_info.value.source_locations[0]
    assert lineno == expected_line


def test_signal_type_mismatch_records_call_site() -> None:
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Analog)
    b = Port('b', Direction.IN,  ELECTRICAL, signal_type=Digital)
    with pytest.raises(SignalTypeMismatchError) as exc_info:
        expected_line = _next_line()
        wire(a, b)
    _, lineno = exc_info.value.source_locations[0]
    assert lineno == expected_line


def test_node_merge_error_records_call_sites_for_each_prior_wire() -> None:
    """Merging two pre-existing nets surfaces all involved call sites:
    the current `wire()` plus the two earlier calls whose nodes the
    merge would join."""
    a_out = Port('ao', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    a_bid = Port('ab', Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    b_out = Port('bo', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    b_bid = Port('bb', Direction.BIDIR, ELECTRICAL, signal_type=Digital)

    line_a = _next_line()
    wire(a_out, a_bid)
    line_b = _next_line()
    wire(b_out, b_bid)
    with pytest.raises(NodeMergeError) as exc_info:
        line_merge = _next_line()
        wire(a_bid, b_bid)

    lines = [n for _, n in exc_info.value.source_locations]
    assert line_merge in lines
    assert line_a in lines
    assert line_b in lines


# --------------------------------------------- _validate-time errors


def test_circuit_validate_short_records_source_locations() -> None:
    """`Circuit._validate` walks logical nets; when it raises
    `ShortCircuitError`, the offending `wire()` calls are attributed."""
    from framework.circuit import Circuit
    from components.passives.rail import Rail
    from components.passives.resistor import Resistor

    class Shorted(Circuit):
        def __init__(self) -> None:
            self.hi  = Rail(True)
            self.lo  = Rail(False)
            self.r   = Resistor(330, refdes_number=1)
            wire(self.hi.out, self.r.t1)
            wire(self.lo.out, self.r.t1)
            wire(self.r.t2,   self.lo.out)
            super().__init__()

    with pytest.raises(ShortCircuitError) as exc_info:
        Shorted()
    files = [f for f, _ in exc_info.value.source_locations]
    assert any(
        f.endswith('test_error_with_source_location.py') for f in files
    )
    # Both shorting wire() calls contribute their source location to
    # the offending net, so the attribution includes ≥2 entries.
    assert len(exc_info.value.source_locations) >= 2
