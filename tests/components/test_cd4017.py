from components.chips.cd4017 import CD4017
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'Q5',  Direction.OUT),
    ( 2, 'Q1',  Direction.OUT),
    ( 3, 'Q0',  Direction.OUT),
    ( 4, 'Q2',  Direction.OUT),
    ( 5, 'Q6',  Direction.OUT),
    ( 6, 'Q7',  Direction.OUT),
    ( 7, 'Q3',  Direction.OUT),
    ( 8, 'VSS', Direction.IN),
    ( 9, 'Q8',  Direction.OUT),
    (10, 'Q4',  Direction.OUT),
    (11, 'Q9',  Direction.OUT),
    (12, 'CO',  Direction.OUT),
    (13, 'CE',  Direction.IN),
    (14, 'CLK', Direction.IN),
    (15, 'RST', Direction.IN),
    (16, 'VDD', Direction.IN),
)


def test_construction_with_refdes_1():
    ic = CD4017(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert CD4017.REFDES_PREFIX == 'U'


def test_footprint():
    assert CD4017.FOOTPRINT == 'Package_DIP:DIP-16_W7.62mm'


def test_pin_count():
    ic = CD4017(refdes_number=1)
    assert len(ic.pins) == 16


def test_pin_numbers_and_names_match_datasheet():
    ic = CD4017(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = CD4017(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = CD4017(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_starts_at_count_zero():
    ic = CD4017(refdes_number=1)
    assert ic(clk=False) == 0


def test_call_advances_on_rising_edge():
    ic = CD4017(refdes_number=1)
    ic(clk=False)
    assert ic(clk=True) == 1
    ic(clk=False)
    assert ic(clk=True) == 2


def test_q0_high_at_count_zero():
    ic = CD4017(refdes_number=1)
    ic(clk=False)
    assert bool(ic.ports['Q0'].value) is True
    for q in ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'):
        assert bool(ic.ports[q].value) is False


def test_co_high_for_first_five_counts():
    ic = CD4017(refdes_number=1)
    ic(clk=False)
    for expected in range(10):
        assert bool(ic.ports['CO'].value) == (expected < 5)
        ic(clk=True); ic(clk=False)


def test_repr_includes_count_and_refdes():
    ic = CD4017(refdes_number=3)
    r = repr(ic)
    assert "U3" in r
    assert "count=0" in r
