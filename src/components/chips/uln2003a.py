from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.darlington_channel import DarlingtonChannel


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

    __slots__ = ('_channels',)

    CHANNELS:    int   = 7
    V_THRESHOLD: float = DarlingtonChannel.V_THRESHOLD   # mirror of cell's threshold
    I_OUT_MAX:   float = 0.500   # A — maximum sink current per channel

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._channels = tuple(DarlingtonChannel(domain) for _ in range(self.CHANNELS))

        in_pins, out_pins = [], []
        for i in range(1, self.CHANNELS + 1):
            in_pins .append(Pin(f'in_{i}',  Direction.IN,  domain, mandatory=False, signal_type=Analog))
            out_pins.append(Pin(f'out_{i}', Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, channel in enumerate(self._channels):
            wire(in_pins[i].internal,  channel.ports['b'])
            wire(channel.ports['out'], out_pins[i].internal)

        super().__init__(pins=in_pins + out_pins, cells=list(self._channels))

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"ULN2003A has {self.CHANNELS} channels; got {len(inputs)} inputs")
        self._assert_no_inputs_wired()
        for i in range(self.CHANNELS):
            v = inputs[i] if i < len(inputs) else 0.0
            self._ports[f'in_{i+1}'].drive(v)
        self.evaluate()
        return tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))

    @property
    def out(self) -> tuple:
        """Output pin values as a tuple: True = HIGH, False = LOW, None = undriven."""
        return tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'CH{i+1}:{"HIGH" if self._ports[f"out_{i+1}"].value else "LOW"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        outs = tuple(self._ports[f'out_{i+1}'].value for i in range(self.CHANNELS))
        return f'ULN2003A(out={outs})'
