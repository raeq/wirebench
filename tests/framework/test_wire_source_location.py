"""Every `wire()` call captures its source location and records it on
the resulting `Node`.  The capture is automatic (from the caller's
frame), survives `validate_call`'s pydantic wrapper, and accumulates
across calls that extend an existing node.
"""
from __future__ import annotations

import inspect

from framework.ground import ELECTRICAL
from framework.port import Direction, Port
from framework.signals import Digital
from framework.wire import _wire_with_attribution, wire


def _make_pair() -> tuple[Port, Port]:
    out = Port('o', Direction.OUT, ELECTRICAL, signal_type=Digital)
    inp = Port('i', Direction.IN,  ELECTRICAL, signal_type=Digital)
    return out, inp


def _here() -> int:
    """Return the line number of the *caller's* call to this helper."""
    frame = inspect.currentframe()
    assert frame is not None and frame.f_back is not None
    return frame.f_back.f_lineno


def test_node_records_source_location_from_user_frame() -> None:
    """A bare `wire()` captures the test file and the exact line."""
    out, inp = _make_pair()
    wire(out, inp); expected_line = _here()
    assert out.node is not None
    locs = out.node.source_locations
    assert len(locs) == 1
    filename, lineno = locs[0]
    assert filename.endswith('test_wire_source_location.py'), filename
    assert lineno == expected_line


def test_multiple_wire_calls_accumulate_on_same_node() -> None:
    """When a second `wire()` extends an existing node, both source
    locations are recorded in call order."""
    a_out = Port('ao', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    a_bid = Port('ab', Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    a_in  = Port('ai', Direction.IN,    ELECTRICAL, signal_type=Digital)

    wire(a_out, a_bid);  first_line  = _here()
    wire(a_bid, a_in);   second_line = _here()

    locs = a_out.node.source_locations
    assert len(locs) == 2
    files = [f for f, _ in locs]
    lines = [n for _, n in locs]
    assert all(f.endswith('test_wire_source_location.py') for f in files)
    assert lines == [first_line, second_line]


def test_explicit_source_location_via_internal_helper() -> None:
    """The `.wirebench` loader uses `_wire_with_attribution` directly
    to attribute a reconstructed wire to the user's original source
    line rather than to the loader's own frame."""
    out, inp = _make_pair()
    _wire_with_attribution(
        [out, inp],
        dynamically_driven=False,
        source_location=('hello_led.py', 14),
    )
    assert out.node.source_locations == (('hello_led.py', 14),)


def test_captured_filename_is_basename_for_portability() -> None:
    """Auto-captured source locations store the file *basename*, never
    an absolute path — so `.wirebench` files written on one machine
    stay portable across users / filesystems / CI."""
    import os
    out, inp = _make_pair()
    wire(out, inp)
    filename, _ = out.node.source_locations[0]
    assert filename == 'test_wire_source_location.py'
    assert os.sep not in filename, (
        f"Captured filename should be a basename; got {filename!r}"
    )


def test_internal_helper_with_none_leaves_node_unattributed() -> None:
    """Passing `source_location=None` to the internal helper means *no
    attribution*: the resulting node carries no source location, even
    though we're inside a frame the auto-capture would otherwise grab."""
    out, inp = _make_pair()
    _wire_with_attribution(
        [out, inp],
        dynamically_driven=False,
        source_location=None,
    )
    assert out.node.source_locations == ()


def test_source_locations_is_immutable_tuple() -> None:
    """The public `source_locations` property hands out a tuple — the
    internal list isn't directly exposed."""
    out, inp = _make_pair()
    wire(out, inp)
    locs = out.node.source_locations
    assert isinstance(locs, tuple)
