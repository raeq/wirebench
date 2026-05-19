import pytest
from components.passives.led import LED


def test_initially_undriven(red_led):
    # Power-on with no signal: lit is None, not False (parity with comparator).
    assert red_led.lit is None


def test_true_signal_lights(red_led):
    red_led(True)
    assert red_led.lit is True


def test_false_signal_extinguishes(red_led):
    red_led(True)
    red_led(False)
    assert red_led.lit is False


def test_none_signal_returns_to_undriven(red_led):
    red_led(True)
    red_led(None)
    assert red_led.lit is None


def test_lit_is_readonly(red_led):
    with pytest.raises(AttributeError):
        red_led.lit = True


def test_str_on(red_led):
    red_led(True)
    assert str(red_led) == "red: ON"


def test_str_undriven(red_led):
    assert str(red_led) == "red: ?"


def test_str_off(red_led):
    red_led(False)
    assert str(red_led) == "red: OFF"


def test_repr(red_led):
    assert repr(red_led) == "LED(color='red', lit=None, refdes='D1')"


def test_cathode_port_exists(red_led):
    assert 'cathode' in red_led.ports


def test_cathode_high_prevents_lighting(red_led):
    # anode HIGH but cathode also HIGH → no voltage drop → LED off
    red_led.ports['cathode'].drive(True)
    red_led(True)
    assert red_led.lit is False


def test_physics_constants_present():
    assert hasattr(LED, 'V_F')
    assert hasattr(LED, 'I_F_TYP')
    assert hasattr(LED, 'I_F_MAX')
    assert LED.V_F > 0
    assert LED.I_F_MAX > LED.I_F_TYP


def test_anode_and_cathode_are_both_mandatory(red_led):
    """Regression: an LED with a floating cathode does not light at the
    bench — leaving it unconnected silently is a physical-fidelity
    violation. Both ports must be declared mandatory so the framework
    refuses the bug at construction time, not at the bench.

    Discovered when the breadboard visualiser drew WaterAlarm with no
    ground connection to either LED's cathode: the rendered SVG was
    technically faithful (the source had no `wire()` for the cathode)
    but matched a circuit that wouldn't light. The fix is to enforce
    cathode-must-be-wired at the framework layer."""
    assert red_led.ports['anode'].mandatory, (
        "LED.anode must be mandatory: a real LED with a floating anode "
        "has no driver and cannot light."
    )
    assert red_led.ports['cathode'].mandatory, (
        "LED.cathode must be mandatory: a real LED with a floating "
        "cathode has no return path to ground and cannot light. "
        "Allowing the cathode to default to GND is a physical-fidelity "
        "violation."
    )


def test_floating_cathode_refused_at_circuit_construction():
    """End-to-end: a Circuit that wires only the LED's anode (and
    leaves the cathode floating) must fail at `Circuit.__init__` with
    UnconnectedPinError naming the cathode.

    This is the test that would have caught the WaterAlarm regression
    — assembly_guide / kicad_sch / etc. happily exported the broken
    design because the framework's validator silently tolerated the
    floating cathode."""
    from framework.circuit import Circuit
    from framework.errors import UnconnectedPinError
    from framework.wire import wire
    from components.passives.rail import Rail

    class _DanglingCathode(Circuit):
        def __init__(self) -> None:
            self.vcc = Rail(True)
            self.led = LED('red', refdes_number=1)
            wire(self.vcc.out, self.led.anode)
            # Cathode deliberately left floating.
            super().__init__()

    with pytest.raises(UnconnectedPinError, match='LED.cathode'):
        _DanglingCathode()
