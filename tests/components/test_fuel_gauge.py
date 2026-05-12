import pytest

from components.chips.concepts.fuel_gauge import FuelGauge
from framework.port import Direction


def test_full_voltage_reads_full_soc():
    g = FuelGauge()
    out = g(4.2)
    assert out['state_of_charge'] == pytest.approx(1.0)


def test_mid_voltage_reads_mid_soc():
    g = FuelGauge()
    out = g(3.7)
    assert out['state_of_charge'] == pytest.approx(0.5)


def test_empty_voltage_reads_zero_soc():
    g = FuelGauge()
    out = g(3.0)
    assert out['state_of_charge'] == 0.0


def test_se_high_when_above_threshold():
    g = FuelGauge(shutdown_threshold=0.05)
    out = g(3.7)
    assert out['se'] is True


def test_se_low_when_below_threshold():
    g = FuelGauge(shutdown_threshold=0.05)
    out = g(3.01)   # well below 5 % SoC
    assert out['se'] is False


def test_se_low_exactly_at_threshold():
    """SE goes LOW *at or below* the threshold — strict greater-than.
    At 3.4 V the inverse curve hits an anchor point exactly (no
    interpolation rounding) so SoC = 0.10 lands precisely on the
    threshold and SE is LOW."""
    g = FuelGauge(shutdown_threshold=0.10)
    out = g(3.4)
    assert out['se'] is False


def test_undriven_bat_leaves_se_undriven():
    g = FuelGauge()
    out = g(None)
    assert out['se'] is None
    assert out['state_of_charge'] == 0.0


def test_vcc_out_holds_2_5v_when_running():
    g = FuelGauge()
    g(4.0)
    assert g.ports['vcc_out'].value == pytest.approx(FuelGauge.VREG25_VOLTAGE)


def test_vcc_out_undriven_when_bat_undriven():
    g = FuelGauge()
    g(None)
    assert g.ports['vcc_out'].value is None


def test_input_ports_are_in():
    g = FuelGauge()
    for name in ('bat', 'ts', 'srp', 'srn'):
        assert g.ports[name].direction is Direction.IN


def test_output_ports_are_out():
    g = FuelGauge()
    assert g.ports['vcc_out'].direction is Direction.OUT
    assert g.ports['se'].direction is Direction.OUT


def test_configurable_shutdown_threshold():
    g = FuelGauge(shutdown_threshold=0.50)
    assert g.shutdown_threshold == 0.50


def test_state_of_charge_property_tracks_latest_evaluate():
    g = FuelGauge()
    g(3.7)
    assert g.state_of_charge == pytest.approx(0.5)
    g(4.2)
    assert g.state_of_charge == pytest.approx(1.0)


def test_repr_includes_soc_and_threshold():
    g = FuelGauge(shutdown_threshold=0.10)
    g(3.7)
    r = repr(g)
    assert '0.5' in r
    assert '0.1' in r
