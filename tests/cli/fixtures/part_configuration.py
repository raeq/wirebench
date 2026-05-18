"""A Chip with an OUT pin but no behavioural cell driving it →
PartConfigurationError at chip construction time."""
from typing import ClassVar

from components.chips.concepts.inverter import Inverter
from framework import Circuit
from framework.chip import Chip
from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.signals import Analog, Digital
from framework.wire import wire


class PartiallyDriven(Chip):
    """Declares two OUT pins; only one is driven by an internal cell."""

    __slots__ = ('_refdes_number', '_gate')
    REFDES_PREFIX: ClassVar[str] = 'U'

    def __init__(self, *, refdes_number: int = 1) -> None:
        self._refdes_number = refdes_number
        self._gate = Inverter(ELECTRICAL)
        a1 = Pin(PinId(1, 'a_1'), Direction.IN, ELECTRICAL,
                 mandatory=False, signal_type=Digital)
        y1 = Pin(PinId(2, 'y_1'), Direction.OUT, ELECTRICAL,
                 mandatory=False, signal_type=Digital)
        # y_2 is OUT but undriven — triggers PartConfigurationError.
        y2 = Pin(PinId(3, 'y_2'), Direction.OUT, ELECTRICAL,
                 mandatory=False, signal_type=Digital)
        gnd = Pin(PinId(4, 'GND'), Direction.IN, ELECTRICAL,
                  mandatory=False, signal_type=Analog)
        vcc = Pin(PinId(5, 'VCC'), Direction.IN, ELECTRICAL,
                  mandatory=False, signal_type=Analog)
        wire(a1.internal, self._gate.ports['a'])
        wire(self._gate.ports['y'], y1.internal)
        super().__init__(pins=[a1, y1, y2, gnd, vcc], cells=[self._gate])

    def __call__(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError


class BrokenDesign(Circuit):
    def __init__(self) -> None:
        self.u1 = PartiallyDriven(refdes_number=1)
        super().__init__()
