from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire
from .concepts.inverter import Inverter


class SN74HC04(Chip):
    """Texas Instruments SN74HC04 — hex inverting buffer.

    Pins (Vcc/GND not modelled):
        a_1 .. a_6 — gate inputs
        y_1 .. y_6 — gate outputs (y_i = NOT(a_i))

    Internally the chip composes six private Inverter cells.

    Supply voltage: 2 V – 6 V.  Typical propagation delay: 7 ns at 5 V.
    The SN74HC04 is buffered (three inversion stages internally per gate),
    so it is a hard-switched logic part — unlike the CD4069UB, which is
    unbuffered and usable in linear/oscillator modes.  The cell-level
    Inverter does not model that distinction; it is a chip-level
    annotation only.

    Unused CMOS inputs must always be tied to GND or Vcc in real
    circuits — never left floating.
    """

    __slots__ = ['_gates']

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

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"SN74HC04 has {self.CHANNELS} channels; got {len(inputs)} inputs")
        self._assert_no_inputs_wired()
        for i in range(self.CHANNELS):
            v = inputs[i] if i < len(inputs) else False
            self._ports[f'a_{i+1}'].drive(v)
        self.evaluate()
        return tuple(self._ports[f'y_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._ports[f"y_{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        return 'SN74HC04()'
