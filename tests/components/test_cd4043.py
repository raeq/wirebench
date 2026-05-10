import pytest
from components.cd4043 import CD4043


@pytest.fixture
def latch():
    return CD4043()


def test_initial_q_unknown(latch):
    assert latch.q is None


def test_initial_q_bar_port_unknown(latch):
    assert latch.ports['q_bar'].value is None


def test_set(latch):
    assert latch(s=True, r=False) is True


def test_reset(latch):
    latch(s=True, r=False)
    assert latch(s=False, r=True) is False


def test_hold_after_set(latch):
    latch(s=True, r=False)
    assert latch(s=False, r=False) is True


def test_hold_after_reset(latch):
    latch(s=True, r=False)
    latch(s=False, r=True)
    assert latch(s=False, r=False) is False


def test_q_bar_port_complement_of_q(latch):
    latch(s=True, r=False)
    assert latch.ports['q_bar'].value is False
    latch(s=False, r=True)
    assert latch.ports['q_bar'].value is True


def test_both_active_raises(latch):
    with pytest.raises(ValueError):
        latch(s=True, r=True)


def test_repr(latch):
    assert repr(latch) == "CD4043(q=None)"


# --- OE (output enable) ---

def test_oe_high_enables_outputs(latch):
    latch(s=True, r=False)
    latch.ports['oe'].drive(True)
    latch._evaluate()
    assert latch.ports['q'].value is True
    assert latch.ports['q_bar'].value is False


def test_oe_low_tristates_outputs(latch):
    latch(s=True, r=False)
    latch.ports['oe'].drive(False)
    latch._evaluate()
    assert latch.ports['q'].value is None
    assert latch.ports['q_bar'].value is None


def test_oe_unconnected_defaults_to_enabled(latch):
    latch(s=True, r=False)
    # oe port never driven — should behave as OE=HIGH
    assert latch.ports['q'].value is True


def test_oe_tristated_does_not_change_latch_state(latch):
    latch(s=True, r=False)           # set
    latch.ports['oe'].drive(False)
    latch._evaluate()                # outputs tri-stated
    latch.ports['oe'].drive(True)
    latch._evaluate()                # outputs re-enabled
    assert latch.ports['q'].value is True  # latch held its state
