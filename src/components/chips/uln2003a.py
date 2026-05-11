from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog, Digital
from framework.wire import wire
from framework.registry import register
from .concepts.darlington_channel import DarlingtonChannel


@register('ULN2003A')
class ULN2003A(Chip):
    """Seven-channel NPN Darlington transistor array (TI ULN2003A).

    The chip's external surface is its 14 signal pins (Vcc/COM/GND not
    modelled):
        in_1  .. in_7  — channel inputs (analog voltage)
        out_1 .. out_7 — channel outputs (digital, open-collector)

    Each pin is a `Pin` — a bonded-wire relay between the package and
    the silicon.  Internally the chip composes seven private
    DarlingtonChannel cells.

    Channel behaviour:
      input ≤ V_THRESHOLD → transistor off → pin pulled HIGH by pull-up
      input  > V_THRESHOLD → transistor on  → pin sunk LOW (open-collector)

    Real-world notes
    ----------------
    V_CE_SAT ≈ 0.9 V: a "LOW" output is not a clean 0 V — it sits near
    0.9 V.  Account for that when sizing load resistors or checking
    logic-level compatibility of downstream inputs.

    I_OUT_MAX = 500 mA per channel.  Each channel needs a pull-up to
    Vcc on the COM pin; omitting it leaves the output floating when the
    transistor is off.
    """

    __slots__ = ('_channels', '_refdes_number')

    CHANNELS:    int   = 7
    V_THRESHOLD: float = DarlingtonChannel.V_THRESHOLD   # mirror of cell's threshold
    I_OUT_MAX:   float = 0.500   # A — maximum sink current per channel
    REFDES_PREFIX: ClassVar[str] = 'U'

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._channels = tuple(DarlingtonChannel(domain) for _ in range(self.CHANNELS))

        # 16-pin DIP datasheet pinout: pin 8 (GND) and pin 9 (COM)
        # omitted. Inputs in_1..in_7 are pins 1..7; outputs are reverse-
        # numbered for routing convenience: out_i is at pin (17 - i),
        # so out_1=16, out_2=15, ..., out_7=10.
        in_pins, out_pins = [], []
        for i in range(1, self.CHANNELS + 1):
            in_pins .append(Pin(PinId(i, f'in_{i}'),
                                Direction.IN,  domain, mandatory=False, signal_type=Analog))
            out_pins.append(Pin(PinId(17 - i, f'out_{i}'),
                                Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, channel in enumerate(self._channels):
            wire(in_pins[i].internal,  channel.ports['b'])
            wire(channel.ports['out'], out_pins[i].internal)

        super().__init__(pins=in_pins + out_pins, cells=list(self._channels))

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        in_1: float | None = 0.0, in_2: float | None = 0.0, in_3: float | None = 0.0,
        in_4: float | None = 0.0, in_5: float | None = 0.0, in_6: float | None = 0.0,
        in_7: float | None = 0.0,
    ) -> tuple[bool | None, ...]:
        self._assert_no_inputs_wired()
        for i, v in enumerate((in_1, in_2, in_3, in_4, in_5, in_6, in_7), start=1):
            self._ports[f'in_{i}'].drive(v)
        self.evaluate()
        return tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))

    @property
    def output_levels(self) -> tuple[bool | None, ...]:
        """Output pin values as a tuple: True = HIGH, False = LOW, None = undriven."""
        return tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'CH{i+1}:{"HIGH" if self._ports[f"out_{i+1}"].value else "LOW"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        outs = tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))
        return f"ULN2003A(out={outs}, refdes={self.refdes!r})"
