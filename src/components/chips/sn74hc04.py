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
from .concepts.inverter import Inverter


@register('SN74HC04')
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

    __slots__ = ('_gates', '_refdes_number')

    CHANNELS: int = 6
    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-14_W7.62mm"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Jumper every unused input to Vcc or ground.** This is a "
        "CMOS family chip just like the 4xxx parts; floating inputs "
        "misbehave the same way (random oscillation, extra supply "
        "current, hand-wave-sensitive behaviour). If you only use one "
        "of the six inverters, ground the other five inputs.",
        "**Put a 100 nF decoupling capacitor right at the supply pin.** "
        "From pin 14 (Vcc) to pin 7 (GND), with the cap's leads under "
        "5 mm long — close enough that you'd call it 'touching the "
        "chip'. This is the most-skipped step in CMOS hobby work, and "
        "the most common cause of 'sometimes it works, sometimes it "
        "doesn't' bugs. The chip's switching currents create supply "
        "ringing inside the package itself; the cap has to be "
        "millimetres away to suppress it. A cap on the other side of "
        "the breadboard does nothing.",
        "**Don't drive 5 V logic with a 3.3 V signal — at least not "
        "this family.** The HC variant has CMOS-style input thresholds "
        "(around half the supply, so ~2.5 V on a 5 V rail). A 3.3 V "
        "HIGH from an ESP32 or RPi might or might not register as HIGH "
        "depending on temperature and chip tolerance. Use a 74HCT04 "
        "instead (TTL-style ~1.4 V threshold, recognises 3.3 V cleanly) "
        "or insert a level-shifter chip between the two voltage domains.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._gates = tuple(Inverter(domain) for _ in range(self.CHANNELS))

        # 14-pin DIP datasheet pinout: pins 7 (GND) and 14 (VCC) modelled
        # as Analog supply pins so the assembly-guide ERC can verify
        # they're wired.  No cell consumes them — the gates are powered
        # implicitly by the framework's voltage-only graph.
        a_pin_numbers = (1, 3, 5, 9, 11, 13)
        y_pin_numbers = (2, 4, 6, 8, 10, 12)
        a_pins, y_pins = [], []
        for i in range(self.CHANNELS):
            a_pins.append(Pin(PinId(a_pin_numbers[i], f'a_{i+1}'),
                              Direction.IN,  domain, mandatory=False, signal_type=Digital))
            y_pins.append(Pin(PinId(y_pin_numbers[i], f'y_{i+1}'),
                              Direction.OUT, domain, mandatory=False, signal_type=Digital))
        gnd_pin = Pin(PinId(7,  'GND'), Direction.IN, domain,
                      mandatory=False, signal_type=Analog)
        vcc_pin = Pin(PinId(14, 'VCC'), Direction.IN, domain,
                      mandatory=False, signal_type=Analog)

        for i, gate in enumerate(self._gates):
            wire(a_pins[i].internal, gate.ports['a'])
            wire(gate.ports['y'],    y_pins[i].internal)

        super().__init__(
            pins=a_pins + y_pins + [gnd_pin, vcc_pin],
            cells=list(self._gates),
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
        a_1: bool | None = False, a_2: bool | None = False, a_3: bool | None = False,
        a_4: bool | None = False, a_5: bool | None = False, a_6: bool | None = False,
    ) -> tuple[bool | None, ...]:
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
        return f"SN74HC04(y={ys}, refdes={self.refdes!r})"
