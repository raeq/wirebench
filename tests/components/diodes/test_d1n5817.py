from components.diodes.d1n5817 import D1N5817
from framework.diode import Diode


def test_construction():
    d = D1N5817(refdes_number=1)
    assert d.refdes == 'D1'


def test_refdes_prefix():
    assert D1N5817.REFDES_PREFIX == 'D'


def test_footprint():
    assert D1N5817.FOOTPRINT == 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'


def test_is_diode():
    assert issubclass(D1N5817, Diode)


def test_ports():
    d = D1N5817(refdes_number=1)
    assert set(d.ports.keys()) == {'anode', 'cathode'}


def test_pin_numbers():
    assert D1N5817.PIN_NUMBERS == {'anode': 1, 'cathode': 2}


def test_call_is_noop():
    # D1N5817 is Category A passive — the diode itself models no
    # directional behaviour.  Forward-conduction in a series-rectifier
    # role is provided by a `SeriesRectifier` cell wired alongside the
    # diode in the circuit; see docs/behavioural-cell-audit-spec.md §7.2.2.
    assert D1N5817(refdes_number=1)() is None


def test_repr():
    assert repr(D1N5817(refdes_number=1)) == "D1N5817(refdes='D1')"
