from components.transistors.bc548 import BC548
from framework.transistor import BJT


def test_construction():
    q = BC548(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert BC548.REFDES_PREFIX == 'Q'


def test_footprint():
    assert BC548.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_bjt():
    assert issubclass(BC548, BJT)
    assert BC548._SPICE_PREFIX == 'Q'
    assert BC548._SPICE_PIN_ORDER == ('c', 'b', 'e')


def test_ports():
    q = BC548(refdes_number=1)
    assert set(q.ports.keys()) == {'c', 'b', 'e'}


def test_pin_numbers():
    assert BC548.PIN_NUMBERS == {'c': 1, 'b': 2, 'e': 3}


def test_call_is_noop():
    assert BC548(refdes_number=1)() is None


def test_repr():
    assert repr(BC548(refdes_number=1)) == "BC548(refdes='Q1')"
