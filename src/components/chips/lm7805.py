from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('LM7805')
class LM7805(Chip):
    """Texas Instruments LM7805 — fixed +5V positive linear regulator (TO-220).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Put a capacitor on each side of the regulator, close to its "
        "pins.** A 0.33 µF capacitor from input (pin 1) to ground, and "
        "a 0.1 µF from output (pin 3) to ground, with the leads under "
        "5 mm long. Skip these and the 7805 misbehaves — it can "
        "oscillate (audible whine, ringing on a scope) or overshoot "
        "when the load changes suddenly. This step seems optional but "
        "isn't.",
        "**Feed the input at least 7 V — anything lower and the output "
        "drops with it.** The 7805 needs about 2 V of headroom between "
        "input and output to hold regulation. A 9 V battery slowly "
        "sagging under load eventually crosses that line and the "
        "regulator's output sags too. For battery-powered work, use "
        "an LDO regulator (LP2950, AMS1117-5.0) — they only need a few "
        "hundred millivolts of headroom.",
        "**Add a heatsink whenever the load draws more than ~250 mA.** "
        "Whatever voltage the regulator is dropping (input minus 5 V) "
        "becomes heat — a 12 V input dropping to 5 V at 500 mA "
        "dissipates 3.5 W, enough to thermal-shutdown the chip in "
        "seconds without a heatsink. If the heat is more than a "
        "watt or two, switch to a switching regulator instead.",
        "**The TO-220's metal tab is internally tied to ground** "
        "(pin 2). That makes mounting easy — you can bolt it straight "
        "to a grounded heatsink without an insulator. The flip side: "
        "the tab and pin 2 are the same node, so don't mount the tab "
        "to anything that isn't at ground potential.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'INPUT',  Direction.IN,  Analog),
        (2, 'GND',    Direction.IN,  Analog),
        (3, 'OUTPUT', Direction.OUT, Analog),
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
        return f"LM7805(refdes={self.refdes!r})"
