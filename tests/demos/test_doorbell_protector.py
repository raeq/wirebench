import warnings

import pytest


def _make():
    # The IC2→inverter→IC1 feedback wire creates a topo-sort cycle;
    # the warning at construction is expected.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from doorbell_protector import DoorbellProtector
        return DoorbellProtector()


@pytest.fixture
def protector():
    return _make()


def test_bom_present(protector):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in protector._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    # Two LM555s (subclass), two transistors, two diodes, relay.
    assert "NE555_Monostable.U1" in parts
    assert "NE555_Monostable.U2" in parts
    assert "BC548.Q1"            in parts
    assert "Q2N3904.Q2"          in parts
    assert "D1N4007.D1"          in parts
    assert "LED.D2"              in parts
    assert "Relay_SPDT.K1"       in parts
    # Eight resistors and five capacitors per the project BOM.
    for n in range(1, 9):
        assert f"Resistor.R{n}" in parts
    for n in range(1, 6):
        assert f"Capacitor.C{n}" in parts


def test_initial_state_quiet(protector):
    """At rest the relay is on NC, no bell, no lock-out."""
    protector(button_pressed=False, advance_ms=0)
    assert protector.bell_ringing is False
    assert protector.locked_out   is False


def test_press_starts_5s_bell(protector):
    protector(button_pressed=False, advance_ms=0)
    assert protector(button_pressed=True, advance_ms=10) is True
    assert protector.bell_remaining_ms == 5000


def test_press_during_bell_does_not_restart(protector):
    """A second press while IC1 is running must be ignored — no reset
    of the 5 s pulse."""
    protector(button_pressed=False, advance_ms=0)
    protector(button_pressed=True,  advance_ms=10)     # bell starts
    protector(button_pressed=False, advance_ms=2_000)  # 2 s of bell
    before = protector.bell_remaining_ms
    protector(button_pressed=True,  advance_ms=10)     # second press
    after = protector.bell_remaining_ms
    assert after < before                              # time ticked
    assert after > 2_000                                # not reset to 5000


def test_bell_ends_after_5s_and_lockout_begins(protector):
    """When IC1.OUT falls, IC2 must trigger on the falling edge and
    start its 50 s lock-out pulse."""
    protector(button_pressed=False, advance_ms=0)
    protector(button_pressed=True,  advance_ms=10)
    protector(button_pressed=False, advance_ms=5_000)
    assert protector.bell_ringing is False
    assert protector.locked_out   is True
    assert protector.lockout_remaining_ms == 50_000


def test_press_during_lockout_does_not_ring(protector):
    """While IC2 holds IC1.RESET low the bell cannot retrigger."""
    protector(button_pressed=False, advance_ms=0)
    protector(button_pressed=True,  advance_ms=10)
    protector(button_pressed=False, advance_ms=5_000)   # bell ends, lockout starts
    protector(button_pressed=True,  advance_ms=1_000)   # press 1 s into lockout
    assert protector.bell_ringing is False
    assert protector.locked_out   is True


def test_lockout_decrements_with_time(protector):
    protector(button_pressed=False, advance_ms=0)
    protector(button_pressed=True,  advance_ms=10)
    protector(button_pressed=False, advance_ms=5_000)
    initial_lock = protector.lockout_remaining_ms
    protector(button_pressed=False, advance_ms=10_000)
    assert protector.lockout_remaining_ms == initial_lock - 10_000


def test_press_after_lockout_clears_rings_bell(protector):
    """Once IC2 finishes and the inverter has had one more evaluate
    to propagate the RESET HIGH, a new press should fire IC1 again."""
    protector(button_pressed=False, advance_ms=0)
    protector(button_pressed=True,  advance_ms=10)
    protector(button_pressed=False, advance_ms=5_000)   # bell ends, lockout starts
    # Run out the whole 50 s lock-out, plus one settle cycle for the
    # inverter → RESET propagation (the cycle warning's one-cycle lag).
    protector(button_pressed=False, advance_ms=50_000)
    protector(button_pressed=False, advance_ms=10)
    assert protector.locked_out is False
    # Now a fresh press must work.
    assert protector(button_pressed=True, advance_ms=10) is True
    assert protector.bell_remaining_ms == 5_000


def test_relay_state_matches_bell_ringing(protector):
    protector(button_pressed=False, advance_ms=0)
    assert protector.relay.closed_path == 'nc'
    protector(button_pressed=True, advance_ms=10)
    assert protector.relay.closed_path == 'no'
    assert protector.bell_ringing is True


def test_release_alone_does_not_trigger(protector):
    """A button release (LOW→HIGH on the active-LOW trigger) must
    never re-fire the bell."""
    protector(button_pressed=False, advance_ms=0)
    assert protector.bell_ringing is False
    protector(button_pressed=False, advance_ms=10)   # idle release
    assert protector.bell_ringing is False


def test_multiple_consecutive_idle_calls_stay_quiet(protector):
    protector(button_pressed=False, advance_ms=0)
    for _ in range(5):
        protector(button_pressed=False, advance_ms=100)
        assert protector.bell_ringing is False
        assert protector.locked_out   is False
