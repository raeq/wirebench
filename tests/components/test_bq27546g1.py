import pytest

from components.chips.bq27546g1 import BQ27546G1
from components.chips.concepts.fuel_gauge import FuelGauge
from framework.port import Direction
from framework.signals import Analog, Digital


EXPECTED_PINS = (
    ( 1, 'SRP',   Direction.IN,    Analog),
    ( 2, 'HDQ',   Direction.BIDIR, Digital),
    ( 3, 'SCL',   Direction.IN,    Digital),
    ( 4, 'SRN',   Direction.IN,    Analog),
    ( 5, 'TS',    Direction.IN,    Analog),
    ( 6, 'SDA',   Direction.BIDIR, Digital),
    ( 7, 'VSS',   Direction.IN,    Analog),
    ( 8, 'VSS',   Direction.IN,    Analog),
    ( 9, 'SE',    Direction.OUT,   Digital),
    (10, 'VCC',   Direction.OUT,   Analog),
    (11, 'CE',    Direction.IN,    Digital),
    (12, 'NC1',   Direction.IN,    Digital),
    (13, 'REGIN', Direction.IN,    Analog),
    (14, 'BAT',   Direction.IN,    Analog),
    (15, 'NC2',   Direction.IN,    Digital),
)


def test_construction_with_refdes_1():
    ic = BQ27546G1(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert BQ27546G1.REFDES_PREFIX == 'U'


def test_pin_count():
    ic = BQ27546G1(refdes_number=1)
    assert len(ic.pins) == 15


def test_pin_numbers_and_names_match_datasheet():
    ic = BQ27546G1(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, *_ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = BQ27546G1(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction, _ in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_has_one_internal_fuel_gauge_cell():
    ic = BQ27546G1(refdes_number=1)
    gauges = [fn for fn in ic.parts if isinstance(fn, FuelGauge)]
    assert len(gauges) == 1


def test_call_at_full_charge():
    ic = BQ27546G1(refdes_number=1)
    out = ic(4.2)
    assert out['state_of_charge'] == pytest.approx(1.0)
    assert out['SE'] is True


def test_call_at_mid_charge():
    ic = BQ27546G1(refdes_number=1)
    out = ic(3.7)
    assert out['state_of_charge'] == pytest.approx(0.5)
    assert out['SE'] is True


def test_call_at_empty():
    ic = BQ27546G1(refdes_number=1)
    out = ic(3.0)
    assert out['state_of_charge'] == 0.0
    assert out['SE'] is False


def test_call_undriven():
    ic = BQ27546G1(refdes_number=1)
    out = ic()
    assert out['state_of_charge'] == 0.0
    assert out['SE'] is None


def test_vcc_pin_drives_2_5v_when_running():
    ic = BQ27546G1(refdes_number=1)
    ic(4.0)
    assert ic.ports['VCC'].value == pytest.approx(2.5)


def test_state_of_charge_property():
    ic = BQ27546G1(refdes_number=1)
    ic(3.7)
    assert ic.state_of_charge == pytest.approx(0.5)


def test_repr():
    assert repr(BQ27546G1(refdes_number=1)) == "BQ27546G1(refdes='U1')"


def test_two_vss_pins_disambiguated_in_ports():
    """The chip has two physical VSS pads.  Both must be reachable
    under disambiguated names so the demo can tie both to GND."""
    ic = BQ27546G1(refdes_number=1)
    assert 'VSS_1' in ic.ports
    assert 'VSS_2' in ic.ports
