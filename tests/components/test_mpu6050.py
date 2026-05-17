from components.chips.mpu6050 import MPU6050
from framework.port import Direction


EXPECTED_PINS = (
    (1,  'CLKIN',  Direction.IN),
    (6,  'AUX_DA', Direction.BIDIR),
    (7,  'AUX_CL', Direction.OUT),
    (8,  'VLOGIC', Direction.IN),
    (9,  'AD0',    Direction.IN),
    (10, 'REGOUT', Direction.OUT),
    (11, 'FSYNC',  Direction.IN),
    (12, 'INT',    Direction.OUT),
    (13, 'VDD',    Direction.IN),
    (18, 'GND',    Direction.IN),
    (20, 'CPOUT',  Direction.OUT),
    (23, 'SCL',    Direction.IN),
    (24, 'SDA',    Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = MPU6050(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert MPU6050.REFDES_PREFIX == 'U'


def test_footprint():
    assert MPU6050.FOOTPRINT == 'Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm'


def test_pin_count():
    ic = MPU6050(refdes_number=1)
    assert len(ic.pins) == 13


def test_pin_numbers_and_names_match_datasheet():
    ic = MPU6050(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = MPU6050(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = MPU6050(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_reserved_pins_omitted():
    ic = MPU6050(refdes_number=1)
    pin_numbers = {p.id.number for p in ic.pins}
    for reserved in (2, 3, 4, 5, 14, 15, 16, 17, 19, 21, 22):
        assert reserved not in pin_numbers


def test_call_is_noop():
    ic = MPU6050(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(MPU6050(refdes_number=1)) == "MPU6050(refdes='U1')"
