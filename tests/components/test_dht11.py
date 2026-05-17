from components.chips.dht11 import DHT11
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'VDD',  Direction.IN),
    (2, 'DATA', Direction.BIDIR),
    (3, 'NC',   Direction.IN),
    (4, 'GND',  Direction.IN),
)


def test_construction_with_refdes_1():
    ic = DHT11(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert DHT11.REFDES_PREFIX == 'U'


def test_footprint():
    assert DHT11.FOOTPRINT == 'Package_TO_SOT_THT:DHT11'


def test_pin_count():
    ic = DHT11(refdes_number=1)
    assert len(ic.pins) == 4


def test_pin_numbers_and_names_match_datasheet():
    ic = DHT11(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = DHT11(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = DHT11(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = DHT11(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(DHT11(refdes_number=1)) == "DHT11(refdes='U1')"
