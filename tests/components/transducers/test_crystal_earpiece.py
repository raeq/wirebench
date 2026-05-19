import pytest

from components.transducers.crystal_earpiece import CrystalEarpiece
from framework.units import Ohms


def test_construction_with_refdes():
    e = CrystalEarpiece(refdes_number=1)
    assert e.refdes == 'LS1'


def test_default_impedance_is_32k():
    """Crystal earpieces present tens of kΩ at 1 kHz — 32 kΩ is the
    canonical mid-band value used in the crystal-radio literature."""
    e = CrystalEarpiece(refdes_number=1)
    assert float(e.impedance_ohms) == pytest.approx(32_000)


def test_refdes_prefix():
    assert CrystalEarpiece.REFDES_PREFIX == 'LS'


def test_terminals_are_bidir_analog():
    from framework.port import Direction
    from framework.signals import Analog
    e = CrystalEarpiece(refdes_number=1)
    for name in ('t1', 't2'):
        p = e.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True


def test_call_returns_impedance():
    e = CrystalEarpiece(impedance_ohms=50_000, refdes_number=1)
    assert float(e()) == pytest.approx(50_000)


def test_high_impedance_distinguishes_from_speaker():
    """Crystal earpieces are characterised by their high impedance —
    orders of magnitude greater than a moving-coil speaker.  This
    is the *teaching point*: a crystal radio runs on microwatts and
    needs the high impedance to extract any audible level."""
    e = CrystalEarpiece(refdes_number=1)
    assert float(e.impedance_ohms) > 10_000
