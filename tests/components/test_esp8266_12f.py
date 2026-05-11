from components.chips.esp8266_12f import ESP8266_12F
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'RST',          Direction.IN),
    (  2, 'ADC',          Direction.IN),
    (  3, 'EN',           Direction.IN),
    (  4, 'GPIO16',       Direction.BIDIR),
    (  5, 'GPIO14',       Direction.BIDIR),
    (  6, 'GPIO12',       Direction.BIDIR),
    (  7, 'GPIO13',       Direction.BIDIR),
    (  8, 'VCC',          Direction.IN),
    (  9, 'CS0',          Direction.BIDIR),
    ( 10, 'MISO',         Direction.BIDIR),
    ( 11, 'GPIO0',        Direction.BIDIR),
    ( 12, 'MOSI',         Direction.BIDIR),
    ( 13, 'SCLK',         Direction.BIDIR),
    ( 14, 'GND',          Direction.IN),
    ( 15, 'GPIO10',       Direction.BIDIR),
    ( 16, 'GPIO9',        Direction.BIDIR),
    ( 17, 'GPIO11',       Direction.BIDIR),
    ( 18, 'GPIO6',        Direction.BIDIR),
    ( 19, 'GPIO7',        Direction.BIDIR),
    ( 20, 'GPIO8',        Direction.BIDIR),
    ( 21, 'RXD',          Direction.BIDIR),
    ( 22, 'TXD',          Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = ESP8266_12F(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert ESP8266_12F.REFDES_PREFIX == 'U'


def test_footprint():
    assert ESP8266_12F.FOOTPRINT == 'RF_Module:ESP-12E'


def test_pin_count():
    ic = ESP8266_12F(refdes_number=1)
    assert len(ic.pins) == 22


def test_pin_numbers_and_names_match_datasheet():
    ic = ESP8266_12F(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = ESP8266_12F(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = ESP8266_12F(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = ESP8266_12F(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(ESP8266_12F(refdes_number=1)) == "ESP8266_12F(refdes='U1')"
