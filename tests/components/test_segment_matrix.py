from components.chips.concepts.segment_matrix import SegmentMatrix


def test_default_is_unlit():
    """Before any drive, no segment is reported lit."""
    m = SegmentMatrix()
    # __call__ with defaults: digits LOW, segments HIGH → nothing lit.
    matrix = m()
    for row in matrix:
        assert all(cell is False for cell in row)


def test_digit_with_no_segment_drive_is_blank():
    """A HIGH digit with all segments HIGH is dark."""
    m = SegmentMatrix()
    matrix = m(dig_1=True)
    assert all(cell is False for cell in matrix[0])


def test_single_segment_lit_on_selected_digit():
    """Common-anode polarity: dig HIGH + seg LOW → lit."""
    m = SegmentMatrix()
    matrix = m(dig_1=True, seg_a=False)
    assert matrix[0][0] is True   # digit 1, segment a
    # No other segment lit on digit 1.
    assert all(cell is False for cell in matrix[0][1:])
    # No segments lit on other digits.
    for row in matrix[1:]:
        assert all(cell is False for cell in row)


def test_segment_only_lit_when_digit_high():
    """Segment LOW with digit LOW is NOT lit (common-anode polarity)."""
    m = SegmentMatrix()
    matrix = m(dig_1=False, seg_a=False)
    assert matrix[0][0] is False


def test_all_segments_lit_with_all_digits_high():
    """Asserting every cell is lit on every digit when fully driven."""
    m = SegmentMatrix()
    matrix = m(dig_1=True, dig_2=True, dig_3=True, dig_4=True,
               seg_a=False, seg_b=False, seg_c=False, seg_d=False,
               seg_e=False, seg_f=False, seg_g=False, seg_dp=False)
    for row in matrix:
        for cell in row:
            assert cell is True


def test_undriven_segment_is_not_lit():
    """A None-valued segment (undriven cathode) does not sink current."""
    m = SegmentMatrix()
    # Drive only the digit; leave segment_a explicitly undriven.
    matrix = m(dig_1=True, seg_a=None)
    assert matrix[0][0] is False
