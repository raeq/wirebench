"""Drive-type classification — how an OUT (or BIDIR) pin's output
stage behaves at the bench level, independent of its `PinFunction`
role or its `signal_type` encoding.

`signal_type` answers "how is this pin's value represented" (Digital
or Analog).  `PinFunction` answers "what is this pin for at the
system level" (POWER, GROUND, REFERENCE, …).  `DriveType` answers
"what kind of transistor is at the pin, and what does the rest of the
circuit have to provide to make the pin useful?"

The axis matters because a chip's silicon dictates whether the user
needs to add a pull-up resistor.  A push-pull output drives both HIGH
and LOW unaided; an open-drain or open-collector output can only
pull LOW — without an external pull-up to a positive rail, the line
floats when the transistor is off and downstream logic sees an
undefined level.  ERC catches the missing pull-up the same way Stage
B catches a floating RESET.

Members:

  PUSH_PULL       — default — totem-pole CMOS or push-pull bipolar
                    output that drives both HIGH and LOW.  No external
                    pull required.
  OPEN_DRAIN      — NMOS pull-down only.  Output sinks LOW when the
                    transistor conducts and floats high-impedance
                    otherwise.  Requires an external pull-up resistor
                    to a positive rail, or a wired-AND with another
                    open-drain output sharing the same pull-up
                    (I²C bus convention).
  OPEN_COLLECTOR  — BJT collector pull-down only.  Electrically
                    equivalent to OPEN_DRAIN at the bench level
                    (Darlington outputs, classic open-collector logic,
                    LM-series comparator outputs).  The distinction is
                    silicon technology, not user-facing wiring.
  TRI_STATE       — push-pull output with a high-Z disable.  Treated
                    as labelling only in this stage: the framework's
                    static analysis can't enforce "exactly one driver
                    asserts at a time" without temporal state.  Stage
                    D may add an ERC rule once a default-driver-on-net
                    notion exists; until then the value is metadata.

Crystal-pair pins (XTAL1 / XTAL2), differential pairs (LVDS, USB
D±), and RF-specific drives stay out of scope here — those are
multi-pin protocol concerns rather than per-pin drive-type concerns.
"""
from __future__ import annotations

from enum import Enum


class DriveType(Enum):
    """How an OUT / BIDIR pin's output stage behaves at the bench."""
    PUSH_PULL      = 'push_pull'
    OPEN_DRAIN     = 'open_drain'
    OPEN_COLLECTOR = 'open_collector'
    TRI_STATE      = 'tri_state'
