from components.chips.stm32f411ceu6 import STM32F411CEU6
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'VBAT',         Direction.IN),
    (  2, 'PC13',         Direction.BIDIR),
    (  3, 'PC14',         Direction.BIDIR),
    (  4, 'PC15',         Direction.BIDIR),
    (  5, 'PH0',          Direction.BIDIR),
    (  6, 'PH1',          Direction.BIDIR),
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
    ( 20, 'PB2',          Direction.BIDIR),
    ( 21, 'PB10',         Direction.BIDIR),
    ( 22, 'VCAP_1',       Direction.IN),
    ( 23, 'VSS',        Direction.IN),
    ( 24, 'VDD',        Direction.IN),
    ( 25, 'PB12',         Direction.BIDIR),
    ( 26, 'PB13',         Direction.BIDIR),
    ( 27, 'PB14',         Direction.BIDIR),
    ( 28, 'PB15',         Direction.BIDIR),
    ( 29, 'PA8',          Direction.BIDIR),
    ( 30, 'PA9',          Direction.BIDIR),
    ( 31, 'PA10',         Direction.BIDIR),
    ( 32, 'PA11',         Direction.BIDIR),
    ( 33, 'PA12',         Direction.BIDIR),
    ( 34, 'PA13',         Direction.BIDIR),
    ( 35, 'VSS',        Direction.IN),
    ( 36, 'VDD',        Direction.IN),
    ( 37, 'PA14',         Direction.BIDIR),
    ( 38, 'PA15',         Direction.BIDIR),
    ( 39, 'PB3',          Direction.BIDIR),
    ( 40, 'PB4',          Direction.BIDIR),
    ( 41, 'PB5',          Direction.BIDIR),
    ( 42, 'PB6',          Direction.BIDIR),
    ( 43, 'PB7',          Direction.BIDIR),
    ( 44, 'BOOT0',        Direction.IN),
    ( 45, 'PB8',          Direction.BIDIR),
    ( 46, 'PB9',          Direction.BIDIR),
    ( 47, 'VSS',        Direction.IN),
    ( 48, 'VDD',        Direction.IN),
)


def test_construction_with_refdes_1():
    ic = STM32F411CEU6(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert STM32F411CEU6.REFDES_PREFIX == 'U'


def test_footprint():
    assert STM32F411CEU6.FOOTPRINT == 'Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm'


def test_pin_count():
    ic = STM32F411CEU6(refdes_number=1)
    assert len(ic.pins) == 48


def test_pin_numbers_and_names_match_datasheet():
    ic = STM32F411CEU6(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = STM32F411CEU6(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = STM32F411CEU6(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = STM32F411CEU6(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(STM32F411CEU6(refdes_number=1)) == "STM32F411CEU6(refdes='U1')"
