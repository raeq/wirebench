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

from framework.board import Board
from framework.circuit import Circuit
from framework.factor import FactorNode
from framework.mate import mate
from framework.port import Port
from framework.wire import wire
from components.chips.cd4043 import CD4043
from components.chips.cd4069 import CD4069
from components.chips.sn74hc04 import SN74HC04
from components.chips.uln2003a import ULN2003A
from components.connectors.headers import Header2xNFemale, Header2xNMale
from components.passives.led import LED
from components.passives.rail import Rail


class SensorBoard(Board):
    """Conditions raw probe voltages into clean logic-level signals
    suitable for transmission to the controller board over the GPIO
    header.
    """

    def __init__(self, *, refdes_number: int) -> None:
        sensor    = ULN2003A(refdes_number=1)
        connector = Header2xNFemale(pin_count=40, pitch_mm=2.54, refdes_number=1)

        # Probe inputs come in on the connector and go to the ULN2003A;
        # ULN2003A outputs (open-collector) go back out on the connector.
        wire(connector.pins[2].internal, sensor.ports['in_1'])   # J1.p3
        wire(connector.pins[3].internal, sensor.ports['in_2'])   # J1.p4
        wire(sensor.ports['out_1'], connector.pins[4].internal)  # J1.p5
        wire(sensor.ports['out_2'], connector.pins[5].internal)  # J1.p6

        super().__init__(
            name='Sensor Board',
            revision='A',
            components=[sensor, connector],
            refdes_number=refdes_number,
        )


class ControllerBoard(Board):
    """Reads conditioned sensor outputs over the GPIO header, drives
    the alarm latch and indicator LEDs."""

    __slots__ = ('_red_led', '_green_led')

    def __init__(self, *, refdes_number: int) -> None:
        sn74hc04  = SN74HC04(refdes_number=1)
        cd4069    = CD4069  (refdes_number=2)
        cd4043    = CD4043  (refdes_number=3)
        red_led   = LED('red',   refdes_number=1)
        green_led = LED('green', refdes_number=2)
        gnd       = Rail(False)
        vcc       = Rail(True)
        connector = Header2xNMale(pin_count=40, pitch_mm=2.54, refdes_number=1)

        # Sensor outputs arrive on P1.p5 (conditioned low_probe) and
        # P1.p6 (conditioned high_probe).
        wire(connector.pins[4].internal, cd4043.ports['s_1'])         # P1.p5
        wire(connector.pins[5].internal, sn74hc04.ports['a_1'])       # P1.p6
        wire(sn74hc04.ports['y_1'],      cd4043.ports['r_1'])

        # Q drives red LED directly; /Q derived from Q via CD4069 gate 1.
        wire(cd4043.ports['q_1'],   red_led.ports['anode'])
        wire(cd4043.ports['q_1'],   cd4069.ports['a_1'])
        wire(cd4069.ports['y_1'],   green_led.ports['anode'])

        # CD4043 OE tied HIGH.
        wire(vcc.ports['out'], cd4043.ports['oe'])

        # Tie off all unused CMOS inputs and unused latch S/R inputs.
        wire(gnd.ports['out'],
             sn74hc04.ports['a_2'], sn74hc04.ports['a_3'], sn74hc04.ports['a_4'],
             sn74hc04.ports['a_5'], sn74hc04.ports['a_6'],
             cd4069.ports['a_2'], cd4069.ports['a_3'], cd4069.ports['a_4'],
             cd4069.ports['a_5'], cd4069.ports['a_6'],
             cd4043.ports['s_2'], cd4043.ports['r_2'],
             cd4043.ports['s_3'], cd4043.ports['r_3'],
             cd4043.ports['s_4'], cd4043.ports['r_4'])

        super().__init__(
            name='Controller Board',
            revision='A',
            components=[sn74hc04, cd4069, cd4043, red_led, green_led, gnd, vcc, connector],
            refdes_number=refdes_number,
        )
        self._red_led   = red_led
        self._green_led = green_led

    @property
    def red_led(self) -> LED:
        return self._red_led

    @property
    def green_led(self) -> LED:
        return self._green_led


class WaterAlarmAssembly(Circuit):
    """Stacked assembly: SensorBoard (A1) mated to ControllerBoard (A2)
    via a 40-pin GPIO header pair.  Surface inputs are the two probe
    voltages on the sensor board; the controller's LEDs are read via
    component handles."""

    __slots__ = ('_sensor', '_controller')

    def __init__(self) -> None:
        self._sensor     = SensorBoard    (refdes_number=1)
        self._controller = ControllerBoard(refdes_number=2)

        # Mate the only connector on each board.
        mate(self._sensor.connectors[0], self._controller.connectors[0])

        # Surface ports: drive the probes via the sensor's J1.p3 / J1.p4
        # (already qualified by the connector's refdes in the board's
        # _ports dict).
        ports: dict[str, Port] = {
            'low_probe':  self._sensor.ports['J1.p3'],
            'high_probe': self._sensor.ports['J1.p4'],
        }
        super().__init__(
            factor_nodes=[self._sensor, self._controller],
            ports=ports,
        )

    def __call__(self, low_probe: float, high_probe: float) -> bool | None:
        self._ports['low_probe'].drive(low_probe)
        self._ports['high_probe'].drive(high_probe)
        self.evaluate()
        # Latch state on the controller board.
        result: bool | None = self._controller.red_led.lit
        return result

    @property
    def sensor(self) -> SensorBoard:
        return self._sensor

    @property
    def controller(self) -> ControllerBoard:
        return self._controller

    def __str__(self) -> str:
        return f"{self._controller.red_led} | {self._controller.green_led}"

    def __repr__(self) -> str:
        return "WaterAlarmAssembly()"


def _main() -> None:
    VCC, GND = 5.0, 0.0
    asm = WaterAlarmAssembly()

    print("Bill of materials (per board):")
    for board in (asm.sensor, asm.controller):
        print(f"  {board.refdes} ({board.name}, rev {board.revision}):")
        from framework.refdes import RefdesBearing
        for fn in board._factor_nodes:
            if isinstance(fn, RefdesBearing):
                print(f"    {fn.refdes:5s} {type(fn).__name__}")
    print()

    scenarios = [
        ("initial — tank empty",                GND, GND),
        ("water touches low probe (held set)",  VCC, GND),
        ("water reaches high probe (reset)",    VCC, VCC),
        ("water recedes below high (held clr)", VCC, GND),
        ("water gone again (set)",              GND, GND),
    ]

    print(f'{"event":40s} | low | high | red | green | alarm')
    print('-' * 80)
    for label, low, high in scenarios:
        alarm = asm(low, high)
        red   = 'on ' if asm.controller.red_led.lit  else 'off' if asm.controller.red_led.lit  is False else ' ? '
        green = 'on ' if asm.controller.green_led.lit else 'off' if asm.controller.green_led.lit is False else ' ? '
        print(f'{label:40s} | {low:>3.1f} | {high:>4.1f} | {red} | {green}  | {alarm}')


if __name__ == '__main__':
    _main()
