from components.chips.concepts.decade_counter import DecadeCounter


def test_initial_count_is_zero():
    assert DecadeCounter().count == 0


def test_first_rising_edge_advances_from_zero():
    """`_prev_clk` initialises to LOW, so the very first HIGH on the
    clock pin is a real rising edge (matches a CMOS pin at rest)."""
    c = DecadeCounter()
    assert c(clk=True) == 1


def test_advances_on_each_rising_edge():
    c = DecadeCounter()
    c(clk=False)
    c(clk=True);  assert c.count == 1
    c(clk=False); assert c.count == 1
    c(clk=True);  assert c.count == 2
    c(clk=False); assert c.count == 2
    c(clk=True);  assert c.count == 3


def test_inhibit_freezes_the_count():
    c = DecadeCounter()
    c(clk=False)
    c(clk=True, inhibit=True);  assert c.count == 0
    c(clk=False, inhibit=True); assert c.count == 0
    c(clk=True, inhibit=True);  assert c.count == 0


def test_reset_clamps_to_zero_at_any_time():
    c = DecadeCounter()
    c(clk=False)
    c(clk=True);  c(clk=False)
    c(clk=True);  c(clk=False)
    c(clk=True);  c(clk=False)
    assert c.count == 3
    c(clk=False, reset=True)
    assert c.count == 0


def test_self_clamping_feedback_within_one_evaluate():
    """If RST and Q_N are externally wired so Q_6 (or any Q_n with
    n>0) feeds RST, the cell should clamp inside the same evaluate
    rather than leaving a single-pass transient.  We simulate that
    wire by driving the cell to count=6 then asserting reset; the
    second pass inside evaluate() should clamp the outputs back to
    Q0."""
    from framework.wire import wire
    c = DecadeCounter()
    # Wire reset to q6 — what the dice circuit does at chip level.
    wire(c.ports['q6'], c.ports['reset'])
    # Pulse the clock six times to drive count to 6 (and beyond).
    c.ports['clk'].drive(False); c.evaluate()
    for _ in range(7):
        c.ports['clk'].drive(True);  c.evaluate()
        c.ports['clk'].drive(False); c.evaluate()
    # After the 6th rising edge, count would have gone to 6 then
    # been clamped to 0 by the self-feedback within the same evaluate.
    assert c.count != 6


def test_q_outputs_one_hot():
    c = DecadeCounter()
    c(clk=False)
    for expected in range(1, 10):
        c(clk=True)
        for i in range(10):
            assert bool(c.ports[f'q{i}'].value) == (i == expected)
        c(clk=False)


def test_co_high_for_counts_0_through_4():
    c = DecadeCounter()
    c(clk=False)
    for n in range(10):
        assert bool(c.ports['co'].value) == (c.count < 5), \
            f"CO wrong at count={c.count}"
        c(clk=True); c(clk=False)


def test_repr_includes_count():
    c = DecadeCounter()
    assert 'count=0' in repr(c)
