"""Pin function classification — what a package pin's role is at the
bench level, independent of how its value is encoded for the simulator.

The framework already has `signal_type` (Digital / Analog) and
`Direction` (IN / OUT / BIDIR).  Those answer "how is this pin's value
represented" and "which way does it flow."  They don't answer "is this
pin power, ground, reference, reset, clock-in, or no-connect" — which
is the question that drives bench correctness: every chip's supply
pins MUST be wired or the part doesn't function, every RESET line
floating is unpredictable behaviour, every undriven REFERENCE makes
the ADC read garbage.

Roles currently classified:

  POWER     — supply input            (VCC / VDD / AVCC / VBUS)
  GROUND    — return                  (GND / VSS / AGND / DGND)
  REFERENCE — analog reference input  (AREF / VREF / VBG / BG_REF)
  RESET     — chip reset input        (RESET / RST / NRST / nRESET /
                                       RST_N / RESET_B)
  CLOCK_IN  — external clock input    (CLKIN / EXTCLK / OSCIN / CLK_IN)
  NC        — explicit no-connect     (NC / N.C. / DNC)

Crystal-pair pins (XTAL1 / XTAL2) are deliberately NOT in this enum:
they're a *pair* sharing one oscillator loop, not a single-pin role,
and modelling them properly needs a Crystal connection part rather
than a per-pin function label.  Output-enable pins (OE / OE1 / OE2),
chip-select (CS / CE), and protocol-specific signals (SDA / SCL / MISO
/ MOSI / SCK) are also out of scope here — those are direction +
drive-type concerns, not role concerns, and grow elsewhere.

Classification is name-based, anchored regex, case-insensitive.  Chips
whose silkscreen deviates from the canonical names can override on a
case-by-case basis via the `PIN_FUNCTIONS` ClassVar on the chip class:

    class WeirdChip(Chip):
        PIN_FUNCTIONS = {'PWR': PinFunction.POWER, 'RTN': PinFunction.GROUND}
"""
from __future__ import annotations

import re
from enum import Enum


class PinFunction(Enum):
    """The bench-level role of a package pin."""
    POWER     = 'power'
    GROUND    = 'ground'
    REFERENCE = 'reference'
    RESET     = 'reset'
    CLOCK_IN  = 'clock_in'
    NC        = 'nc'


# Canonical regex table — one entry per role.  Patterns are anchored
# (^...$) so a near-miss like `VDD_SENSE` does NOT silently match
# POWER, and `RESET_BUT_NOT_REALLY` does NOT silently match RESET.
# The table order is the lookup order — first match wins.  Roles that
# share name fragments (e.g. RESET / RST overlap with REFERENCE's
# REF prefix in some chip families) are kept disjoint by anchoring;
# add new patterns with disjointness in mind.
_PATTERNS: tuple[tuple[re.Pattern[str], PinFunction], ...] = (
    (re.compile(r'^(?:VCC|VDD|AVCC|VBUS)$',                re.IGNORECASE), PinFunction.POWER),
    (re.compile(r'^(?:GND|VSS|AGND|DGND)$',                re.IGNORECASE), PinFunction.GROUND),
    (re.compile(r'^(?:VREF|AREF|VBG|BG_REF)$',             re.IGNORECASE), PinFunction.REFERENCE),
    (re.compile(r'^(?:NRESET|RESET|NRST|RST|RST_N|RESET_B)$', re.IGNORECASE), PinFunction.RESET),
    (re.compile(r'^(?:CLKIN|EXTCLK|OSCIN|CLK_IN)$',        re.IGNORECASE), PinFunction.CLOCK_IN),
    (re.compile(r'^(?:NC|N\.C\.|DNC)$',                    re.IGNORECASE), PinFunction.NC),
)


def infer_pin_function(pin_name: str) -> PinFunction | None:
    """Classify a pin by its name.  Returns None for signal pins."""
    for pattern, function in _PATTERNS:
        if pattern.match(pin_name):
            return function
    return None
