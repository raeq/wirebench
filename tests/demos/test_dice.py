import warnings

import pytest


def _make_dice():
    # The Q6 → RST feedback wire makes the parent's topological sort
    # fall back to declaration order — the warning at construction is
    # expected.  Suppress it here so the tests stay clean.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        from dice import Dice
        return Dice()


@pytest.fixture
def dice():
    return _make_dice()


def test_bom_present(dice):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in dice._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    # Two ICs.
    assert "NE555.U1"  in parts
    assert "CD4017.U2" in parts
    # Six 1N4148s.
    for n in range(1, 7):
        assert f"D1N4148.D{n}" in parts
    # Seven red LEDs (D7..D13).
    for n in range(7, 14):
        assert f"LED.D{n}" in parts
    # Four resistors at LEDs, three at the 555 + pull-up.
    for n in range(1, 8):
        assert f"Resistor.R{n}" in parts
    # Two capacitors.
    assert "Capacitor.C1" in parts
    assert "Capacitor.C2" in parts


def test_initial_count_is_zero_face_is_two(dice):
    """At construction the counter sits at Q0 — the dice's mapped face
    is roll 2 (the project starts its sequence at 2 to save diodes)."""
    face = dice(button_pressed=False, ticks=0)
    assert dice.counter.count == 0
    assert face == 2


def test_button_held_advances_one_count_per_tick(dice):
    """Each tick is one rising-then-falling clock cycle.  With the
    button pressed (CE LOW) every tick must increment the counter."""
    dice(button_pressed=False, ticks=0)
    for expected in (1, 2, 3, 4, 5):
        dice(button_pressed=True, ticks=1)
        assert dice.counter.count == expected


def test_button_released_freezes_count(dice):
    """Releasing the button (CE HIGH) inhibits the counter — any
    further ticks must leave count unchanged."""
    dice(button_pressed=True, ticks=3)
    frozen = dice.counter.count
    for _ in range(5):
        dice(button_pressed=False, ticks=1)
        assert dice.counter.count == frozen


def test_q6_reset_wraps_cycle_to_six_faces(dice):
    """After six ticks the counter rolls over via Q6 → RST and the
    next face is roll 2 again, not roll 1 or a stale state."""
    faces_seen = []
    dice(button_pressed=False, ticks=0)   # settle initial state
    for _ in range(6):
        face = dice(button_pressed=True, ticks=1)
        faces_seen.append(face)
    # Six consecutive ticks produce rolls 3, 4, 5, 6, 1, 2 in order.
    assert faces_seen == [3, 4, 5, 6, 1, 2]


def test_face_one_lights_only_centre(dice):
    """Roll 1 corresponds to Q5 active → only LED A drives."""
    dice(button_pressed=True, ticks=5)
    assert dice.face == 1
    assert dice.lit_leds == ('A',)


def test_face_two_lights_one_diagonal_pair(dice):
    """Roll 2 corresponds to Q0 active.  CO drives LED B1+B2."""
    dice(button_pressed=False, ticks=0)
    assert dice.face == 2
    assert set(dice.lit_leds) == {'B1', 'B2'}


def test_face_three_lights_diagonal_and_centre(dice):
    """Roll 3 = Q1 active.  CO drives B-pair, OR_A drives centre."""
    dice(button_pressed=False, ticks=0)
    dice(button_pressed=True, ticks=1)
    assert dice.face == 3
    assert set(dice.lit_leds) == {'A', 'B1', 'B2'}


def test_face_four_lights_both_diagonals(dice):
    """Roll 4 = Q2 active.  Both diagonal pairs lit, no centre, no middle."""
    dice(button_pressed=False, ticks=0)
    dice(button_pressed=True, ticks=2)
    assert dice.face == 4
    assert set(dice.lit_leds) == {'B1', 'B2', 'C1', 'C2'}


def test_face_five_lights_both_diagonals_and_centre(dice):
    """Roll 5 = Q3 active.  Diagonals + centre."""
    dice(button_pressed=False, ticks=0)
    dice(button_pressed=True, ticks=3)
    assert dice.face == 5
    assert set(dice.lit_leds) == {'A', 'B1', 'B2', 'C1', 'C2'}


def test_face_six_lights_diagonals_and_middle(dice):
    """Roll 6 = Q4 active.  Diagonals + middle pair, no centre."""
    dice(button_pressed=False, ticks=0)
    dice(button_pressed=True, ticks=4)
    assert dice.face == 6
    assert set(dice.lit_leds) == {'B1', 'B2', 'C1', 'C2', 'D1', 'D2'}


def test_render_returns_three_line_pip_diagram(dice):
    dice(button_pressed=False, ticks=0)
    out = dice.render()
    assert out.count('\n') == 3   # three lines + trailing newline
