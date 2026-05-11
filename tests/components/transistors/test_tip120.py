from components.transistors.tip120 import TIP120
from framework.transistor import BJT


def test_construction():
    q = TIP120(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert TIP120.REFDES_PREFIX == 'Q'


def test_footprint():
    assert TIP120.FOOTPRINT == 'Package_TO_SOT_THT:TO-220-3_Vertical'


def test_is_bjt():
    assert issubclass(TIP120, BJT)
    assert TIP120._SPICE_PREFIX == 'Q'
    assert TIP120._SPICE_PIN_ORDER == ('c', 'b', 'e')


def test_ports():
    q = TIP120(refdes_number=1)
    assert set(q.ports.keys()) == {'c', 'b', 'e'}


def test_pin_numbers():
    assert TIP120.PIN_NUMBERS == {'b': 1, 'c': 2, 'e': 3}


def test_call_is_noop():
    assert TIP120(refdes_number=1)() is None


def test_repr():
    assert repr(TIP120(refdes_number=1)) == "TIP120(refdes='Q1')"
