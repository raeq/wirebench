from components.chips.stm32f103c8t6 import STM32F103C8T6
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'VBAT',         Direction.IN),
    (  2, 'PC13',         Direction.BIDIR),
    (  3, 'PC14',         Direction.BIDIR),
    (  4, 'PC15',         Direction.BIDIR),
    (  5, 'PD0',          Direction.BIDIR),
    (  6, 'PD1',          Direction.BIDIR),
    (  7, 'NRST',         Direction.IN),
    (  8, 'VSSA',         Direction.IN),
    (  9, 'VDDA',         Direction.IN),
    ( 10, 'PA0',          Direction.BIDIR),
    ( 11, 'PA1',          Direction.BIDIR),
    ( 12, 'PA2',          Direction.BIDIR),
    ( 13, 'PA3',          Direction.BIDIR),
    ( 14, 'PA4',          Direction.BIDIR),
    ( 15, 'PA5',          Direction.BIDIR),
    ( 16, 'PA6',          Direction.BIDIR),
    ( 17, 'PA7',          Direction.BIDIR),
    ( 18, 'PB0',          Direction.BIDIR),
    ( 19, 'PB1',          Direction.BIDIR),
    ( 20, 'VSS',        Direction.IN),
    ( 21, 'VDD',        Direction.IN),
    ( 22, 'PB2',          Direction.BIDIR),
    ( 23, 'PB10',         Direction.BIDIR),
    ( 24, 'PB11',         Direction.BIDIR),
    ( 25, 'VSS',        Direction.IN),
    ( 26, 'VDD',        Direction.IN),
    ( 27, 'PB12',         Direction.BIDIR),
    ( 28, 'PB13',         Direction.BIDIR),
    ( 29, 'PB14',         Direction.BIDIR),
    ( 30, 'PB15',         Direction.BIDIR),
    ( 31, 'PA8',          Direction.BIDIR),
    ( 32, 'PA9',          Direction.BIDIR),
    ( 33, 'PA10',         Direction.BIDIR),
    ( 34, 'PA11',         Direction.BIDIR),
    ( 35, 'PA12',         Direction.BIDIR),
    ( 36, 'PA13',         Direction.BIDIR),
    ( 37, 'VSS',        Direction.IN),
    ( 38, 'VDD',        Direction.IN),
    ( 39, 'PA14',         Direction.BIDIR),
    ( 40, 'PA15',         Direction.BIDIR),
    ( 41, 'PB3',          Direction.BIDIR),
    ( 42, 'PB4',          Direction.BIDIR),
    ( 43, 'PB5',          Direction.BIDIR),
    ( 44, 'PB6',          Direction.BIDIR),
    ( 45, 'PB7',          Direction.BIDIR),
    ( 46, 'BOOT0',        Direction.IN),
    ( 47, 'PB8',          Direction.BIDIR),
    ( 48, 'PB9',          Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = STM32F103C8T6(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert STM32F103C8T6.REFDES_PREFIX == 'U'


def test_footprint():
    assert STM32F103C8T6.FOOTPRINT == 'Package_QFP:LQFP-48_7x7mm_P0.5mm'


def test_pin_count():
    ic = STM32F103C8T6(refdes_number=1)
    assert len(ic.pins) == 48


def test_pin_numbers_and_names_match_datasheet():
    ic = STM32F103C8T6(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = STM32F103C8T6(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = STM32F103C8T6(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = STM32F103C8T6(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(STM32F103C8T6(refdes_number=1)) == "STM32F103C8T6(refdes='U1')"
