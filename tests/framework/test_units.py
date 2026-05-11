from framework.units import (
    Amps, Milliamps, Microamps,
    Volts, Millivolts,
    Ohms, Kilohms,
)


def test_base_unit_stores_value_unchanged():
    assert float(Volts(5)) == 5.0
    assert float(Amps(2)) == 2.0
    assert float(Ohms(330)) == 330.0


def test_milli_scale_to_base():
    assert float(Millivolts(100)) == 0.1
    assert float(Milliamps(50)) == 0.05


def test_micro_scale_to_base():
    assert float(Microamps(500)) == 5e-4


def test_kilo_scale_to_base():
    assert float(Kilohms(4.7)) == 4700.0


def test_str_renders_in_declared_unit():
    assert str(Millivolts(100)) == "100 mV"
    assert str(Kilohms(4.7))    == "4.7 kΩ"
    assert str(Microamps(250))  == "250 µA"


def test_repr_renders_in_declared_unit():
    assert repr(Millivolts(100)) == "Millivolts(100.0)"
    assert repr(Kilohms(4.7))    == "Kilohms(4.7)"


def test_cross_unit_subtraction_is_correct():
    # 5 V − 100 mV = 4.9 V, not 4.9 V (treating 100 as volts)
    result = Volts(5) - Millivolts(100)
    assert float(result) == 4.9
    assert isinstance(result, Volts)


def test_addition_preserves_lhs_unit():
    result = Volts(1) + Millivolts(500)
    assert isinstance(result, Volts)
    assert float(result) == 1.5


# Coverage for the per-subclass __str__ formatters that weren't
# previously exercised (the existing suite hits Millivolts / Kilohms /
# Microamps but not Amps / Volts / Ohms directly).

def test_amps_str_format():
    assert str(Amps(1.5)) == '1.5 A'


def test_volts_str_format():
    assert str(Volts(3.3)) == '3.3 V'


def test_ohms_str_format():
    assert str(Ohms(330)) == '330 Ω'


def test_milliamps_str_format():
    assert str(Milliamps(250)) == '250 mA'


# Coverage for __neg__ / __abs__ / __pos__ / __rsub__ / __radd__
# which are dunder ops the existing arithmetic test doesn't reach.

def test_negate_preserves_unit():
    result = -Volts(5)
    assert isinstance(result, Volts)
    assert float(result) == -5.0


def test_abs_preserves_unit():
    result = abs(Volts(-3))
    assert isinstance(result, Volts)
    assert float(result) == 3.0


def test_pos_preserves_unit():
    result = +Volts(2)
    assert isinstance(result, Volts)
    assert float(result) == 2.0


def test_radd_when_lhs_is_plain_float():
    result = 1.0 + Volts(2)
    assert isinstance(result, Volts)
    assert float(result) == 3.0


def test_rsub_when_lhs_is_plain_float():
    result = 5.0 - Volts(2)
    assert isinstance(result, Volts)
    assert float(result) == 3.0


def test_none_value_constructs_zero():
    # The _Unit ctor accepts None and stores 0.0 in base SI.
    assert float(Volts(None)) == 0.0
