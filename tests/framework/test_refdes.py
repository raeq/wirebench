import pytest

from framework.refdes import IEEE_315_PREFIXES, validate_refdes
from components.passives.resistor import Resistor
from components.passives.led import LED
from components.chips.sn74hc04 import SN74HC04
from components.chips.cd4069 import CD4069
from components.chips.cd4043 import CD4043
from components.chips.lm393 import LM393
from components.chips.uln2003a import ULN2003A
from components.chips.concepts.inverter import Inverter
from components.chips.concepts.nor_latch import NORLatch
from components.chips.concepts.tristate_buffer import TriStateBuffer
from components.chips.concepts.comparator import Comparator
from components.chips.concepts.darlington_channel import DarlingtonChannel


# --- Happy path ---

def test_resistor_refdes_is_R_prefix():
    assert Resistor(330, refdes_number=1).refdes == 'R1'


def test_led_refdes_uses_diode_prefix_D_not_LED():
    # IEEE 315: LEDs are diodes; refdes prefix is D, not LED.
    assert LED('red', refdes_number=2).refdes == 'D2'


def test_chip_refdes_is_U_prefix():
    for cls in (SN74HC04, CD4069, CD4043, LM393, ULN2003A):
        assert cls(refdes_number=3).refdes == 'U3', cls.__name__


def test_refdes_number_property_exposes_int():
    r = Resistor(330, refdes_number=42)
    assert r.refdes_number == 42


# --- Construction errors ---

def test_missing_refdes_number_raises_type_error():
    with pytest.raises(TypeError):
        Resistor(330)        # missing required keyword arg


@pytest.mark.parametrize("bad", [0, -1, 1.0, True, '1', None])
def test_non_positive_int_refdes_number_rejected(bad):
    with pytest.raises((ValueError, TypeError)):
        Resistor(330, refdes_number=bad)


def test_unknown_prefix_rejected_at_construction():
    # A subclass with an invalid REFDES_PREFIX fails at instantiation,
    # because validate_refdes runs before any other side effects.
    class _BadChip(Resistor):
        REFDES_PREFIX = 'XX'   # not in IEEE 315
    with pytest.raises(ValueError, match="Unknown refdes prefix"):
        _BadChip(330, refdes_number=1)


def test_validate_refdes_helper_directly():
    validate_refdes('R', 1)         # OK
    with pytest.raises(ValueError, match="Unknown refdes prefix"):
        validate_refdes('XX', 1)
    with pytest.raises(ValueError, match="positive int"):
        validate_refdes('R', 0)
    with pytest.raises(ValueError, match="positive int"):
        validate_refdes('R', True)


def test_ieee_315_prefixes_contains_codebase_prefixes():
    for prefix in ('R', 'D', 'U'):
        assert prefix in IEEE_315_PREFIXES


# --- Cells carry no refdes ---

@pytest.mark.parametrize("cell_cls", [
    Inverter, NORLatch, TriStateBuffer, Comparator, DarlingtonChannel,
])
def test_cell_has_no_refdes_prefix_attribute(cell_cls):
    assert not hasattr(cell_cls, 'REFDES_PREFIX'), cell_cls.__name__


@pytest.mark.parametrize("cell_cls", [
    Inverter, NORLatch, TriStateBuffer, Comparator, DarlingtonChannel,
])
def test_cell_constructor_rejects_refdes_number(cell_cls):
    with pytest.raises(TypeError):
        cell_cls(refdes_number=1)


# --- refdes is read-only ---

def test_refdes_property_has_no_setter():
    r = Resistor(330, refdes_number=1)
    with pytest.raises(AttributeError):
        r.refdes = 'R9'


# --- Duplicate detection in Circuit._validate ---

def test_duplicate_refdes_within_composite_rejected():
    from framework.circuit import Circuit
    r1 = Resistor(330, refdes_number=1)
    r2 = Resistor(330, refdes_number=1)
    with pytest.raises(ValueError, match="Duplicate refdes"):
        Circuit(factor_nodes=[r1, r2], ports={})


def test_distinct_prefixes_with_same_number_do_not_collide():
    # R1 and U1 share a number but differ on prefix — fine.
    from framework.circuit import Circuit
    r = Resistor(330, refdes_number=1)
    u = SN74HC04(refdes_number=1)
    Circuit(factor_nodes=[r, u], ports={})   # must not raise


# --- __repr__ surfaces refdes ---

def test_resistor_repr_includes_refdes_and_keeps_existing_keyword():
    r = Resistor(330, refdes_number=7)
    s = repr(r)
    assert "refdes='R7'" in s
    assert "ohms=" in s   # existing keyword preserved
