import pytest

from components.transducers.speaker import Speaker
from framework.units import Ohms


def test_construction_with_refdes():
    s = Speaker(impedance_ohms=8, refdes_number=1)
    assert s.refdes == 'LS1'
    assert s.refdes_number == 1


def test_default_impedance_is_8_ohms():
    """8 Ω is the de-facto standard moving-coil speaker on the hobby
    bench — same value Penfold's PB107 P9 / P16 designs assume."""
    s = Speaker(refdes_number=1)
    assert float(s.impedance_ohms) == pytest.approx(8.0)


def test_refdes_prefix():
    assert Speaker.REFDES_PREFIX == 'LS'


def test_impedance_property_returns_unit_typed():
    s = Speaker(impedance_ohms=Ohms(4.0), refdes_number=1)
    assert isinstance(s.impedance_ohms, Ohms)
    assert float(s.impedance_ohms) == pytest.approx(4.0)


def test_terminals_are_bidir_analog():
    from framework.port import Direction
    from framework.signals import Analog
    s = Speaker(refdes_number=1)
    for name in ('t1', 't2'):
        p = s.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True


def test_call_returns_impedance():
    s = Speaker(impedance_ohms=32, refdes_number=1)
    assert float(s()) == pytest.approx(32)


def test_negative_impedance_rejected():
    with pytest.raises(Exception):
        Speaker(impedance_ohms=-8, refdes_number=1)


def test_repr_round_trips():
    s = Speaker(impedance_ohms=16, refdes_number=2)
    assert repr(s) == "Speaker(impedance_ohms=16.0, refdes='LS2')"
