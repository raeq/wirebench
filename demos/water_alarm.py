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
    """

    __slots__ = ('_red_led', '_green_led')

    def __init__(self) -> None:
        sensor    = ULN2003A(refdes_number=1)
        sn74hc04  = SN74HC04(refdes_number=2)
        cd4069    = CD4069(refdes_number=3)
        cd4043    = CD4043(refdes_number=4)
        red_led   = LED('red',   refdes_number=1)
        green_led = LED('green', refdes_number=2)
        gnd       = Rail(False)   # GND tie for unused CMOS inputs and unused latch cells
        vcc       = Rail(True)    # Vcc tie for the CD4043's OE pin

        wire(sensor.out_1,   cd4043.s_1)
        wire(sensor.out_2,   sn74hc04.a_1)
        wire(sn74hc04.y_1,   cd4043.r_1)
        wire(cd4043.q_1,     red_led.anode)
        # /Q is not a CD4043 package pin — derive it via gate 1 of the CD4069.
        wire(cd4043.q_1,     cd4069.a_1)
        wire(cd4069.y_1,     green_led.anode)
        # CD4043 OE must be tied HIGH for outputs to be enabled.
        wire(vcc.out,        cd4043.oe)
        # CMOS inputs must never float — tie all unused inverter inputs
        # LOW (5 unused gates on the SN74HC04, 5 on the CD4069), and the
        # unused latch S/R inputs LOW (latches 2..4 sit in 'hold').
        wire(gnd.out,
             sn74hc04.a_2, sn74hc04.a_3, sn74hc04.a_4,
             sn74hc04.a_5, sn74hc04.a_6,
             cd4069.a_2, cd4069.a_3, cd4069.a_4,
             cd4069.a_5, cd4069.a_6,
             cd4043.s_2, cd4043.r_2,
             cd4043.s_3, cd4043.r_3,
             cd4043.s_4, cd4043.r_4)

        super().__init__(
            factor_nodes=[sensor, sn74hc04, cd4069, cd4043, red_led, green_led, gnd, vcc],
            ports={'low_probe':  sensor.in_1,
                   'high_probe': sensor.in_2,
                   'state':      cd4043.q_1},
        )

        self._red_led   = red_led
        self._green_led = green_led

    def __call__(self, low_probe: float, high_probe: float) -> bool | None:
        self._ports['low_probe'].drive(low_probe)
        self._ports['high_probe'].drive(high_probe)
        self.evaluate()
        result: bool | None = self._ports['state'].value
        return result

    @property
    def red_led(self) -> LED:
        return self._red_led

    @property
    def green_led(self) -> LED:
        return self._green_led

    @property
    def state(self) -> bool | None:
        return self._ports['state'].value

    def __str__(self) -> str:
        return f"{self._red_led} | {self._green_led}"

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
