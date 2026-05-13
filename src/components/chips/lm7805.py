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
        "**Input and output bypass capacitors are mandatory.** The "
        "datasheet calls for 0.33 µF on the input and 0.1 µF on the "
        "output, close to the pins. Without them the regulator oscillates "
        "(audible whine, ringing on a scope) and over-shoots on load "
        "transients.",
        "**Minimum dropout ~2 V.** The 7805 needs V_in ≥ ~7 V to hold "
        "5 V on its output under load. A battery sagging from 9 V to "
        "6 V at high current crosses the dropout threshold and the "
        "output goes with it — use an LDO (LP2950, AMS1117-5.0) for "
        "battery-powered designs.",
        "**TO-220 tab is internally connected to ground** (pin 2). It "
        "can be bolted to a grounded heatsink without insulation — "
        "convenient. But the tab and pin 2 share connection on the "
        "PCB / breadboard, so don't mount the tab to anything *not* at "
        "ground potential.",
        "**Heatsink it above ~250 mA load.** Power dissipated is "
        "(V_in − 5 V) × I_out; a 12 V → 5 V drop at 500 mA dissipates "
        "3.5 W and the package thermal-shuts-down in seconds without a "
        "heatsink. A switching regulator is a better choice for >1 W "
        "drops.",
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
