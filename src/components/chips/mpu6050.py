from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital


@register('MPU6050')
class MPU6050(Chip):
    """InvenSense / TDK MPU-6050 — 6-axis MEMS IMU (QFN-24).

    Black-box package model: only the datasheet headline pins are
    instantiated; pins 2–5, 14–17, 19, 21, 22 are reserved/NC and
    omitted. No internal cells. For behavioural simulation, use the
    .SUBCKT placeholder in spice-models.lib or substitute a vendor
    model. 3.3 V part — do NOT drive directly from 5 V logic.
    """

    __slots__ = ('_refdes_number',)

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm"

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1,  'CLKIN',  Direction.IN,    Analog),
        (6,  'AUX_DA', Direction.BIDIR, Digital),
        (7,  'AUX_CL', Direction.OUT,   Digital),
        (8,  'VLOGIC', Direction.IN,    Analog),
        (9,  'AD0',    Direction.IN,    Digital),
        (10, 'REGOUT', Direction.OUT,   Analog),
        (11, 'FSYNC',  Direction.IN,    Analog),
        (12, 'INT',    Direction.OUT,   Digital),
        (13, 'VDD',    Direction.IN,    Analog),
        (18, 'GND',    Direction.IN,    Analog),
        (20, 'CPOUT',  Direction.OUT,   Analog),
        (23, 'SCL',    Direction.IN,    Digital),
        (24, 'SDA',    Direction.BIDIR, Digital),
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
        return f"MPU6050(refdes={self.refdes!r})"
