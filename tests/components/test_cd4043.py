import pytest
from components.cd4043 import CD4043


@pytest.fixture
def chip():
    return CD4043()


def test_initial_outputs_undefined(chip):
    for i in range(1, 5):
        assert chip.ports[f'q_{i}'].value is None
        assert chip.ports[f'q_{i}_bar'].value is None


def test_set_latch_1(chip):
    out = chip(s_1=True, r_1=False)
    assert out[0] == (True, False)


def test_each_latch_independent(chip):
    out = chip(
        s_1=True,  r_1=False,
        s_2=False, r_2=True,
        s_3=True,  r_3=False,
        s_4=False, r_4=True,
    )
    assert out[0] == (True,  False)
    assert out[1] == (False, True)
    assert out[2] == (True,  False)
    assert out[3] == (False, True)


def test_hold_after_set(chip):
    chip(s_1=True, r_1=False)
    out = chip(s_1=False, r_1=False)
    assert out[0] == (True, False)


def test_both_active_raises(chip):
    with pytest.raises(ValueError):
        chip(s_1=True, r_1=True)


def test_oe_low_tristates_all_outputs(chip):
    chip(s_1=True, r_1=False, s_2=True, r_2=False)
    chip(s_1=False, r_1=False, s_2=False, r_2=False, oe=False)
    for i in range(1, 5):
        assert chip.ports[f'q_{i}'].value is None
        assert chip.ports[f'q_{i}_bar'].value is None


def test_oe_re_enables_after_tristate(chip):
    chip(s_1=True, r_1=False)
    chip(s_1=False, r_1=False, oe=False)
    out = chip(s_1=False, r_1=False, oe=True)
    assert out[0] == (True, False)


def test_oe_unconnected_defaults_to_enabled(chip):
    # Drive via port-level interface; oe is never touched.
    chip.ports['s_1'].drive(True)
    chip.ports['r_1'].drive(False)
    chip._evaluate()
    assert chip.ports['q_1'].value is True


def test_repr_undefined(chip):
    assert repr(chip) == "CD4043(q=(None, None, None, None))"
