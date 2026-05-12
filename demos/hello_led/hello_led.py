"""HelloLED — the minimal viable circuit demo.

A single LED with a series current-limit resistor, driven from the
positive rail.  No chips, no logic, no signal handling — just enough
parts to verify the breadboard, the parts, and the soldering iron all
agree on what "this LED should light up" means.

This demo exists for the assembly-guide exporter, which needs a tiny
deterministic design to render as a golden Markdown file.  The
schematic equivalent:

    VCC ──[R1 = 330 Ω]──[D1 anode → cathode]── GND

Run directly to see the LED state under a single "power applied"
scenario:

    python demos/hello_led/hello_led.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from circuitry import (
    Circuit, wire,
    LED, Rail, Resistor,
    run_scenarios,
)


class HelloLED(Circuit):
    """A single LED with a current-limit resistor across the supply rails.

    Parts:
      R1 — 330 Ω carbon-film resistor
      D1 — red LED, 5 mm through-hole

    Wiring:
      VCC ── R1 ── D1.anode ── D1.cathode ── GND

    Under the framework's voltage-only graph evaluation the resistor is
    opaque — its terminals are passive voltage nodes, so the LED's
    `lit` attribute reports `?` instead of `on` when scenarios run.
    The design exists primarily as a target for the assembly-guide
    exporter; the simulation limitation is honest.

    Composite Circuits omit __slots__ so that `Circuit.__init__` can
    auto-collect parts from `self.__dict__` (insertion order = the
    order of dataflow-sensitive fallback evaluation).
    """

    def __init__(self) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(330, refdes_number=1)
        self.d1  = LED('red', refdes_number=1)

        # R1 is a passive: under graph evaluation its terminals are just
        # voltage nodes joined by Ohm's law.  Wire the anode directly to
        # the supply rail through R1 — the framework treats this as one
        # logical net for evaluation, and the assembly-guide exporter
        # splits it back into two breadboard tie strips with R1
        # bridging them.
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2,   self.d1.anode)
        wire(self.gnd.out, self.d1.cathode)

        super().__init__(
            ports={'lit': self.d1.anode},
        )

    def __call__(self) -> bool | None:
        # No external signal interface — power is hardwired via the rails.
        # Evaluating the design propagates the Rail drives down to the LED.
        self.evaluate()
        return self.d1.lit

    def __repr__(self) -> str:
        return "HelloLED()"


def _main() -> None:
    run_scenarios(
        HelloLED(),
        scenarios=[
            ("power applied", ()),
        ],
        columns=[
            ("d1", lambda c, a, k: 'on' if c.d1.lit else 'off' if c.d1.lit is False else '?'),
        ],
    )


if __name__ == '__main__':
    _main()
