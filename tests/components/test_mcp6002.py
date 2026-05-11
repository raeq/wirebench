from components.chips.mcp6002 import MCP6002
from framework.port import Direction


EXPECTED_PINS = (
    (1, 'OUT1', Direction.OUT),
    (2, 'IN1_NEG', Direction.IN),
    (3, 'IN1_POS', Direction.IN),
    (4, 'VSS',  Direction.IN),
    (5, 'IN2_POS', Direction.IN),
    (6, 'IN2_NEG', Direction.IN),
    (7, 'OUT2', Direction.OUT),
    (8, 'VDD',  Direction.IN),
)


def test_construction_with_refdes_1():
    ic = MCP6002(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert MCP6002.REFDES_PREFIX == 'U'


def test_footprint():
    assert MCP6002.FOOTPRINT == 'Package_DIP:DIP-8_W7.62mm'


def test_pin_count():
    ic = MCP6002(refdes_number=1)
    assert len(ic.pins) == 8


def test_pin_numbers_and_names_match_datasheet():
    ic = MCP6002(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = MCP6002(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = MCP6002(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = MCP6002(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(MCP6002(refdes_number=1)) == "MCP6002(refdes='U1')"
