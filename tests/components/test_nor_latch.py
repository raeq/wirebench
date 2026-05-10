import pytest
from components.nor_latch import NORLatch


@pytest.fixture
def cell():
    return NORLatch()


def test_initial_q_unknown(cell):
    assert cell.ports['q'].value is None


def test_initial_q_bar_port_unknown(cell):
    assert cell.ports['q_bar'].value is None


def test_set(cell):
    assert cell(s=True, r=False) is True


def test_reset(cell):
    cell(s=True, r=False)
    assert cell(s=False, r=True) is False


def test_hold_after_set(cell):
    cell(s=True, r=False)
    assert cell(s=False, r=False) is True


def test_hold_after_reset(cell):
    cell(s=True, r=False)
    cell(s=False, r=True)
    assert cell(s=False, r=False) is False


def test_q_bar_port_complement_of_q(cell):
    cell(s=True, r=False)
    assert cell.ports['q_bar'].value is False
    cell(s=False, r=True)
    assert cell.ports['q_bar'].value is True


def test_both_active_raises(cell):
    with pytest.raises(ValueError):
        cell(s=True, r=True)


def test_repr(cell):
    assert repr(cell) == "NORLatch(q=None)"
