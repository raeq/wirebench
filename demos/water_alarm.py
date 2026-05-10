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

from framework.circuit import Circuit
from framework.wire import wire
from components.chips.uln2003a import ULN2003A
from components.chips.sn74hc04 import SN74HC04
from components.chips.cd4069 import CD4069
from components.chips.cd4043 import CD4043
from components.passives.led import LED
from components.passives.rail import Rail


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

        wire(sensor.ports['out_1'],  cd4043.ports['s_1'])
        wire(sensor.ports['out_2'],  sn74hc04.ports['a_1'])
        wire(sn74hc04.ports['y_1'],  cd4043.ports['r_1'])
        wire(cd4043.ports['q_1'],    red_led.ports['anode'])
        # /Q is not a CD4043 package pin — derive it via gate 1 of the CD4069.
        wire(cd4043.ports['q_1'],    cd4069.ports['a_1'])
        wire(cd4069.ports['y_1'],    green_led.ports['anode'])
        # CD4043 OE must be tied HIGH for outputs to be enabled.
        wire(vcc.ports['out'], cd4043.ports['oe'])
        # CMOS inputs must never float — tie all unused inverter inputs
        # LOW (5 unused gates on the SN74HC04, 5 on the CD4069), and the
        # unused latch S/R inputs LOW (latches 2..4 sit in 'hold').
        wire(gnd.ports['out'],
             sn74hc04.ports['a_2'], sn74hc04.ports['a_3'], sn74hc04.ports['a_4'],
             sn74hc04.ports['a_5'], sn74hc04.ports['a_6'],
             cd4069.ports['a_2'], cd4069.ports['a_3'], cd4069.ports['a_4'],
             cd4069.ports['a_5'], cd4069.ports['a_6'],
             cd4043.ports['s_2'], cd4043.ports['r_2'],
             cd4043.ports['s_3'], cd4043.ports['r_3'],
             cd4043.ports['s_4'], cd4043.ports['r_4'])

        super().__init__(
            factor_nodes=[sensor, sn74hc04, cd4069, cd4043, red_led, green_led, gnd, vcc],
            ports={'low_probe':  sensor.ports['in_1'],
                   'high_probe': sensor.ports['in_2'],
                   'state':      cd4043.ports['q_1']},
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

    def __str__(self) -> str:
        return f"{self._red_led} | {self._green_led}"

    def __repr__(self) -> str:
        return "WaterAlarm()"


def _main() -> None:
    """Run a five-step level scenario and print a per-chip signal trace."""
    from framework.refdes import RefdesBearing

    VCC, GND = 5.0, 0.0
    wa = WaterAlarm()

    print("Bill of materials:")
    chips = [fn for fn in wa._factor_nodes if isinstance(fn, RefdesBearing)]
    for fn in chips:
        print(f"  {fn.refdes:5s} {type(fn).__name__}")
    print()

    scenarios = [
        ("initial — tank empty",                GND, GND),
        ("water touches low probe (held set)",  VCC, GND),
        ("water reaches high probe (reset)",    VCC, VCC),
        ("water recedes below high (held clr)", VCC, GND),
        ("water gone again (set)",              GND, GND),
    ]

    def chip_state(fn: object) -> str:
        cls = type(fn).__name__
        if cls == 'ULN2003A':
            outs = fn.output_levels  # type: ignore[attr-defined]
            return _level(outs[0])
        if cls in ('SN74HC04', 'CD4069'):
            return _level(fn.ports['y_1'].value)  # type: ignore[attr-defined]
        if cls == 'CD4043':
            return _level(fn.ports['q_1'].value)  # type: ignore[attr-defined]
        if cls == 'LED':
            lit = fn.lit  # type: ignore[attr-defined]
            return 'on ' if lit else 'off' if lit is False else ' ? '
        return '?'

    hdr = '  '.join(f'{c.refdes:>4s}' for c in chips)
    print(f'{"event":40s} | low | high | {hdr} | state')
    print('-' * (40 + 14 + 4 * len(chips) + 6 + 9))
    for label, low, high in scenarios:
        state = wa(low, high)
        cells = '  '.join(f'{chip_state(c):>4s}' for c in chips)
        print(f'{label:40s} | {low:>3.1f} | {high:>4.1f} | {cells} | {state}')


def _level(v: bool | None) -> str:
    return 'H' if v else 'L' if v is False else '?'


if __name__ == '__main__':
    _main()
