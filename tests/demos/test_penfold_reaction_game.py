"""Targeted topology test for the Penfold reaction-game demo.

The spec's *teaching point* is the *button-stops-clock* topology:
a clock oscillator + a CD4017 decade counter + ten LEDs + a button
that gates the counter.  This test asserts the structural skeleton —
not the timing behaviour, which is opaque under wirebench's voltage-
only graph evaluation (same constraint the dice demo runs into).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DEMO_DIR = Path(__file__).resolve().parent.parent.parent / 'demos' / 'penfold_reaction_game'
if str(_DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMO_DIR))

from framework.refdes import RefdesBearing


@pytest.fixture
def game():
    from penfold_reaction_game import ReactionGame
    return ReactionGame()


def _refdes_classes(circuit) -> dict[str, str]:
    return {
        fn.refdes: type(fn).__name__
        for fn in circuit.parts
        if isinstance(fn, RefdesBearing)
    }


def test_clock_oscillator_present(game):
    """The astable clock is an NE555 — Penfold's choice for P22."""
    classes = _refdes_classes(game)
    assert 'U1' in classes
    assert classes['U1'] == 'NE555'


def test_decade_counter_present(game):
    """Counter is a CD4017 — the chip that makes the demo identifiable."""
    classes = _refdes_classes(game)
    assert 'U2' in classes
    assert classes['U2'] == 'CD4017'


def test_ten_indicator_leds(game):
    """Penfold's ten LEDs (D1..D10) are the readout — one per counter Q."""
    classes = _refdes_classes(game)
    leds = [(rd, cls) for rd, cls in classes.items() if cls == 'LED']
    assert len(leds) == 10
    for n in range(1, 11):
        assert f'D{n}' in classes
        assert classes[f'D{n}'] == 'LED'


def test_button_pressed_port_present(game):
    """The composite exposes a `button_pressed` external port.  This is
    the wirebench expression of Penfold's S1 push-button — no dedicated
    Switch class; the port boundary carries the signal."""
    assert 'button_pressed' in game.ports
    assert 'tick' in game.ports


def test_idle_face_after_no_ticks(game):
    """At construction the counter sits at Q0 → face '1'."""
    face = game(button_pressed=False, ticks=0)
    assert game.counter.count == 0
    assert face == 1


def test_press_advances_counter(game):
    """Holding the button down → CE LOW → counter ticks normally."""
    game(button_pressed=True, ticks=5)
    assert game.counter.count == 5
    assert game.face == 6


def test_release_freezes_counter(game):
    """Release the button → CE HIGH → no further ticks register."""
    game(button_pressed=True,  ticks=3)
    frozen_count = game.counter.count
    game(button_pressed=False, ticks=10)
    assert game.counter.count == frozen_count
