from components.transistors.irlb8721 import IRLB8721
from framework.transistor import MOSFET


def test_construction():
    q = IRLB8721(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert IRLB8721.REFDES_PREFIX == 'Q'


def test_footprint():
    assert IRLB8721.FOOTPRINT == 'Package_TO_SOT_THT:TO-220-3_Vertical'


def test_is_mosfet():
    assert issubclass(IRLB8721, MOSFET)
    assert IRLB8721._SPICE_PREFIX == 'M'
    assert IRLB8721._SPICE_PIN_ORDER == ('d', 'g', 's')


def test_ports():
    q = IRLB8721(refdes_number=1)
    assert set(q.ports.keys()) == {'d', 'g', 's'}


def test_pin_numbers():
    assert IRLB8721.PIN_NUMBERS == {'g': 1, 'd': 2, 's': 3}


def test_call_is_noop():
    assert IRLB8721(refdes_number=1)() is None


def test_repr():
    assert repr(IRLB8721(refdes_number=1)) == "IRLB8721(refdes='Q1')"
