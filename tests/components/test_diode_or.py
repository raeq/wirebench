import pytest

from components.chips.concepts.diode_or import DiodeOR


def test_construction_requires_at_least_one_input():
    with pytest.raises(ValueError):
        DiodeOR(input_names=())


def test_rejects_duplicate_input_names():
    with pytest.raises(ValueError):
        DiodeOR(input_names=('a', 'a'))


def test_reserved_output_name_rejected():
    with pytest.raises(ValueError):
        DiodeOR(input_names=('out',))


def test_single_input_acts_as_passthrough():
    or_ = DiodeOR(input_names=('q0',))
    assert or_(q0=True) is True
    assert or_(q0=False) is False


def test_out_is_high_when_any_input_is_high():
    or_ = DiodeOR(input_names=('q1', 'q3', 'q5'))
    assert or_(q1=True,  q3=False, q5=False) is True
    assert or_(q1=False, q3=True,  q5=False) is True
    assert or_(q1=False, q3=False, q5=True)  is True


def test_out_is_low_when_all_inputs_are_low():
    or_ = DiodeOR(input_names=('q1', 'q3', 'q5'))
    assert or_(q1=False, q3=False, q5=False) is False


def test_omitted_inputs_default_to_false():
    or_ = DiodeOR(input_names=('q1', 'q3', 'q5'))
    assert or_(q1=True) is True
    assert or_() is False


def test_none_inputs_treated_as_low():
    or_ = DiodeOR(input_names=('q1', 'q3', 'q5'))
    assert or_(q1=None, q3=None, q5=None) is False


def test_unknown_input_name_raises():
    or_ = DiodeOR(input_names=('a', 'b'))
    with pytest.raises(ValueError):
        or_(a=True, c=True)


def test_repr_lists_inputs():
    or_ = DiodeOR(input_names=('x', 'y'))
    assert "['x', 'y']" in repr(or_)
