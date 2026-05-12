import pytest

from components.passives.cell import Cell, soc_from_ocv
from framework.errors import PartParameterError
from framework.ground import ELECTRICAL
from framework.port import Direction
from framework.units import Volts


def test_default_is_full_charged():
    bt = Cell(refdes_number=1)
    assert bt.state_of_charge == 1.0


def test_default_terminal_voltage_is_4_2():
    bt = Cell(refdes_number=1)
    assert float(bt.terminal_voltage) == pytest.approx(4.2)


def test_terminal_voltage_at_zero_soc():
    bt = Cell(initial_state_of_charge=0.0, refdes_number=1)
    assert float(bt.terminal_voltage) == pytest.approx(3.0)


@pytest.mark.parametrize("soc,expected_v", [
    (0.00, 3.0),
    (0.10, 3.4),
    (0.50, 3.7),
    (0.90, 4.0),
    (1.00, 4.2),
])
def test_ocv_curve_anchor_points(soc, expected_v):
    bt = Cell(refdes_number=1)
    assert float(bt(soc)) == pytest.approx(expected_v)


def test_ocv_curve_interpolates_between_anchors():
    bt = Cell(refdes_number=1)
    # 30 % SoC is 1/2 between (0.10, 3.4) and (0.50, 3.7) → 3.55
    assert float(bt(0.30)) == pytest.approx(3.55)


def test_soc_from_ocv_inverts_curve():
    """Round-trip: a voltage emitted at SoC should invert back to it
    within numerical tolerance."""
    for soc in (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.00):
        v = float(Cell(initial_state_of_charge=soc, refdes_number=1).terminal_voltage)
        assert soc_from_ocv(v) == pytest.approx(soc, abs=1e-9)


def test_soc_from_ocv_clamps_below_curve():
    """A measurement below the fully-empty voltage maps to 0 % SoC."""
    assert soc_from_ocv(2.5) == 0.0


def test_soc_from_ocv_clamps_above_curve():
    """A measurement above fully-charged maps to 100 % SoC."""
    assert soc_from_ocv(4.5) == 1.0


def test_state_of_charge_setter_accepts_valid_range():
    bt = Cell(refdes_number=1)
    bt.state_of_charge = 0.5
    assert bt.state_of_charge == 0.5


def test_state_of_charge_setter_rejects_negative():
    bt = Cell(refdes_number=1)
    with pytest.raises(PartParameterError):
        bt.state_of_charge = -0.1


def test_state_of_charge_setter_rejects_above_one():
    bt = Cell(refdes_number=1)
    with pytest.raises(PartParameterError):
        bt.state_of_charge = 1.5


def test_evaluate_drives_pos_to_ocv_and_neg_to_zero():
    bt = Cell(initial_state_of_charge=0.5, refdes_number=1)
    bt.evaluate()
    assert bt.ports['pos'].value == pytest.approx(3.7)
    assert bt.ports['neg'].value == 0.0


def test_pos_terminal_is_out():
    bt = Cell(refdes_number=1)
    assert bt.ports['pos'].direction is Direction.OUT


def test_neg_terminal_is_out():
    bt = Cell(refdes_number=1)
    assert bt.ports['neg'].direction is Direction.OUT


def test_refdes_prefix():
    assert Cell.REFDES_PREFIX == 'BT'


def test_refdes_assembled():
    assert Cell(refdes_number=3).refdes == 'BT3'


def test_initial_charge_validated():
    """Construction-time validation prevents nonsense initial SoC."""
    with pytest.raises(Exception):
        Cell(initial_state_of_charge=1.5, refdes_number=1)


def test_repr_includes_soc():
    bt = Cell(initial_state_of_charge=0.5, refdes_number=2)
    r = repr(bt)
    assert '0.5' in r
    assert 'BT2' in r


def test_call_returns_volts():
    """Calling the cell returns a Volts-typed value, not raw float."""
    bt = Cell(refdes_number=1)
    assert isinstance(bt(0.5), Volts)
