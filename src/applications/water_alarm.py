from framework.circuit import Circuit
from framework.wire import wire
from components.uln2003a import ULN2003A
from components.sn74hc04 import SN74HC04
from components.cd4043 import CD4043
from components.led import LED
from components.rail import Rail


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

        wire(sensor.ports['out_1'], latch.ports['s'])
        wire(sensor.ports['out_2'], inv.ports['a_1'])
        wire(inv.ports['y_1'],      latch.ports['r'])
        wire(latch.ports['q'],      red_led.ports['anode'])
        wire(latch.ports['q_bar'],  green_led.ports['anode'])
        # CMOS inputs must never float — tie the unused inverter inputs LOW.
        wire(gnd.ports['out'],
             inv.ports['a_2'], inv.ports['a_3'], inv.ports['a_4'],
             inv.ports['a_5'], inv.ports['a_6'])

        super().__init__(
            factor_nodes=[sensor, inv, latch, red_led, green_led, gnd],
            inputs={'low_probe':  sensor.ports['in_1'],
                    'high_probe': sensor.ports['in_2']},
            outputs={'state': latch.ports['q']},
        )

        self._red_led   = red_led
        self._green_led = green_led

    def __call__(self, low_probe_v, high_probe_v) -> bool | None:
        self._inputs['low_probe'].drive(low_probe_v)
        self._inputs['high_probe'].drive(high_probe_v)
        self._evaluate()
        return self._outputs['state'].value

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
