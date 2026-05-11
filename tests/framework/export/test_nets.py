"""Logical-net walker tests — extracted compute_logical_nets()."""
import warnings

import pytest

# Trigger component registration so loader/walker see every class.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.board      # noqa: F401

from framework.circuit import Circuit
from framework.export.nets import LogicalNet, compute_logical_nets
from framework.pin import Pin

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def test_compute_logical_nets_returns_LogicalNet_instances():
    design = _silently(WaterAlarm)
    nets = compute_logical_nets(design)
    assert all(isinstance(n, LogicalNet) for n in nets)
    assert all(isinstance(n.nodes, frozenset) for n in nets)
    assert all(isinstance(n.ports, tuple) for n in nets)


def test_compute_logical_nets_assigns_unique_ids():
    design = _silently(WaterAlarm)
    nets = compute_logical_nets(design)
    ids = [n.id for n in nets]
    assert ids == sorted(ids)              # increasing
    assert len(ids) == len(set(ids))       # unique


def test_conductors_excluded_from_port_list():
    """`LogicalNet.ports` lists only real (non-conductor) ports — Pin
    faces are conductors and must not appear."""
    design = _silently(WaterAlarm)
    nets = compute_logical_nets(design)
    for net in nets:
        for owner, _ in net.ports:
            assert not getattr(owner, 'IS_CONDUCTOR', False), \
                f"Pin/Conductor leaked into net.ports: {owner!r}"


def test_mated_assembly_collapses_pins_into_one_net():
    """A mated assembly's wired pins collapse into one logical net per
    pair (sensor side + controller side share the same extended net)."""
    asm = _silently(WaterAlarmAssembly)
    nets = compute_logical_nets(asm)

    # WaterAlarmAssembly wires 4 sensor-data lines through the header
    # (probes p3/p4 + conditioned outputs p5/p6). Each is one logical
    # net spanning both boards, not two.
    real_port_counts = sorted(len(n.ports) for n in nets if len(n.ports) > 1)
    # At minimum a few nets must have ports from both boards. We assert
    # cross-board membership: at least one net has ports owned by
    # components on the sensor side AND the controller side.
    # Cells inside the chips show up as the "real" ports on each net
    # (the chip's package pin is itself a conductor and is excluded).
    # The sensor's DarlingtonChannel feeds either the controller's
    # NORLatch (set line, via the inverter chain) or its Inverter (the
    # reset line, before inversion). Either pairing is proof the net
    # spans both boards.
    cross_board = []
    for net in nets:
        type_names = {type(o).__name__ for o, _ in net.ports}
        if 'DarlingtonChannel' in type_names and (
            'NORLatch' in type_names or 'Inverter' in type_names
        ):
            cross_board.append(net)
    assert cross_board, \
        "Expected at least one logical net spanning both boards via the header mate"


def test_validate_still_catches_shorts_via_extracted_walker():
    """Regression: Circuit._validate now delegates to compute_logical_nets;
    a cross-conductor short (two OUT drivers tied through a Pin) is
    only caught by the logical-net walker — wire() can't see it because
    it inspects each individual wire() call, not the joined extended
    net.
    """
    from components.passives.rail import Rail
    from framework.connector import Connector
    from framework.wire import wire
    from components.connectors.headers import Header2xNFemale
    # Two Rail(True) drivers tied through a connector pin: one drives
    # the pin's external face, the other drives the internal face.
    # wire() sees two independent calls; only compute_logical_nets
    # joins them into one net with two OUT ports → short.
    conn = Header2xNFemale(pin_count=1, pitch_mm=2.54, refdes_number=1)
    vcc1 = Rail(True)
    vcc2 = Rail(True)
    # Both faces of a connector pin become writers if both rails drive
    # them. wire() is called once per face, so each call individually
    # is legal.
    pin = conn.pins[0]
    wire(vcc1.ports['out'], pin.external)
    wire(vcc2.ports['out'], pin.internal)
    with pytest.raises(ValueError, match='Short circuit'):
        Circuit(factor_nodes=[conn, vcc1, vcc2], ports={})
