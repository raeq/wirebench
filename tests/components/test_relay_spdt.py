import pytest

from components.relays.spdt import Relay_SPDT
from framework.port import Direction
from framework.signals import Analog
from framework.units import Volts


def test_construction_with_refdes_1():
    k = Relay_SPDT(refdes_number=1)
    assert k.refdes == 'K1'


def test_refdes_prefix():
    assert Relay_SPDT.REFDES_PREFIX == 'K'


def test_footprint():
    assert Relay_SPDT.FOOTPRINT == 'Relay_THT:Relay_SPDT_Generic'


def test_default_pickup_voltage_is_1V():
    k = Relay_SPDT(refdes_number=1)
    assert float(k.pickup_voltage) == 1.0


def test_pickup_voltage_is_configurable():
    k = Relay_SPDT(refdes_number=1, pickup_voltage=Volts(9.0))
    assert float(k.pickup_voltage) == 9.0


def test_starts_at_rest_with_com_on_nc():
    """No coil drive yet — armature is at the spring-rest position."""
    k = Relay_SPDT(refdes_number=1)
    assert k.closed_path == 'nc'
    assert k.energised is False


def test_all_terminals_are_bidir_analog():
    """All five terminals must be BIDIR Analog so wire() accepts both
    Digital control sources and Analog supply rails."""
    k = Relay_SPDT(refdes_number=1)
    for name in ('coil_plus', 'coil_minus', 'com', 'no', 'nc'):
        p = k.ports[name]
        assert p.direction is Direction.BIDIR, name
        assert p.signal_type is Analog, name


def test_pin_numbers_match_expected_layout():
    expected = {'coil_plus': 1, 'coil_minus': 2, 'com': 3, 'no': 4, 'nc': 5}
    assert Relay_SPDT.PIN_NUMBERS == expected


def test_call_picks_up_with_digital_high_drive():
    """Default pickup is 1 V; Digital HIGH canonicalises to 1.0 V via
    the framework so a True drive is exactly at the threshold."""
    k = Relay_SPDT(refdes_number=1)
    assert k(coil_plus=True, coil_minus=False) == 'no'
    assert k.energised is True


def test_call_releases_when_drive_drops_to_zero():
    k = Relay_SPDT(refdes_number=1)
    k(coil_plus=True, coil_minus=False)   # energise
    assert k(coil_plus=False, coil_minus=False) == 'nc'
    assert k.energised is False


def test_call_below_pickup_does_not_close_no():
    """Below the pickup voltage, the spring keeps COM on NC."""
    k = Relay_SPDT(refdes_number=1, pickup_voltage=Volts(2.0))
    assert k(coil_plus=True, coil_minus=False) == 'nc'   # 1 V < 2 V


def test_call_with_analog_supply_voltage():
    k = Relay_SPDT(refdes_number=1, pickup_voltage=Volts(6.0))
    assert k(coil_plus=9.0, coil_minus=0.0) == 'no'


def test_call_with_negative_differential_does_not_close():
    """Differential is signed — only positive coil current picks the
    armature up.  A negative differential is treated as below threshold."""
    k = Relay_SPDT(refdes_number=1)
    assert k(coil_plus=0.0, coil_minus=5.0) == 'nc'


def test_rejects_zero_pickup_voltage():
    with pytest.raises(Exception):
        Relay_SPDT(refdes_number=1, pickup_voltage=0)


def test_str_includes_closed_path():
    k = Relay_SPDT(refdes_number=2)
    k(coil_plus=True, coil_minus=False)
    assert "K2" in str(k)
    assert "NO" in str(k).upper()


def test_repr_includes_state():
    k = Relay_SPDT(refdes_number=2)
    r = repr(k)
    assert "K2" in r
    assert "pickup_voltage=1.0" in r
    assert "closed_path='nc'" in r
