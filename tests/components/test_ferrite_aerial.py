import pytest

from components.passives.ferrite_aerial import FerriteAerial
from framework.units import Henries, Microhenries


def test_construction_with_refdes():
    fa = FerriteAerial(henries=400e-6, refdes_number=1)
    assert fa.refdes == 'L1'


def test_refdes_prefix_l():
    """Ferrite aerial is an inductor at heart — refdes prefix L."""
    assert FerriteAerial.REFDES_PREFIX == 'L'


def test_henries_property():
    fa = FerriteAerial(henries=Microhenries(400), refdes_number=1)
    assert isinstance(fa.henries, Henries)
    assert float(fa.henries) == pytest.approx(400e-6)


def test_terminals_are_bidir_analog():
    from framework.port import Direction
    from framework.signals import Analog
    fa = FerriteAerial(henries=400e-6, refdes_number=1)
    for name in ('t1', 't2'):
        p = fa.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True


def test_call_returns_henries():
    fa = FerriteAerial(henries=400e-6, refdes_number=1)
    assert float(fa()) == pytest.approx(400e-6)
