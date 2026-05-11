from components.transistors.q2n7000 import Q2N7000
from framework.transistor import MOSFET


def test_construction():
    q = Q2N7000(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert Q2N7000.REFDES_PREFIX == 'Q'


def test_footprint():
    assert Q2N7000.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_mosfet():
    assert issubclass(Q2N7000, MOSFET)
    assert Q2N7000._SPICE_PREFIX == 'M'
    assert Q2N7000._SPICE_PIN_ORDER == ('d', 'g', 's')


def test_ports():
    q = Q2N7000(refdes_number=1)
    assert set(q.ports.keys()) == {'d', 'g', 's'}


def test_pin_numbers():
    assert Q2N7000.PIN_NUMBERS == {'s': 1, 'g': 2, 'd': 3}


def test_call_is_noop():
    assert Q2N7000(refdes_number=1)() is None


def test_repr():
    assert repr(Q2N7000(refdes_number=1)) == "Q2N7000(refdes='Q1')"
