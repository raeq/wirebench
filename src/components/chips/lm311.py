from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.wire import wire
from .concepts.opamp import OpAmp


@register('LM311')
class LM311(Chip):
    """Texas Instruments LM311 — single high-speed open-collector comparator
    with strobe and balance (PDIP-8).

    Composes two private `OpAmp` cells — one each for COL_OUT and
    EMIT_OUT — because the LM311's output is an internal NPN
    transistor whose *collector* and *emitter* are both brought out
    to package pins.  In real silicon the two are linked by the
    transistor; in the framework each pin has its own driver from a
    cell observing the same comparator inputs.  The cells produce
    rail-to-rail drive for topology purposes; add a pull-up resistor
    at the bench for the actual open-collector behaviour.
    """

    __slots__ = ('_refdes_number', '_cell_col', '_cell_emit')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-8_W7.62mm"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Wire a pull-up resistor on the output — same as the LM393.** "
        "The LM311 can only pull its output LOW; without a pull-up "
        "(~10 kΩ to wherever you want HIGH to live), the output node "
        "floats when the comparator wants to drive HIGH and the "
        "circuit appears dead. The LM311 has an extra trick the LM393 "
        "doesn't: the emitter (pin 1) is brought out separately, so "
        "you can pull the output up to *any* supply rail — handy for "
        "driving an optoisolator or a different logic family.",
        "**Tie pin 6 (Strobe) to V+ for normal operation.** Strobe is "
        "an active-LOW disable: pull it LOW and the output is forced "
        "off regardless of what the inputs are doing. Most LM311 "
        "variants are 'active' (responding to inputs) when strobe "
        "floats, but check the datasheet for your specific part — a "
        "few behave the other way around, and a floating pin can give "
        "you mystery comparator failures.",
        "**Add a 1 MΩ resistor from the output back to the + input to "
        "stop chatter at the threshold.** With no feedback, tiny input "
        "noise causes the output to flicker rapidly between HIGH and "
        "LOW. The 1 MΩ resistor creates a small amount of hysteresis "
        "(~50 mV) that ignores noise without significantly shifting "
        "the switching threshold. Same fix as on the LM393.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'EMIT_OUT', Direction.OUT, Analog),
        (2, 'IN_POS',      Direction.IN,  Analog),
        (3, 'IN_NEG',      Direction.IN,  Analog),
        (4, 'VCC_NEG',     Direction.IN,  Analog),
        (5, 'BALANCE',  Direction.IN,  Analog),
        (6, 'BAL_STRB', Direction.IN,  Analog),
        (7, 'COL_OUT',  Direction.OUT, Analog),
        (8, 'VCC_POS',     Direction.IN,  Analog),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        self._cell_col  = OpAmp(domain)
        self._cell_emit = OpAmp(domain)
        by_name = {pin.id.name: pin for pin in pins}
        # Both cells share the same inputs and supply; each drives its
        # own output pin.
        wire(by_name['IN_POS'].internal,
             self._cell_col.ports['v_in_pos'],
             self._cell_emit.ports['v_in_pos'])
        wire(by_name['IN_NEG'].internal,
             self._cell_col.ports['v_in_neg'],
             self._cell_emit.ports['v_in_neg'])
        wire(by_name['VCC_POS'].internal,
             self._cell_col.ports['v_supply'],
             self._cell_emit.ports['v_supply'])
        wire(by_name['VCC_NEG'].internal,
             self._cell_col.ports['v_gnd'],
             self._cell_emit.ports['v_gnd'])
        wire(self._cell_col.ports['out'],  by_name['COL_OUT'].internal)
        wire(self._cell_emit.ports['out'], by_name['EMIT_OUT'].internal)
        super().__init__(pins=pins, cells=[self._cell_col, self._cell_emit])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        """Black-box package — no behavioural model. Pin states are
        observable via `chip.ports['<name>'].value`. For analog or
        timing-accurate behaviour, simulate the .SUBCKT in SPICE."""
        return None

    def __repr__(self) -> str:
        return f"LM311(refdes={self.refdes!r})"
