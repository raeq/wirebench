from framework.circuit import Circuit
from framework.wire import wire
from components.parts.uln2003a import ULN2003A
from components.parts.sn74hc04 import SN74HC04
from components.parts.cd4043 import CD4043
from components.passives.led import LED
from framework.rail import Rail


class WaterAlarm(Circuit):
    """Water level alarm.

    Two probes are mounted in the tank at the minimum and maximum water levels.
    Drive each probe with Vcc (≥ 1V) when submerged, 0 V when dry.

    ULN2003A output is open-collector: HIGH when transistor off (probe dry),
    LOW when transistor conducting (probe submerged).

    Wiring:
      low_probe  → ULN2003A ch1                   → CD4043 S  (HIGH=dry → set alarm)
      high_probe → ULN2003A ch2 → SN74HC04 gate 1 → CD4043 R  (LOW=wet → inverted → reset)
      CD4043 Q   → red LED   (alarm active)
      CD4043 /Q  → green LED (alarm clear)

    The SN74HC04 is a 14-pin hex inverter (6 gates); only gate 1 is used here.
    The remaining five gates (a_2/y_2 – a_6/y_6) are available for other signals.
    Leave unused inputs tied to GND or Vcc — never leave them floating.
    """

    __slots__ = ['_red_led', '_green_led']

    def __init__(self) -> None:
        sensor    = ULN2003A()
        inv       = SN74HC04()
        latch     = CD4043()
        red_led   = LED('red')
        green_led = LED('green')
        gnd       = Rail(False)   # GND tie for the five unused inverter gates

        wire(sensor.ports['out_1'], latch.ports['s_1'])
        wire(sensor.ports['out_2'], inv.ports['a_1'])
        wire(inv.ports['y_1'],      latch.ports['r_1'])
        wire(latch.ports['q_1'],    red_led.ports['anode'])
        wire(latch.ports['q_1_bar'], green_led.ports['anode'])
        # CMOS inputs must never float — tie unused inverter inputs LOW
        # and unused latch S/R inputs LOW (so those latches sit in 'hold').
        wire(gnd.ports['out'],
             inv.ports['a_2'], inv.ports['a_3'], inv.ports['a_4'],
             inv.ports['a_5'], inv.ports['a_6'],
             latch.ports['s_2'], latch.ports['r_2'],
             latch.ports['s_3'], latch.ports['r_3'],
             latch.ports['s_4'], latch.ports['r_4'])

        super().__init__(
            factor_nodes=[sensor, inv, latch, red_led, green_led, gnd],
            ports={'low_probe':  sensor.ports['in_1'],
                   'high_probe': sensor.ports['in_2'],
                   'state':      latch.ports['q_1']},
        )

        self._red_led   = red_led
        self._green_led = green_led

    def __call__(self, low_probe, high_probe) -> bool | None:
        self._ports['low_probe'].drive(low_probe)
        self._ports['high_probe'].drive(high_probe)
        self.evaluate()
        return self._ports['state'].value

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
