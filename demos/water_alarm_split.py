"""Water-level alarm, split across two boards.

The same circuit as `demos/water_alarm.py`, re-cast as two physical
PCBs mated through a 40-pin GPIO header pair (Raspberry-Pi HAT style).

Layout
------
  SensorBoard      ULN2003A + Header2xNFemale(40-pin)
                   J1.p1 = VCC, p2 = GND, p3 = low_probe, p4 = high_probe,
                   p5 = conditioned low (open-collector), p6 = conditioned high.

  ControllerBoard  SN74HC04 + CD4069 + CD4043 + 2 LEDs + Vcc/GND rails
                   + Header2xNMale(40-pin).  Mates into SensorBoard via
                   the GPIO header.  Only the 6 sensor-data pins are
                   wired through; the other 34 pins are unconnected on
                   this design.

  WaterAlarmAssembly  composes A1 (sensor) and A2 (controller), calls
                       mate(), and exposes the probe inputs and LED
                       state for the demo trace.

Run directly:

    python demos/water_alarm_split.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from circuitry import (
    Board, Circuit, mate, wire,
    LED, Rail,
    CD4043, CD4069, SN74HC04, ULN2003A,
    run_scenarios,
)
from components.connectors.headers import Header2xNFemale, Header2xNMale


class SensorBoard(Board):
    """Conditions raw probe voltages into clean logic-level signals
    suitable for transmission to the controller board over the GPIO
    header.
    """

    def __init__(self, *, refdes_number: int) -> None:
        self.sensor    = ULN2003A(refdes_number=1)
        self.connector = Header2xNFemale(pin_count=40, pitch_mm=2.54, refdes_number=1)

        # Probe inputs come in on the connector and go to the ULN2003A;
        # ULN2003A outputs (open-collector) go back out on the connector.
        wire(self.connector.pins[2].internal, self.sensor.in_1)   # J1.p3
        wire(self.connector.pins[3].internal, self.sensor.in_2)   # J1.p4
        wire(self.sensor.out_1, self.connector.pins[4].internal)  # J1.p5
        wire(self.sensor.out_2, self.connector.pins[5].internal)  # J1.p6

        super().__init__(
            name='Sensor Board',
            revision='A',
            refdes_number=refdes_number,
        )


class ControllerBoard(Board):
    """Reads conditioned sensor outputs over the GPIO header, drives
    the alarm latch and indicator LEDs."""

    def __init__(self, *, refdes_number: int) -> None:
        self.sn74hc04  = SN74HC04(refdes_number=1)
        self.cd4069    = CD4069  (refdes_number=2)
        self.cd4043    = CD4043  (refdes_number=3)
        self.red_led   = LED('red',   refdes_number=1)
        self.green_led = LED('green', refdes_number=2)
        self.gnd       = Rail(False)
        self.vcc       = Rail(True)
        self.connector = Header2xNMale(pin_count=40, pitch_mm=2.54, refdes_number=1)

        # Sensor outputs arrive on P1.p5 (conditioned low_probe) and
        # P1.p6 (conditioned high_probe).
        wire(self.connector.pins[4].internal, self.cd4043.s_1)    # P1.p5
        wire(self.connector.pins[5].internal, self.sn74hc04.a_1)  # P1.p6
        wire(self.sn74hc04.y_1, self.cd4043.r_1)

        # Q drives red LED directly; /Q derived from Q via CD4069 gate 1.
        wire(self.cd4043.q_1, self.red_led.anode)
        wire(self.cd4043.q_1, self.cd4069.a_1)
        wire(self.cd4069.y_1, self.green_led.anode)

        # CD4043 OE tied HIGH.
        wire(self.vcc.out, self.cd4043.oe)

        # Tie off all unused CMOS inputs and unused latch S/R inputs.
        wire(self.gnd.out,
             self.sn74hc04.a_2, self.sn74hc04.a_3, self.sn74hc04.a_4,
             self.sn74hc04.a_5, self.sn74hc04.a_6,
             self.cd4069.a_2, self.cd4069.a_3, self.cd4069.a_4,
             self.cd4069.a_5, self.cd4069.a_6,
             self.cd4043.s_2, self.cd4043.r_2,
             self.cd4043.s_3, self.cd4043.r_3,
             self.cd4043.s_4, self.cd4043.r_4)

        super().__init__(
            name='Controller Board',
            revision='A',
            refdes_number=refdes_number,
        )


class WaterAlarmAssembly(Circuit):
    """Stacked assembly: SensorBoard (A1) mated to ControllerBoard (A2)
    via a 40-pin GPIO header pair.  Surface inputs are the two probe
    voltages on the sensor board; the controller's LEDs are read via
    component handles.

    Omits __slots__ so `Circuit.__init__` can auto-collect the two
    boards from `self.__dict__`."""

    def __init__(self) -> None:
        self.sensor     = SensorBoard    (refdes_number=1)
        self.controller = ControllerBoard(refdes_number=2)

        # Mate the only connector on each board.
        mate(self.sensor.connectors[0], self.controller.connectors[0])

        # Board ports are dotted by connector refdes (e.g. 'J1.p3'),
        # so attribute access can't reach them — use the dict form.
        super().__init__(
            ports={
                'low_probe':  self.sensor.ports['J1.p3'],
                'high_probe': self.sensor.ports['J1.p4'],
            },
        )

    def __call__(self, low_probe: float, high_probe: float) -> bool | None:
        self._ports['low_probe'].drive(low_probe)
        self._ports['high_probe'].drive(high_probe)
        self.evaluate()
        # Latch state on the controller board.
        result: bool | None = self.controller.red_led.lit
        return result

    def __str__(self) -> str:
        return f"{self.controller.red_led} | {self.controller.green_led}"

    def __repr__(self) -> str:
        return "WaterAlarmAssembly()"


def _led_state(led: LED) -> str:
    return 'on' if led.lit else 'off' if led.lit is False else '?'


def _main() -> None:
    VCC, GND = 5.0, 0.0
    asm = WaterAlarmAssembly()

    # Per-board BOM listing — the scenario runner only prints the
    # composite's direct children, which are the two boards.  For a
    # split assembly the part-level BOM is more useful printed per
    # board, so we do that explicitly here.
    from framework.refdes import RefdesBearing
    print("Bill of materials (per board):")
    for board in (asm.sensor, asm.controller):
        print(f"  {board.refdes} ({board.name}, rev {board.revision}):")
        for fn in board._factor_nodes:
            if isinstance(fn, RefdesBearing):
                print(f"    {fn.refdes:5s} {type(fn).__name__}")
    print()

    run_scenarios(
        asm,
        scenarios=[
            ("initial — tank empty",                  (GND, GND)),
            ("water touches low probe (held set)",    (VCC, GND)),
            ("water reaches high probe (reset)",      (VCC, VCC)),
            ("water recedes below high (held clr)",   (VCC, GND)),
            ("water gone again (set)",                (GND, GND)),
        ],
        bom=False,   # printed above per-board
        columns=[
            ("low",   lambda c, a, k: f"{a[0]:.1f}"),
            ("high",  lambda c, a, k: f"{a[1]:.1f}"),
            ("red",   lambda c, a, k: _led_state(c.controller.red_led)),
            ("green", lambda c, a, k: _led_state(c.controller.green_led)),
            ("alarm", lambda c, a, k: c.controller.red_led.lit),
        ],
    )


if __name__ == '__main__':
    _main()
