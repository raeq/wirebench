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


def test_call_models_forward_conduction():
    # The 1N5817 now wraps a `DiodeForward` cell with V_F = 0.3 V
    # (Schottky drop).  Above V_F, the cathode tracks anode minus the
    # drop; at or below V_F, the cell holds the cathode at 0 V.
    d = D1N5817(refdes_number=1)
    assert d(5.0) == 4.7
    d2 = D1N5817(refdes_number=2)
    assert d2(0.1) == 0.0   # below the 0.3 V threshold


def test_call_with_no_anode_returns_default_cathode():
    # Calling with no anode argument leaves the cell with a zero
    # anode (the cell's evaluate() defaults None → 0.0), so the
    # cathode reads 0.0 V — the diode is "off".
    assert D1N5817(refdes_number=1)() == 0.0


def test_repr():
    assert repr(D1N5817(refdes_number=1)) == "D1N5817(refdes='D1')"
