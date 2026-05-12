"""Water-level alarm — composite-circuit demo.

A bench-style assembly of four chips, two LEDs, and Vcc/GND rails that
implements a hysteresis-driven tank-level alarm.  See the WaterAlarm
class docstring for the wiring diagram.

Run directly to see a signal trace through five level scenarios:

    python demos/water_alarm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from circuitry import (
    Circuit, wire,
    LED, Rail,
    ULN2003A, SN74HC04, CD4069, CD4043,
    run_scenarios,
)


class WaterAlarm(Circuit):
    """Water level alarm.

    Two probes are mounted in the tank at the minimum and maximum water levels.
    Drive each probe with Vcc (≥ 1V) when submerged, 0 V when dry.

    ULN2003A output is open-collector: HIGH when transistor off (probe dry),
    LOW when transistor conducting (probe submerged).

    Wiring:
      low_probe  → ULN2003A ch1                   → CD4043 S  (HIGH=dry → set alarm)
      high_probe → ULN2003A ch2 → SN74HC04 gate 1 → CD4043 R  (LOW=wet → inverted → reset)
      CD4043 Q                                    → red LED   (alarm active)
      CD4043 Q   → CD4069 gate 1                  → green LED (alarm clear; /Q derived externally)

    Real CD4043B silicon does not bond /Q out to a package pin, so the
    green LED's drive is generated externally by inverting Q.  We use a
    second inverter chip (CD4069) for that; sharing gates of the same
    SN74HC04 between the high-probe inversion and the Q inversion would
    place the chip on both sides of the latch in the dataflow,
    appearing as a cycle to the framework's chip-granularity
    topological sort.  Splitting the function across two chips keeps
    the graph acyclic.

    Leave unused CMOS inputs tied to GND or Vcc — never floating.

    Composite Circuits omit __slots__ so that `Circuit.__init__` can
    auto-collect parts from `self.__dict__` (insertion order = the
    order of dataflow-sensitive fallback evaluation, but this design
    has no feedback cycle, so order is irrelevant).
    """

    def __init__(self) -> None:
        # Parts — assigning to `self.x` puts them in `__dict__` so the
        # base Circuit will collect them when we call super().__init__()
        # below.  Public names so consumers and tests can reach them
        # directly (no `_foo` plus `@property def foo` boilerplate).
        self.sensor    = ULN2003A(refdes_number=1)
        self.sn74hc04  = SN74HC04(refdes_number=2)
        self.cd4069    = CD4069(refdes_number=3)
        self.cd4043    = CD4043(refdes_number=4)
        self.red_led   = LED('red',   refdes_number=1)
        self.green_led = LED('green', refdes_number=2)
        self.gnd       = Rail(False)   # GND tie for unused CMOS inputs and unused latch cells
        self.vcc       = Rail(True)    # Vcc tie for the CD4043's OE pin

        wire(self.sensor.out_1,   self.cd4043.s_1)
        wire(self.sensor.out_2,   self.sn74hc04.a_1)
        wire(self.sn74hc04.y_1,   self.cd4043.r_1)
        wire(self.cd4043.q_1,     self.red_led.anode)
        # /Q is not a CD4043 package pin — derive it via gate 1 of the CD4069.
        wire(self.cd4043.q_1,     self.cd4069.a_1)
        wire(self.cd4069.y_1,     self.green_led.anode)
        # CD4043 OE must be tied HIGH for outputs to be enabled.
        wire(self.vcc.out,        self.cd4043.oe)
        # CMOS inputs must never float — tie all unused inverter inputs
        # LOW (5 unused gates on the SN74HC04, 5 on the CD4069), and the
        # unused latch S/R inputs LOW (latches 2..4 sit in 'hold').
        wire(self.gnd.out,
             self.sn74hc04.a_2, self.sn74hc04.a_3, self.sn74hc04.a_4,
             self.sn74hc04.a_5, self.sn74hc04.a_6,
             self.cd4069.a_2, self.cd4069.a_3, self.cd4069.a_4,
             self.cd4069.a_5, self.cd4069.a_6,
             self.cd4043.s_2, self.cd4043.r_2,
             self.cd4043.s_3, self.cd4043.r_3,
             self.cd4043.s_4, self.cd4043.r_4)

        super().__init__(
            ports={'low_probe':  self.sensor.in_1,
                   'high_probe': self.sensor.in_2,
                   'state':      self.cd4043.q_1},
        )

    def __call__(self, low_probe: float, high_probe: float) -> bool | None:
        self._ports['low_probe'].drive(low_probe)
        self._ports['high_probe'].drive(high_probe)
        self.evaluate()
        result: bool | None = self._ports['state'].value
        return result

    @property
    def state(self) -> bool | None:
        return self._ports['state'].value

    def __str__(self) -> str:
        return f"{self.red_led} | {self.green_led}"

    def __repr__(self) -> str:
        return "WaterAlarm()"


def _level(v: bool | None) -> str:
    return 'H' if v else 'L' if v is False else '?'


def _main() -> None:
    VCC, GND = 5.0, 0.0
    run_scenarios(
        WaterAlarm(),
        scenarios=[
            ("initial — tank empty",                  (GND, GND)),
            ("water touches low probe (held set)",    (VCC, GND)),
            ("water reaches high probe (reset)",      (VCC, VCC)),
            ("water recedes below high (held clr)",   (VCC, GND)),
            ("water gone again (set)",                (GND, GND)),
        ],
        columns=[
            ("low",   lambda c, a, k: f"{a[0]:.1f}"),
            ("high",  lambda c, a, k: f"{a[1]:.1f}"),
            ("red",   lambda c, a, k: 'on'  if c.red_led.lit  else 'off' if c.red_led.lit  is False else '?'),
            ("green", lambda c, a, k: 'on'  if c.green_led.lit else 'off' if c.green_led.lit is False else '?'),
            ("state", lambda c, a, k: _level(c.state)),
        ],
    )


if __name__ == '__main__':
    _main()
