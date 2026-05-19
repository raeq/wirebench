import pytest
from components.passives.resistor import Resistor


def test_ohms_law(shunt):
    # 100 A through 1 Ω → 100 V
    assert shunt(100) == 100


def test_returns_volts(shunt):
    from framework.units import Volts
    assert isinstance(shunt(100), Volts)


def test_scaling():
    # 50 A through 10 Ω → 500 V (V = I × R, consistent units)
    r = Resistor(ohms=10, refdes_number=1)
    assert r(50) == 500


def test_unit_typed_call():
    # Real-world sizing: 10 mA through 330 Ω → 3.3 V
    from framework.units import Milliamps
    r = Resistor(ohms=330, refdes_number=1)
    assert r(Milliamps(10)) == pytest.approx(3.3)


def test_zero_current(shunt):
    assert shunt(0) == 0


def test_call_does_not_drive_terminal_ports():
    # __call__ is a calculator, not an actuator — t2 stays undriven.
    r = Resistor(ohms=10, refdes_number=1)
    r(5)
    assert r.ports['t2'].value is None


def test_repeated_calls_recompute():
    r = Resistor(ohms=10, refdes_number=1)
    assert r(5) == 50
    assert r(7) == 70


def test_port_names():
    r = Resistor(ohms=470, refdes_number=1)
    assert 't1' in r.ports
    assert 't2' in r.ports


def test_repr():
    r = Resistor(ohms=47, refdes_number=1)
    assert repr(r) == "Resistor(ohms=47.0, refdes='R1')"


def test_repr_round_trip_for_unit_inputs():
    from framework.units import Ohms, Kilohms
    assert repr(Resistor(Ohms(47),     refdes_number=1)) == "Resistor(ohms=47.0, refdes='R1')"
    assert repr(Resistor(Kilohms(4.7), refdes_number=2)) == "Resistor(ohms=4700.0, refdes='R2')"


def test_str():
    r = Resistor(ohms=47, refdes_number=1)
    assert str(r) == "47.0 Ω"


def test_terminals_are_mandatory():
    """Both Resistor terminals must be `mandatory=True`. A real
    resistor with a floating terminal does nothing — leaving it
    unwired silently is a physical-fidelity violation that produces
    breadboard layouts where the resistor sits with no jumpers
    attached. Earlier this was `mandatory=False` to let demos declare
    BOM-only timing/decoupling components without wiring them; that
    pattern is exactly the bug this regression test exists to catch."""
    r = Resistor(330, refdes_number=1)
    assert r.ports['t1'].mandatory is True
    assert r.ports['t2'].mandatory is True


def test_floating_resistor_refused_at_circuit_construction():
    """End-to-end: a Circuit that declares a Resistor but doesn't
    wire its terminals raises `UnconnectedPinError` at
    `Circuit.__init__`. Mirrors the LED.cathode regression test."""
    from framework.circuit import Circuit
    from framework.errors import UnconnectedPinError

    class _DanglingResistor(Circuit):
        def __init__(self) -> None:
            self.r = Resistor(330, refdes_number=1)
            super().__init__()

    with pytest.raises(UnconnectedPinError, match='Resistor'):
        _DanglingResistor()
