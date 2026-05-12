"""Tests for `Node.ports` tracking.

`Node` keeps the list of ports attached to it so that callers walking
the wiring graph (notably Circuit's orphan-port detector) can ask any
node for every port joined to it.  Attachment happens automatically via
`Port.connect`, which is itself called from `wire()` and from direct
test-side `Port.connect` invocations.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from framework.ground import ELECTRICAL
from framework.node import Node
from framework.port import Direction, Port
from framework.signals import Digital
from framework.wire import wire


def test_node_tracks_its_attached_ports() -> None:
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.IN,  ELECTRICAL, signal_type=Digital)
    wire(a, b)
    assert a.node is b.node
    assert a.node.ports == (a, b)


def test_node_ports_attachment_order_matches_wire_order() -> None:
    a = Port('a', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    c = Port('c', Direction.IN,    ELECTRICAL, signal_type=Digital)
    wire(a, b)
    wire(b, c)   # c joins the existing a–b node
    assert a.node.ports == (a, b, c)


def test_node_ports_property_returns_tuple() -> None:
    """The property returns an immutable view so callers can't mutate
    the node's internal list."""
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
    n = Node('test', ELECTRICAL)
    a.connect(n)
    assert isinstance(n.ports, tuple)


def test_node_attach_is_private_invocation_only() -> None:
    """`Node._attach` is only invoked from `Port.connect`, which is
    invoked from `wire()` (and from a handful of test-internal direct
    calls).  No production code outside the framework's wiring layer
    should call it directly.

    Verify by grep: in `src/`, the only file with a `node._attach`
    callsite (besides `node.py` itself) is `port.py`.  If a future
    change adds another caller, this test fails and reminds the
    contributor to keep the privilege boundary intact.
    """
    src_root = Path(__file__).resolve().parents[2] / 'src'
    callers: list[Path] = []
    for py in src_root.rglob('*.py'):
        text = py.read_text()
        if '._attach(' in text and py.name != 'node.py':
            callers.append(py.relative_to(src_root))
    # The framework's only legitimate caller is Port.connect.
    assert callers == [Path('framework/port.py')], (
        f"Unexpected `._attach` callers in src/: {callers}"
    )
