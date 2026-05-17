from components.chips.display5641as import Display5641AS
from framework.port import Direction


EXPECTED_PINS = (
    ( 1, 'SEG_E',  Direction.IN),
    ( 2, 'SEG_D',  Direction.IN),
    ( 3, 'SEG_DP', Direction.IN),
    ( 4, 'SEG_C',  Direction.IN),
    ( 5, 'SEG_G',  Direction.IN),
    ( 6, 'DIG_4',  Direction.IN),
    ( 7, 'SEG_B',  Direction.IN),
    ( 8, 'DIG_3',  Direction.IN),
    ( 9, 'DIG_2',  Direction.IN),
    (10, 'SEG_F',  Direction.IN),
    (11, 'SEG_A',  Direction.IN),
    (12, 'DIG_1',  Direction.IN),
)


def test_construction_with_refdes_1():
    ic = Display5641AS(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert Display5641AS.REFDES_PREFIX == 'U'


def test_footprint():
    assert Display5641AS.FOOTPRINT == 'Display_7Segment:Display_5641AS'


def test_pin_count():
    ic = Display5641AS(refdes_number=1)
    assert len(ic.pins) == 12


def test_pin_numbers_and_names_match_datasheet():
    ic = Display5641AS(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = Display5641AS(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number].direction is direction


def test_ports_keyed_by_pin_name():
    ic = Display5641AS(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def _drive_for_char(c: str) -> dict[str, bool]:
    """Build keyword args for __call__ that show character `c` on digit 1.

    Common-anode polarity: digit HIGH, lit segments LOW, dark segments HIGH.
    Other three digits stay LOW (dark).
    """
    char_to_segs = {
        '0': {'A', 'B', 'C', 'D', 'E', 'F'},
        '1': {'B', 'C'},
        '2': {'A', 'B', 'D', 'E', 'G'},
        '3': {'A', 'B', 'C', 'D', 'G'},
        '4': {'B', 'C', 'F', 'G'},
        '5': {'A', 'C', 'D', 'F', 'G'},
        '6': {'A', 'C', 'D', 'E', 'F', 'G'},
        '7': {'A', 'B', 'C'},
        '8': {'A', 'B', 'C', 'D', 'E', 'F', 'G'},
        '9': {'A', 'B', 'C', 'D', 'F', 'G'},
        'C': {'A', 'D', 'E', 'F'},
        '-': {'G'},
        ' ': set(),
    }
    lit = char_to_segs[c]
    kwargs: dict[str, bool] = {'DIG_1': True}
    for seg in ('A', 'B', 'C', 'D', 'E', 'F', 'G'):
        kwargs[f'SEG_{seg}'] = seg not in lit
    kwargs['SEG_DP'] = True   # decimal point always off in this table
    return kwargs


def test_glyph_decodes_digit_zero_through_nine():
    ic = Display5641AS(refdes_number=1)
    for c in '0123456789':
        glyphs = ic(**_drive_for_char(c))
        assert glyphs[0] == c, f"expected '{c}' on dig1, got {glyphs[0]!r}"
        # Other digits dark.
        for g in glyphs[1:]:
            assert g == ' '


def test_glyph_decodes_dash_blank_and_C():
    ic = Display5641AS(refdes_number=1)
    for c in ('-', ' ', 'C'):
        glyphs = ic(**_drive_for_char(c))
        assert glyphs[0] == c


def test_unknown_pattern_renders_as_question_mark():
    """Drive an arbitrary segment combination not in the glyph table."""
    ic = Display5641AS(refdes_number=1)
    # Light only seg_a and seg_g on dig1 — not a recognised glyph.
    glyphs = ic(DIG_1=True, SEG_A=False, SEG_G=False)
    assert glyphs[0] == '?'


def test_digit_low_blanks_everything_on_that_digit():
    """A LOW digit anode keeps the digit dark regardless of segments."""
    ic = Display5641AS(refdes_number=1)
    glyphs = ic(DIG_1=False,
                SEG_A=False, SEG_B=False, SEG_C=False, SEG_D=False,
                SEG_E=False, SEG_F=False, SEG_G=False, SEG_DP=False)
    assert glyphs[0] == ' '


def test_only_selected_digit_lights():
    """Driving DIG_2 lights digit 2 only; digits 1, 3, 4 stay dark."""
    ic = Display5641AS(refdes_number=1)
    kwargs = _drive_for_char('3')
    # Re-route: light digit 2 instead of digit 1.
    kwargs.pop('DIG_1')
    kwargs['DIG_2'] = True
    glyphs = ic(**kwargs)
    assert glyphs == (' ', '3', ' ', ' ')
