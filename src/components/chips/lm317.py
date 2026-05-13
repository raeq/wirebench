from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('LM317')
class LM317(Chip):
    """Texas Instruments LM317 — adjustable +1.25V to +37V positive regulator (TO-220).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The LM317 sets its output voltage from two resistors — R1 "
        "(OUT to ADJ) and R2 (ADJ to GND).** The math: output voltage "
        "= 1.25 × (1 + R2/R1). A typical pair is R1 = 240 Ω plus "
        "R2 chosen for the voltage you want — e.g. R2 = 720 Ω gives "
        "5 V output. Swap R1 and R2 around and the equation inverts; "
        "the regulator either tries to output less than its minimum "
        "or much more than the input can supply.",
        "**Always have at least ~10 mA flowing through the output — "
        "even at no load.** Below that current, the LM317 loses "
        "regulation and the output drifts upward. The R1/R2 divider "
        "you already need (sized around 240 Ω for R1) bleeds ~5 mA, "
        "and any actual load adds to that, so this usually takes "
        "care of itself.",
        "**Add a 10 µF capacitor from the ADJ pin (pin 1) to ground.** "
        "Without it, most of the supply's ripple comes straight through "
        "to the output — especially at low loads. The cap shunts the "
        "ripple to ground at the ADJ pin instead. This one-cap fix is "
        "famous enough that the datasheet calls it out explicitly.",
        "**If you have both a big output cap (>25 µF) *and* the ADJ "
        "bypass cap above, add two protection diodes.** When the supply "
        "shorts out at power-off, the caps can dump current back "
        "through the regulator and crack the chip. A 1N4001 from OUT "
        "to IN with the band pointing at IN, and another from OUT to "
        "ADJ with the band pointing at ADJ, gives the dump current "
        "somewhere to go.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'ADJ',    Direction.IN,  Analog),
        (2, 'OUTPUT', Direction.OUT, Analog),
        (3, 'INPUT',  Direction.IN,  Analog),
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
        super().__init__(pins=pins, cells=[])

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
        return f"LM317(refdes={self.refdes!r})"
