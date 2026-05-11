from components.transistors.q2n3904 import Q2N3904
from framework.transistor import BJT


def test_construction():
    q = Q2N3904(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert Q2N3904.REFDES_PREFIX == 'Q'


def test_footprint():
    assert Q2N3904.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_bjt():
    assert issubclass(Q2N3904, BJT)
    assert Q2N3904._SPICE_PREFIX == 'Q'
    assert Q2N3904._SPICE_PIN_ORDER == ('c', 'b', 'e')


def test_ports():
    q = Q2N3904(refdes_number=1)
    assert set(q.ports.keys()) == {'c', 'b', 'e'}


def test_pin_numbers():
    assert Q2N3904.PIN_NUMBERS == {'e': 1, 'b': 2, 'c': 3}


def test_call_is_noop():
    assert Q2N3904(refdes_number=1)() is None


def test_repr():
    assert repr(Q2N3904(refdes_number=1)) == "Q2N3904(refdes='Q1')"
