from components.chips.bmp280 import BMP280
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'GND',      Direction.IN),
    (2, 'CSB',      Direction.IN),
    (3, 'SDI_SDA',  Direction.BIDIR),
    (4, 'SCK_SCL',  Direction.IN),
    (5, 'SDO_ADDR', Direction.BIDIR),
    (6, 'VDDIO',    Direction.IN),
    (7, 'GND',      Direction.IN),
    (8, 'VDD',      Direction.IN),
)


def test_construction_with_refdes_1():
    ic = BMP280(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert BMP280.REFDES_PREFIX == 'U'


def test_footprint():
    assert BMP280.FOOTPRINT == 'Package_LGA:Bosch_LGA-8_2x2.5mm_P0.65mm'


def test_pin_count():
    ic = BMP280(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = BMP280(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = BMP280(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = BMP280(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = BMP280(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(BMP280(refdes_number=1)) == "BMP280(refdes='U1')"
