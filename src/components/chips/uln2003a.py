from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.drive_type import DriveType
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
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-16_W7.62mm"
    # Every output is an open-collector Darlington — the chip sinks
    # LOW when the channel's input is high and floats high-impedance
    # otherwise.  External pull-up to the load supply required
    # (datasheet figure 2; the docstring + GOTCHAS above already
    # call this out as the canonical user mistake).
    PIN_DRIVE_TYPES: ClassVar[dict[str, "DriveType"]] = {
        f'out_{i}': DriveType.OPEN_COLLECTOR for i in range(1, 8)
    }

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Wire your load between the + rail and the output pin — not "
        "between the output pin and ground.** The ULN2003A *sinks* "
        "current to ground; it doesn't *source* current from a rail. "
        "Put your relay / motor / coil with one end on V+, the other "
        "end on the chip's output, and the chip pulls the output LOW to "
        "energise the load. Wiring it the way you'd wire a transistor "
        "to drive HIGH is the most common 'why is nothing happening?' "
        "mistake with this part.",
        "**Pin 9 (COMMON) goes to the load supply, not to logic Vcc.** "
        "If you're driving 12 V relays, pin 9 connects to the 12 V "
        "rail. The chip has built-in freewheel diodes (the things "
        "that catch the voltage spike when a relay turns off) and "
        "pin 9 is where their cathodes meet. Without pin 9 tied to "
        "the load supply, every switch-off pulse punches straight "
        "through the chip and eventually kills a channel.",
        "**Keep the ground wire from pin 8 short.** With seven channels "
        "each sinking up to 500 mA at once, this one ground pin can "
        "carry several amps in a tight switching loop. A long ground "
        "wire on a breadboard introduces enough inductance that the "
        "chip's internal reference shifts relative to system ground, "
        "and channels can start switching when you didn't ask them to. "
        "Run pin 8's wire directly to the rail, no detours.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._channels = tuple(DarlingtonChannel(domain) for _ in range(self.CHANNELS))

        # 16-pin DIP datasheet pinout: pin 8 (GND) modelled as an
        # Analog ground pin so the assembly-guide ERC catches forgetting
        # to wire it.  Pin 9 (COM) — the inductive-load freewheel
        # return — is omitted: it's not a power / ground pin and is
        # only used when driving inductive loads, so leaving it
        # unwired is legitimate for resistive-load builds.  Inputs
        # in_1..in_7 are pins 1..7; outputs are reverse-numbered for
        # routing convenience: out_i is at pin (17 - i), so out_1=16,
        # out_2=15, ..., out_7=10.
        in_pins, out_pins = [], []
        for i in range(1, self.CHANNELS + 1):
            in_pins .append(Pin(PinId(i, f'in_{i}'),
                                Direction.IN,  domain, mandatory=False, signal_type=Analog))
            out_pins.append(Pin(PinId(17 - i, f'out_{i}'),
                                Direction.OUT, domain, mandatory=False, signal_type=Digital))
        gnd_pin = Pin(PinId(8, 'GND'), Direction.IN, domain,
                      mandatory=False, signal_type=Analog)

        for i, channel in enumerate(self._channels):
            wire(in_pins[i].internal,  channel.ports['b'])
            wire(channel.ports['out'], out_pins[i].internal)

        super().__init__(
            pins=in_pins + out_pins + [gnd_pin],
            cells=list(self._channels),
        )

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
