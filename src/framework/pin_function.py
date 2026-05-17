"""Pin function classification — what a package pin's role is at the
bench level, independent of how its value is encoded for the simulator.

The framework already has `signal_type` (Digital / Analog) and
`Direction` (IN / OUT / BIDIR).  Those answer "how is this pin's value
represented" and "which way does it flow."  They don't answer "is this
pin power, ground, or signal" — which is the question that drives bench
correctness: every chip's supply pins MUST be wired or the part
doesn't function.

Scope deliberately minimal — POWER and GROUND only.  Reference, special-
function (RESET, XTAL), and signal subdivision (digital I/O, analog
I/O, protocol-specific) are out of scope until the Power+Ground
machinery proves out.  A chip pin without a recognised power / ground
name gets `None` here and is treated as a signal pin by every consumer.

Classification is inferred from the pin's name with a canonical regex.
Chips whose silkscreen deviates from convention can override on a
case-by-case basis via the `PIN_FUNCTIONS` ClassVar on the chip class:

    class WeirdChip(Chip):
        PIN_FUNCTIONS = {'PWR': PinFunction.POWER, 'RTN': PinFunction.GROUND}
"""
from __future__ import annotations

import re
from enum import Enum


class PinFunction(Enum):
    """The bench-level role of a package pin."""
    POWER  = 'power'    # supply rail input — VCC / VDD / AVCC / VBUS
    GROUND = 'ground'   # return — GND / VSS / AGND / DGND


# Canonical regex for the standard supply and ground names.  Case-
# insensitive to handle datasheet variations.  The patterns are
# anchored so they only match whole pin names — a signal pin named
# `VDD_SENSE` (rare but exists) does NOT get classified as POWER.
_POWER_NAMES = re.compile(
    r'^(?:VCC|VDD|AVCC|VBUS)$', re.IGNORECASE,
)
_GROUND_NAMES = re.compile(
    r'^(?:GND|VSS|AGND|DGND)$', re.IGNORECASE,
)


def infer_pin_function(pin_name: str) -> PinFunction | None:
    """Classify a pin by its name.  Returns None for signal pins."""
    if _POWER_NAMES.match(pin_name):
        return PinFunction.POWER
    if _GROUND_NAMES.match(pin_name):
        return PinFunction.GROUND
    return None
