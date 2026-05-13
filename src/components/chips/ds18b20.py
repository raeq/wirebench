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
        "**4.7 kΩ pull-up on the DQ line is mandatory.** 1-Wire is "
        "open-drain — the line idles HIGH and devices pull it LOW to "
        "communicate. Without the pull-up the line floats; with too "
        "weak a pull-up (>10 kΩ on long cables), the rise time exceeds "
        "the protocol window and the host sees garbled bits.",
        "**Parasitic power needs a strong pull-up.** When VDD is tied "
        "to GND and the chip draws power from the DQ line during "
        "conversions, the host must drive DQ HIGH actively (not "
        "through the pull-up) for the conversion duration — pulling "
        "DQ low instead during a parasitic conversion stalls the "
        "measurement and returns 85°C (the reset value).",
        "**TO-92 pinout, flat side facing you, leads down: GND-DQ-VDD.** "
        "The package matches the BC547 outline exactly — swapping a "
        "DS18B20 for a BC547 in a hurry is a real possibility, and "
        "neither part survives the experience.",
        "**Each chip has a unique 64-bit ROM ID** — wiring multiple "
        "sensors on one DQ line requires enumerating them with SEARCH "
        "ROM and storing the IDs. Replacing a sensor changes the ID; "
        "code that hard-codes a single sensor's ID quietly stops "
        "responding when you swap it out.",
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
