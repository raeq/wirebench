import pytest
from framework.ground import GroundDomain, ELECTRICAL
from framework.node import Node
from framework.port import Port, Direction
from framework.signals import Analog, Digital
from framework.wire import wire
from components.cd4043 import CD4043
from components.inverter import Inverter
from components.led import LED
from components.resistor import Resistor


# --- GroundDomain ---

def test_ground_domain_name():
    d = GroundDomain('thermal')
    assert d.name == 'thermal'


def test_distinct_domains_are_not_identical():
    a = GroundDomain('a')
    b = GroundDomain('b')
    assert a is not b


# --- Node ---

def test_node_initial_value_is_none():
    n = Node('v1', ELECTRICAL)
    assert n.value is None


def test_node_drive_sets_value():
    n = Node('v1', ELECTRICAL)
    n.drive(3.3)
    assert n.value == 3.3


# --- Port ---

def test_port_connects_to_same_domain():
    domain = GroundDomain('electrical')
    p = Port('out', Direction.OUT, domain)
    n = Node('v1', domain)
    p.connect(n)
    assert p._node is n


def test_port_rejects_domain_mismatch():
    elec    = GroundDomain('electrical')
    thermal = GroundDomain('thermal')
    p = Port('out', Direction.OUT, elec)
    n = Node('temp', thermal)
    with pytest.raises(ValueError, match="Ground domain mismatch"):
        p.connect(n)


def test_port_drive_writes_to_node():
    p = Port('out', Direction.OUT, ELECTRICAL)
    n = Node('v1', ELECTRICAL)
    p.connect(n)
    p.drive(5.0)
    assert n.value == 5.0


def test_port_value_reads_from_node():
    p = Port('in', Direction.IN, ELECTRICAL)
    n = Node('v1', ELECTRICAL)
    p.connect(n)
    n.drive(2.5)
    assert p.value == 2.5


def test_unconnected_port_stores_value_locally():
    p = Port('in', Direction.IN, ELECTRICAL)
    p.drive(1.8)
    assert p.value == 1.8


# --- Circuit graph evaluation ---

def test_inverter_in_circuit():
    inv = Inverter()
    assert inv(True) is False
    assert inv(False) is True
    assert inv(None) is None


def test_topological_order_is_respected():
    """Inverter must evaluate before LED for the LED to see the inverted signal."""
    from framework.circuit import Circuit
    from framework.wire import wire

    inv = Inverter()
    led = LED('green')

    wire(inv.ports['y'], led.ports['anode'])

    circuit = Circuit(
        factor_nodes=[led, inv],   # deliberately wrong order — circuit must fix it
        inputs={'sig': inv.ports['a']},
        outputs={'out': inv.ports['y']},
    )

    circuit._inputs['sig'].drive(False)
    circuit._evaluate()
    assert led.lit is True   # False → inverted → True → LED on


def test_ground_domain_enforced_at_wiring_time():
    thermal = GroundDomain('thermal')
    elec_port = Port('out', Direction.OUT, ELECTRICAL)
    thermal_node = Node('temp', thermal)
    with pytest.raises(ValueError):
        elec_port.connect(thermal_node)


# --- Structural enforcement ---

def test_wire_requires_one_driver():
    a = Port('a', Direction.IN, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.IN, ELECTRICAL, signal_type=Digital)
    with pytest.raises(ValueError, match="no driver"):
        wire(a, b)


def test_wire_rejects_multiple_drivers():
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.OUT, ELECTRICAL, signal_type=Digital)
    c = Port('c', Direction.IN,  ELECTRICAL, signal_type=Digital)
    with pytest.raises(ValueError, match="short circuit"):
        wire(a, b, c)


def test_wire_rejects_signal_type_mismatch():
    out = Port('out', Direction.OUT, ELECTRICAL, signal_type=Digital)
    inp = Port('inp', Direction.IN,  ELECTRICAL, signal_type=Analog)
    with pytest.raises(ValueError, match="Signal type mismatch"):
        wire(out, inp)


def test_circuit_rejects_unconnected_mandatory_port():
    from framework.circuit import Circuit
    latch = CD4043()
    inv = Inverter()
    wire(inv.ports['y'], latch.ports['r'])   # r is wired
    # s is mandatory, unconnected, and not declared as a boundary port → must raise
    with pytest.raises(ValueError, match="Unconnected mandatory port"):
        Circuit(
            factor_nodes=[inv, latch],
            inputs={'a': inv.ports['a']},
            outputs={'q': latch.ports['q']},
        )


def test_circuit_rejects_short_circuit():
    from framework.circuit import Circuit
    from framework.node import Node
    from framework.port import Port, Direction
    a = Inverter()
    b = Inverter()
    shared = Node('shared', ELECTRICAL)
    a.ports['y'].connect(shared)
    b.ports['y'].connect(shared)
    with pytest.raises(ValueError, match="Short circuit"):
        Circuit(
            factor_nodes=[a, b],
            inputs={'a_in': a.ports['a'], 'b_in': b.ports['a']},
            outputs={'out': a.ports['y']},
        )
