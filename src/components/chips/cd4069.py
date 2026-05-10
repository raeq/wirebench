from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from .concepts.inverter import Inverter


class CD4069(Chip):
    """Texas Instruments CD4069UB — hex unbuffered inverter.

    Pins (Vcc/GND not modelled):
        a_1 .. a_6 — gate inputs
        y_1 .. y_6 — gate outputs (y_i = NOT(a_i))

    Internally the chip composes six private Inverter cells.

    Supply voltage: 3 V – 18 V.  Propagation delay: ~30 ns at 5 V.

    The 'UB' suffix means unbuffered — one inversion stage per gate,
    not three.  This makes each gate usable as a linear amplifier or
    oscillator element when biased in the transition region, unlike the
    SN74HC04 which is hard-switched.  The cell-level Inverter does not
    model that distinction; for pure logic inversion the two chips are
    equivalent.

    Unused CMOS inputs must always be tied to GND or Vcc in real
    circuits — never left floating.
    """

    __slots__ = ('_gates',)

    CHANNELS: int = 6

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._gates = tuple(Inverter(domain) for _ in range(self.CHANNELS))

        a_pins, y_pins = [], []
        for i in range(1, self.CHANNELS + 1):
            a_pins.append(Pin(f'a_{i}', Direction.IN,  domain, mandatory=False, signal_type=Digital))
            y_pins.append(Pin(f'y_{i}', Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, gate in enumerate(self._gates):
            wire(a_pins[i].internal, gate.ports['a'])
            wire(gate.ports['y'],    y_pins[i].internal)

        super().__init__(pins=a_pins + y_pins, cells=list(self._gates))

    def __call__(
        self,
        a_1: bool = False, a_2: bool = False, a_3: bool = False,
        a_4: bool = False, a_5: bool = False, a_6: bool = False,
    ) -> tuple:
        self._assert_no_inputs_wired()
        for i, v in enumerate((a_1, a_2, a_3, a_4, a_5, a_6), start=1):
            self._ports[f'a_{i}'].drive(v)
        self.evaluate()
        return tuple(self._ports[f'y_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._ports[f"y_{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        ys = tuple(self._ports[f'y_{i+1}'].value for i in range(self.CHANNELS))
        return f"CD4069(y={ys})"
