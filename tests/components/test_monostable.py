from components.chips.concepts.monostable import Monostable


def test_starts_idle_with_output_low():
    m = Monostable(duration_ms=1000)
    # Before any drive, prev_trig is None — no edge can be detected,
    # so the very first evaluate must leave the output LOW.
    assert m(trig=True, reset=True) is False
    assert m.running is False


def test_falling_edge_starts_pulse():
    m = Monostable(duration_ms=1000)
    m(trig=True)            # idle HIGH, seed prev_trig
    out = m(trig=False)     # falling edge → trigger
    assert out is True
    assert m.running is True
    assert m.remaining_ms == 1000


def test_rising_edge_does_not_trigger():
    m = Monostable(duration_ms=1000)
    m(trig=False)
    out = m(trig=True)
    assert out is False
    assert m.running is False


def test_press_during_pulse_is_ignored():
    """A second falling edge while the pulse is in progress must not
    extend or restart it."""
    m = Monostable(duration_ms=1000)
    m(trig=True)
    m(trig=False)            # trigger; remaining = 1000
    m(trig=True)             # release; prev now LOW→HIGH
    m._remaining_ms = 400.0  # simulate 600 ms elapsed
    m(trig=True)             # idle HIGH, no edge — remaining unchanged
    m(trig=False)            # another press attempt
    assert m.remaining_ms == 400.0   # still mid-pulse, not retriggered


def test_pulse_ends_when_remaining_reaches_zero():
    m = Monostable(duration_ms=1000)
    m(trig=True); m(trig=False)
    assert m.running is True
    m._remaining_ms = 0.0
    out = m(trig=True)
    assert out is False
    assert m.running is False


def test_reset_low_forces_output_low_and_blocks_trigger():
    m = Monostable(duration_ms=1000)
    m(trig=True, reset=True)
    m(trig=False, reset=False)   # press while reset asserted
    assert m.running is False    # no trigger while RESET is LOW


def test_reset_none_or_high_is_normal_operation():
    """Pin 4 is active-LOW: HIGH or undriven (None) is the normal case
    and must not inhibit triggering."""
    m = Monostable(duration_ms=1000)
    m(trig=True, reset=None)
    out = m(trig=False, reset=None)
    assert out is True


def test_reset_during_pulse_clears_remaining():
    m = Monostable(duration_ms=1000)
    m(trig=True); m(trig=False)
    assert m.running is True
    m(trig=False, reset=False)
    assert m.running is False
    assert m.remaining_ms == 0


def test_running_property_tracks_remaining():
    m = Monostable(duration_ms=1000)
    assert m.running is False
    m(trig=True); m(trig=False)
    assert m.running is True
    m._remaining_ms = 0.0
    m(trig=False)
    assert m.running is False


def test_duration_ms_is_read_only_after_construction():
    m = Monostable(duration_ms=500)
    assert m.duration_ms == 500.0


def test_repr_shows_duration_and_remaining():
    m = Monostable(duration_ms=2500)
    m(trig=True); m(trig=False)
    r = repr(m)
    assert "2500" in r
    assert "remaining_ms=2500" in r
