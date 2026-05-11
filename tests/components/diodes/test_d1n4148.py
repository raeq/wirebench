from components.diodes.d1n4148 import D1N4148
from framework.diode import Diode


def test_construction():
    d = D1N4148(refdes_number=1)
    assert d.refdes == 'D1'


def test_refdes_prefix():
    assert D1N4148.REFDES_PREFIX == 'D'


def test_footprint():
    assert D1N4148.FOOTPRINT == 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'


def test_is_diode():
    assert issubclass(D1N4148, Diode)


def test_ports():
    d = D1N4148(refdes_number=1)
    assert set(d.ports.keys()) == {'anode', 'cathode'}


def test_pin_numbers():
    assert D1N4148.PIN_NUMBERS == {'anode': 1, 'cathode': 2}


def test_call_is_noop():
    assert D1N4148(refdes_number=1)() is None


def test_repr():
    assert repr(D1N4148(refdes_number=1)) == "D1N4148(refdes='D1')"
