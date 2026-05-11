from components.transistors.bc557 import BC557
from framework.transistor import BJT


def test_construction():
    q = BC557(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert BC557.REFDES_PREFIX == 'Q'


def test_footprint():
    assert BC557.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_bjt():
    assert issubclass(BC557, BJT)
    assert BC557._SPICE_PREFIX == 'Q'
    assert BC557._SPICE_PIN_ORDER == ('c', 'b', 'e')


def test_ports():
    q = BC557(refdes_number=1)
    assert set(q.ports.keys()) == {'c', 'b', 'e'}


def test_pin_numbers():
    assert BC557.PIN_NUMBERS == {'c': 1, 'b': 2, 'e': 3}


def test_call_is_noop():
    assert BC557(refdes_number=1)() is None


def test_repr():
    assert repr(BC557(refdes_number=1)) == "BC557(refdes='Q1')"
