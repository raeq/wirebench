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
        "**Vout = 1.25 V × (1 + R2/R1) + I_ADJ × R2.** R1 is the upper "
        "leg (ADJ to OUT, typically 240 Ω); R2 is the lower leg (ADJ to "
        "GND). The fixed 1.25 V reference appears between OUT and ADJ — "
        "swapping R1 and R2 inverts the relationship.",
        "**Minimum load ~10 mA.** Below that the regulator loses "
        "regulation and Vout climbs. The R1 / R2 divider itself usually "
        "provides this — sizing R1 = 240 Ω puts about 5 mA through the "
        "divider, and any real load adds to it.",
        "**ADJ pin is high-impedance and noisy.** A 10 µF cap from ADJ "
        "to ground dramatically improves ripple rejection (the datasheet's "
        "famous trick). Without it the LM317 passes most of the input "
        "ripple straight through, especially at light loads.",
        "**Protection diodes against capacitor discharge.** If you have "
        "a big output cap (>25 µF) and a separate ADJ bypass cap, add a "
        "1N4001 from OUT→IN (cathode to IN) and another from OUT→ADJ "
        "(cathode to ADJ). On a power-off short the caps can dump current "
        "back through the regulator and crack the die.",
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
