import pytest
from framework.ground import GroundDomain, ELECTRICAL
from framework.node import Node
from framework.port import Port, Direction
from framework.signals import Analog, Digital
from framework.wire import wire
from components.parts.cd4043 import CD4043
from components.parts.concepts.nor_latch import NORLatch
from components.parts.sn74hc04 import SN74HC04
from components.passives.led import LED
from components.passives.resistor import Resistor


# --- GroundDomain ---

def test_ground_domain_name():
    d = GroundDomain('thermal')
    assert d.name == 'thermal'


def test_distinct_domains_are_not_identical():
    a = GroundDomain('a')
    b = GroundDomain('b')
    assert a is not b


def test_same_name_returns_same_instance():
    x = GroundDomain('optical')
    y = GroundDomain('optical')
    assert x is y


def test_ground_domain_is_electrical_singleton():
    assert GroundDomain('electrical') is ELECTRICAL


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


def test_drive_coerces_to_signal_type_digital():
    # Digital ports canonicalise truthy values to Python bool.
    p = Port('d', Direction.IN, ELECTRICAL, signal_type=Digital)
    p.drive(1)
    assert p.value is True
    p.drive(0)
    assert p.value is False


def test_drive_preserves_none_as_high_z():
    # None is the high-impedance sentinel — never coerced to Digital(0)/False.
    p = Port('d', Direction.IN, ELECTRICAL, signal_type=Digital)
    p.drive(None)
    assert p.value is None


def test_drive_coerces_to_analog_subtype():
    from framework.units import Volts
    p = Port('v', Direction.IN, ELECTRICAL, signal_type=Volts)
    p.drive(5)             # plain int
    assert isinstance(p.value, Volts)
    assert float(p.value) == 5.0


def test_drive_rejects_uncoercible_value():
    from framework.units import Volts
    p = Port('v', Direction.IN, ELECTRICAL, signal_type=Volts)
    with pytest.raises(TypeError, match="port 'v' expects Volts"):
        p.drive("not a number")


# --- Circuit graph evaluation ---

def test_sn74hc04_inverts_channel_1():
    chip = SN74HC04()
    assert chip(True)[0] is False
    assert chip(False)[0] is True
    assert chip(None)[0] is None


def test_topological_order_is_respected():
    """A logic gate must evaluate before its downstream load reads its output."""
    from framework.circuit import Circuit
    from framework.wire import wire

    chip = SN74HC04()
    led = LED('green')

    wire(chip.ports['y_1'], led.ports['anode'])

    circuit = Circuit(
        factor_nodes=[led, chip],   # deliberately wrong order — circuit must fix it
        ports={'sig': chip.ports['a_1'], 'out': chip.ports['y_1']},
    )

    circuit._ports['sig'].drive(False)
    circuit.evaluate()
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
    latch = NORLatch()
    chip = SN74HC04()
    wire(chip.ports['y_1'], latch.ports['r'])   # r is wired
    # s is mandatory, unconnected, and not declared as a boundary port → must raise
    with pytest.raises(ValueError, match="Unconnected mandatory port"):
        Circuit(
            factor_nodes=[chip, latch],
            ports={'a': chip.ports['a_1'], 'q': latch.ports['q']},
        )


def test_circuit_rejects_short_circuit():
    from framework.circuit import Circuit
    from framework.node import Node
    a = SN74HC04()
    b = SN74HC04()
    shared = Node('shared', ELECTRICAL)
    a.ports['y_1'].connect(shared)
    b.ports['y_1'].connect(shared)
    with pytest.raises(ValueError, match="Short circuit"):
        Circuit(
            factor_nodes=[a, b],
            ports={'a_in': a.ports['a_1'], 'b_in': b.ports['a_1'],
                   'out':  a.ports['y_1']},
        )
