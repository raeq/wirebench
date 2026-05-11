from components.transistors.bs170 import BS170
from framework.transistor import MOSFET


def test_construction():
    q = BS170(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert BS170.REFDES_PREFIX == 'Q'


def test_footprint():
    assert BS170.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_mosfet():
    assert issubclass(BS170, MOSFET)
    assert BS170._SPICE_PREFIX == 'M'
    assert BS170._SPICE_PIN_ORDER == ('d', 'g', 's')


def test_ports():
    q = BS170(refdes_number=1)
    assert set(q.ports.keys()) == {'d', 'g', 's'}


def test_pin_numbers():
    assert BS170.PIN_NUMBERS == {'d': 1, 'g': 2, 's': 3}


def test_call_is_noop():
    assert BS170(refdes_number=1)() is None


def test_repr():
    assert repr(BS170(refdes_number=1)) == "BS170(refdes='Q1')"
