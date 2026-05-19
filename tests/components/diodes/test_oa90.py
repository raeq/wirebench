import pytest

from components.diodes.oa90 import D_OA90


def test_construction_with_refdes():
    d = D_OA90(refdes_number=1)
    assert d.refdes == 'D1'


def test_refdes_prefix():
    assert D_OA90.REFDES_PREFIX == 'D'


def test_germanium_forward_voltage():
    """V_F at room temperature is the *whole* reason for picking the
    OA90 over silicon: ~0.2 V vs the 1N4148's ~0.7 V.  That difference
    is what makes a crystal radio work."""
    assert D_OA90.V_F == pytest.approx(0.2)
    # The 1N4148's nominal V_F is 0.7 V — confirm the germanium one
    # is genuinely lower.
    assert D_OA90.V_F < 0.4


def test_terminals_are_bidir_analog():
    from framework.port import Direction
    from framework.signals import Analog
    d = D_OA90(refdes_number=1)
    for name in ('anode', 'cathode'):
        p = d.ports[name]
        assert p.direction is Direction.BIDIR
        assert p.signal_type is Analog
        assert p.mandatory is True


def test_pin_numbers():
    assert D_OA90.PIN_NUMBERS == {'anode': 1, 'cathode': 2}


def test_repr():
    d = D_OA90(refdes_number=3)
    assert repr(d) == "D_OA90(refdes='D3')"
