from components.diodes.d1n4728a import D1N4728A
from framework.diode import Diode
from framework.port import Direction


def test_construction():
    d = D1N4728A(refdes_number=1)
    assert d.refdes == 'D1'


def test_is_diode():
    assert issubclass(D1N4728A, Diode)


def test_refdes_prefix():
    assert D1N4728A.REFDES_PREFIX == 'D'


def test_footprint():
    assert D1N4728A.FOOTPRINT == 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'


def test_ports():
    d = D1N4728A(refdes_number=1)
    assert set(d.ports.keys()) == {'anode', 'cathode'}
    for name in ('anode', 'cathode'):
        assert d.ports[name].direction is Direction.BIDIR


def test_pin_numbers():
    assert D1N4728A.PIN_NUMBERS == {'anode': 1, 'cathode': 2}


def test_call_is_noop():
    assert D1N4728A(refdes_number=1)() is None


def test_repr():
    assert repr(D1N4728A(refdes_number=1)) == "D1N4728A(refdes='D1')"
