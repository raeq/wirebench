import pytest

from components.passives.variable_capacitor import VariableCapacitor
from framework.units import Farads, Picofarads


def test_construction_with_refdes():
    vc = VariableCapacitor(min_farads=10e-12, max_farads=300e-12, refdes_number=1)
    assert vc.refdes == 'C1'


def test_refdes_prefix():
    assert VariableCapacitor.REFDES_PREFIX == 'C'


def test_value_endpoints():
    vc = VariableCapacitor(min_farads=Picofarads(10), max_farads=Picofarads(300),
                           refdes_number=1)
    assert isinstance(vc.min_farads, Farads)
    assert float(vc.min_farads) == pytest.approx(10e-12)
    assert float(vc.max_farads) == pytest.approx(300e-12)


def test_call_returns_endpoint_pair():
    vc = VariableCapacitor(min_farads=10e-12, max_farads=300e-12, refdes_number=1)
    lo, hi = vc()
    assert isinstance(lo, Farads)
    assert isinstance(hi, Farads)


def test_terminals_are_bidir_analog():
    from framework.port import Direction
    from framework.signals import Analog
    vc = VariableCapacitor(min_farads=10e-12, max_farads=300e-12, refdes_number=1)
    for name in ('t1', 't2'):
        p = vc.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True


def test_negative_value_rejected():
    with pytest.raises(Exception):
        VariableCapacitor(min_farads=-10e-12, max_farads=300e-12, refdes_number=1)
