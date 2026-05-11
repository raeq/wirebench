from components.transistors.irfz44n import IRFZ44N
from framework.transistor import MOSFET


def test_construction():
    q = IRFZ44N(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert IRFZ44N.REFDES_PREFIX == 'Q'


def test_footprint():
    assert IRFZ44N.FOOTPRINT == 'Package_TO_SOT_THT:TO-220-3_Vertical'


def test_is_mosfet():
    assert issubclass(IRFZ44N, MOSFET)
    assert IRFZ44N._SPICE_PREFIX == 'M'
    assert IRFZ44N._SPICE_PIN_ORDER == ('d', 'g', 's')


def test_ports():
    q = IRFZ44N(refdes_number=1)
    assert set(q.ports.keys()) == {'d', 'g', 's'}


def test_pin_numbers():
    assert IRFZ44N.PIN_NUMBERS == {'g': 1, 'd': 2, 's': 3}


def test_call_is_noop():
    assert IRFZ44N(refdes_number=1)() is None


def test_repr():
    assert repr(IRFZ44N(refdes_number=1)) == "IRFZ44N(refdes='Q1')"
