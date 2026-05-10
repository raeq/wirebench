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
