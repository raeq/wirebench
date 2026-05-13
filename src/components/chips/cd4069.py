from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Digital
from framework.wire import wire
from framework.registry import register
from .concepts.inverter import Inverter


@register('CD4069')
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

    __slots__ = ('_gates', '_refdes_number')

    CHANNELS: int = 6
    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-14_W7.62mm"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Every input pin must connect somewhere — Vdd or ground, but "
        "never floating.** If you only use two of the six inverter "
        "gates, jumper the unused inputs straight to ground. A floating "
        "CMOS input misbehaves in odd ways: the chip can oscillate, "
        "draw extra supply current, and behave differently when you "
        "wave your hand near the board. (Technically the input "
        "high-impedance node drifts through the threshold; the output "
        "stage spends time in its linear region and radiates noise into "
        "the supply rail.)",
        "**This chip's gates make weak digital edges — that's by "
        "design.** The 'UB' in the part number means *unbuffered*: "
        "each gate is one transistor stage instead of three. If you "
        "need crisp digital outputs (a clock for another chip, a clean "
        "trigger), use a 74HC04 instead. The CD4069's weakness is "
        "actually its party trick — biased into the in-between region "
        "with feedback resistors, each gate becomes a small linear "
        "amplifier; that's how you build crystal oscillators and "
        "Schmitt-trigger-like circuits out of CMOS inverters.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *, refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._gates = tuple(Inverter(domain) for _ in range(self.CHANNELS))

        # 14-pin DIP datasheet pinout: pins 7 (VSS) and 14 (VDD) omitted.
        # Same physical layout as the SN74HC04.
        a_pin_numbers = (1, 3, 5, 9, 11, 13)
        y_pin_numbers = (2, 4, 6, 8, 10, 12)
        a_pins, y_pins = [], []
        for i in range(self.CHANNELS):
            a_pins.append(Pin(PinId(a_pin_numbers[i], f'a_{i+1}'),
                              Direction.IN,  domain, mandatory=False, signal_type=Digital))
            y_pins.append(Pin(PinId(y_pin_numbers[i], f'y_{i+1}'),
                              Direction.OUT, domain, mandatory=False, signal_type=Digital))

        for i, gate in enumerate(self._gates):
            wire(a_pins[i].internal, gate.ports['a'])
            wire(gate.ports['y'],    y_pins[i].internal)

        super().__init__(pins=a_pins + y_pins, cells=list(self._gates))

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
        return f"CD4069(y={ys}, refdes={self.refdes!r})"
