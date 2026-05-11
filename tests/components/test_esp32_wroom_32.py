from components.chips.esp32_wroom_32 import ESP32_WROOM_32
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'GND',        Direction.IN),
    (  2, '3V3',          Direction.IN),
    (  3, 'EN',           Direction.IN),
    (  4, 'SENSOR_VP',    Direction.IN),
    (  5, 'SENSOR_VN',    Direction.IN),
    (  6, 'GPIO34',       Direction.IN),
    (  7, 'GPIO35',       Direction.IN),
    (  8, 'GPIO32',       Direction.BIDIR),
    (  9, 'GPIO33',       Direction.BIDIR),
    ( 10, 'GPIO25',       Direction.BIDIR),
    ( 11, 'GPIO26',       Direction.BIDIR),
    ( 12, 'GPIO27',       Direction.BIDIR),
    ( 13, 'GPIO14',       Direction.BIDIR),
    ( 14, 'GPIO12',       Direction.BIDIR),
    ( 15, 'GND',        Direction.IN),
    ( 16, 'GPIO13',       Direction.BIDIR),
    ( 17, 'SD2',          Direction.BIDIR),
    ( 18, 'SD3',          Direction.BIDIR),
    ( 19, 'CMD',          Direction.BIDIR),
    ( 20, 'CLK',          Direction.BIDIR),
    ( 21, 'SD0',          Direction.BIDIR),
    ( 22, 'SD1',          Direction.BIDIR),
    ( 23, 'GPIO15',       Direction.BIDIR),
    ( 24, 'GPIO2',        Direction.BIDIR),
    ( 25, 'GPIO0',        Direction.BIDIR),
    ( 26, 'GPIO4',        Direction.BIDIR),
    ( 27, 'GPIO16',       Direction.BIDIR),
    ( 28, 'GPIO17',       Direction.BIDIR),
    ( 29, 'GPIO5',        Direction.BIDIR),
    ( 30, 'GPIO18',       Direction.BIDIR),
    ( 31, 'GPIO19',       Direction.BIDIR),
    ( 33, 'GPIO21',       Direction.BIDIR),
    ( 34, 'RXD0',         Direction.BIDIR),
    ( 35, 'TXD0',         Direction.BIDIR),
    ( 36, 'GPIO22',       Direction.BIDIR),
    ( 37, 'GPIO23',       Direction.BIDIR),
    ( 38, 'GND',        Direction.IN),
)


def test_construction_with_refdes_1():
    ic = ESP32_WROOM_32(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ESP32_WROOM_32.REFDES_PREFIX == 'U'


def test_footprint():
    assert ESP32_WROOM_32.FOOTPRINT == 'RF_Module:ESP32-WROOM-32'


def test_pin_count():
    ic = ESP32_WROOM_32(refdes_number=1)
    assert len(ic.pins) == 37


def test_pin_numbers_and_names_match_datasheet():
    ic = ESP32_WROOM_32(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ESP32_WROOM_32(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = ESP32_WROOM_32(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ESP32_WROOM_32(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ESP32_WROOM_32(refdes_number=1)) == "ESP32_WROOM_32(refdes='U1')"
