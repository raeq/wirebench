"""Assembly-guide exporter tests.

Covers spec §8 tests 6–10:

  6.  End-to-end emit for every breadboard-compatible demo.
  7.  Refusal raises BreadboardIncompatibleError naming offending parts.
  8.  Component-specific GOTCHAS appear in the output.
  9.  Duplicate gotchas deduplicate.
 10.  Deterministic output (idempotent across two exports).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make demos/ importable for the e2e tests.
_DEMOS = Path(__file__).resolve().parents[4] / 'demos'
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))

import components.chips     # noqa: F401 — registry side effects
import components.diodes    # noqa: F401
import components.passives  # noqa: F401
import components.transistors  # noqa: F401
import components.connectors  # noqa: F401

from framework.errors import BreadboardIncompatibleError
from framework.export import export_to_string

from circuitry import Circuit, LED, Rail, Resistor, wire


# ----------------------------------------------------------------- e2e

def test_hello_led_emits_four_sections() -> None:
    """A trivial design emits all four section headings and contains
    one BOM row per refdes-bearing part."""
    from hello_led import HelloLED
    text = export_to_string(HelloLED(), 'assembly_guide')
    for heading in ('# Build Guide:', '## Parts', '## Method', '## Notes & Gotchas'):
        assert heading in text, f"missing section {heading!r}"
    # Two refdes-bearing parts: R1 and D1.
    assert '| R1 |' in text
    assert '| D1 |' in text


def test_water_alarm_emits_full_guide() -> None:
    from water_alarm import WaterAlarm
    text = export_to_string(WaterAlarm(), 'assembly_guide')
    # The four chips appear as ingredients.
    for refdes in ('U1', 'U2', 'U3', 'U4'):
        assert f"| {refdes} |" in text
    # Each chip step names the chip's package by pin count.
    assert 'DIP-16' in text or 'DIP-14' in text


# ------------------------------------------------------------- refusal

class _OnlySMDDesign(Circuit):
    """A minimal design containing one SMD part — triggers refusal."""
    def __init__(self) -> None:
        from components.chips.atmega2560 import ATmega2560
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.u1  = ATmega2560(refdes_number=1)
        # No wires required for the refusal test — refusal happens
        # before the placement pass.
        super().__init__(factor_nodes=[self.vcc, self.gnd, self.u1],
                         ports={})

    def __call__(self) -> None: pass


def test_refusal_names_smd_parts() -> None:
    """When the design contains any SMD part, refusal raises
    `BreadboardIncompatibleError` and the message names the offending
    refdes + class."""
    with pytest.raises(BreadboardIncompatibleError, match='ATmega2560'):
        export_to_string(_OnlySMDDesign(), 'assembly_guide')


def test_refusal_for_top_level_board() -> None:
    """The spec §10 calls for refusal of `Board` and multi-board
    top-levels.  Construct a minimal Board and verify."""
    from framework.board import Board
    from components.connectors.headers import Header1xNMale
    j1 = Header1xNMale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    board = Board(
        name='Test', revision='r1',
        components=[j1],
        refdes_number=1,
    )
    with pytest.raises(BreadboardIncompatibleError, match='Board'):
        export_to_string(board, 'assembly_guide')


# --------------------------------------------------------------- gotchas

def test_led_polarity_gotcha_in_output() -> None:
    """Any design containing an LED produces the LED polarity warning
    in the Notes & Gotchas section.  Per spec §5.4."""
    from hello_led import HelloLED
    text = export_to_string(HelloLED(), 'assembly_guide')
    assert 'LED polarity' in text
    assert 'longer lead' in text.lower()


def test_general_gotchas_emitted() -> None:
    """Universal gotchas appear in the output for every design,
    regardless of the parts list."""
    from hello_led import HelloLED
    text = export_to_string(HelloLED(), 'assembly_guide')
    # General gotchas use specific markers we can grep for.
    assert 'supply voltage' in text.lower()
    assert 'Tie unused CMOS inputs' in text


class _ThreeLEDs(Circuit):
    """Design with three LEDs — triggers the dedup test."""
    def __init__(self) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(330, refdes_number=1)
        self.r2  = Resistor(330, refdes_number=2)
        self.r3  = Resistor(330, refdes_number=3)
        self.d1  = LED('red',   refdes_number=1)
        self.d2  = LED('green', refdes_number=2)
        self.d3  = LED('blue',  refdes_number=3)
        for r, d in [(self.r1, self.d1), (self.r2, self.d2), (self.r3, self.d3)]:
            wire(self.vcc.out, r.t1)
            wire(r.t2,         d.anode)
            wire(self.gnd.out, d.cathode)
        super().__init__(ports={})

    def __call__(self) -> None: pass


def test_duplicate_gotchas_deduplicate() -> None:
    """Three LEDs in a design produce the LED polarity warning *once*,
    not three times."""
    text = export_to_string(_ThreeLEDs(), 'assembly_guide')
    assert text.count('**LED polarity matters.**') == 1


# ------------------------------------------------------ determinism

def test_determinism() -> None:
    """Two exports of the same design produce byte-identical output."""
    from hello_led import HelloLED
    a = export_to_string(HelloLED(), 'assembly_guide')
    b = export_to_string(HelloLED(), 'assembly_guide')
    assert a == b
