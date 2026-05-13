from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('DS18B20')
class DS18B20(Chip):
    """Analog Devices (Maxim) DS18B20 — 1-Wire programmable digital
    thermometer (TO-92, 3-pin).

    Black-box package model: pins follow the datasheet pinout verbatim;
    no internal cells are instantiated. For behavioural simulation, use
    the .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. DQ requires a 4.7 kΩ pull-up to VDD.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Wire a 4.7 kΩ resistor from DQ to + supply — every time, "
        "no exceptions.** The 1-Wire bus is open-drain (the chip can "
        "only pull the line LOW), so the pull-up is what makes the "
        "line HIGH at rest. Without it the line floats and no "
        "communication happens at all. (Detail: weaker pull-ups, like "
        "10 kΩ on a long cable, slow the rise time enough that the "
        "host sees garbled bits.)",
        "**Hold the DS18B20 with the flat side facing you, leads "
        "pointing down — the pins are GND, DQ, VDD from left to "
        "right.** The package is the same TO-92 outline as a BC547 "
        "transistor; swapping one for the other by accident is "
        "easy and neither part survives the mistake. The two parts "
        "live in different bins.",
        "**Each DS18B20 has a unique serial number burned into it at "
        "the factory.** If you wire several sensors on the same data "
        "line, your code needs to enumerate them at startup (SEARCH "
        "ROM command) and remember which is which. Hard-coding a "
        "specific sensor's ID into your code means a replacement "
        "sensor — same model, same wiring — silently stops working "
        "because its ID is different.",
        "**Parasitic power mode (Vdd tied to GND) needs a strong "
        "active pull-up, not just the resistor.** In parasitic mode "
        "the chip steals power from the DQ line during conversions, "
        "and the host must drive DQ HIGH directly (a transistor or "
        "MOSFET push-pull) for the duration. If the line falls LOW "
        "during a parasitic conversion, the chip stalls and returns "
        "85°C (the reset value) instead of a real reading.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'GND', Direction.IN,    Analog),
        (2, 'DQ',  Direction.BIDIR, Digital),
        (3, 'VDD', Direction.IN,    Analog),
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
        return f"DS18B20(refdes={self.refdes!r})"
