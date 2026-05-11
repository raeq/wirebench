from components.transistors.bc547 import BC547
from framework.transistor import BJT


def test_construction():
    q = BC547(refdes_number=1)
    assert q.refdes == 'Q1'


def test_refdes_prefix():
    assert BC547.REFDES_PREFIX == 'Q'


def test_footprint():
    assert BC547.FOOTPRINT == 'Package_TO_SOT_THT:TO-92_Inline'


def test_is_bjt():
    assert issubclass(BC547, BJT)
    assert BC547._SPICE_PREFIX == 'Q'
    assert BC547._SPICE_PIN_ORDER == ('c', 'b', 'e')


def test_ports():
    q = BC547(refdes_number=1)
    assert set(q.ports.keys()) == {'c', 'b', 'e'}


def test_pin_numbers():
    assert BC547.PIN_NUMBERS == {'c': 1, 'b': 2, 'e': 3}


def test_call_is_noop():
    assert BC547(refdes_number=1)() is None


def test_repr():
    assert repr(BC547(refdes_number=1)) == "BC547(refdes='Q1')"
