import pytest

from digital_thermometer import DigitalThermometer


@pytest.fixture
def thermometer():
    return DigitalThermometer()


def test_bom_present(thermometer):
    """All four placeable parts (U1, U2, U3, R1) appear in the assembly."""
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in thermometer.parts
        if isinstance(fn, RefdesBearing)
    }
    assert "Uno_ThermometerSketch.U1" in parts
    assert "DHT11.U2"                   in parts
    assert "Display5641AS.U3"           in parts
    assert "Resistor.R1"                in parts


def test_phase_0_shows_tens_digit_at_23c(thermometer):
    glyphs = thermometer(23.0, phase=0)
    assert glyphs == ('2', ' ', ' ', ' ')


def test_phase_1_shows_ones_digit_at_23c(thermometer):
    glyphs = thermometer(23.0, phase=1)
    assert glyphs == (' ', '3', ' ', ' ')


def test_phase_2_shows_celsius_indicator(thermometer):
    glyphs = thermometer(23.0, phase=2)
    assert glyphs == (' ', ' ', 'C', ' ')


def test_single_digit_temperature_has_leading_blank(thermometer):
    glyphs = thermometer(5.0, phase=0)
    assert glyphs == (' ', ' ', ' ', ' ')   # tens digit is blank
    glyphs = thermometer(5.0, phase=1)
    assert glyphs == (' ', '5', ' ', ' ')


def test_zero_celsius_renders_blank_zero(thermometer):
    glyphs = thermometer(0.0, phase=0)
    assert glyphs == (' ', ' ', ' ', ' ')
    glyphs = thermometer(0.0, phase=1)
    assert glyphs == (' ', '0', ' ', ' ')


def test_out_of_range_temperature_shows_dashes(thermometer):
    glyphs = thermometer(150.0, phase=0)
    assert glyphs[0] == '-'
    glyphs = thermometer(150.0, phase=1)
    assert glyphs[1] == '-'


def test_repeated_calls_do_not_trip_pin_contention(thermometer):
    """Each phase resets the digit/segment pin drives — no BIDIR
    contention should fire on the chip's output pins between calls."""
    for _ in range(3):
        for phase in range(3):
            thermometer(23.0, phase=phase)


def test_fourth_digit_always_dark(thermometer):
    """DIG_4 is tied to GND, so digit 4 must never show a glyph."""
    for phase in range(3):
        glyphs = thermometer(99.0, phase=phase)
        assert glyphs[3] == ' '


def test_arduino_pd2_wired_to_dht11_data(thermometer):
    """The single-bus wire is in the netlist (both ports share a node)."""
    pd2  = thermometer.arduino.ports['PD2']
    data = thermometer.dht11.ports['DATA']
    assert pd2.node is data.node
    assert pd2.node is not None


def test_arduino_pd3_node_includes_r1_and_display_dig_1(thermometer):
    """R1 is on the wire-list between PD3 and DIG_1 (BOM-faithful)."""
    pd3   = thermometer.arduino.ports['PD3']
    dig_1 = thermometer.display.ports['DIG_1']
    t1    = thermometer.r1.ports['t1']
    t2    = thermometer.r1.ports['t2']
    # All four share the same node.
    assert pd3.node is dig_1.node
    assert t1.node  is pd3.node
    assert t2.node  is pd3.node
