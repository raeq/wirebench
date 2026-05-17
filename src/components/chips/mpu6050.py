from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from framework.wire import wire
from .concepts.idle_driver import IdleDriver


@register('MPU6050')
class MPU6050(Chip):
    """InvenSense / TDK MPU-6050 — 6-axis MEMS IMU (QFN-24).

    The MPU-6050's behaviour is I²C-protocol-driven (host queries
    accelerometer / gyro registers over a bus), too complex to model
    behaviourally at the framework level.  Each declared OUT pin is
    backed by an `IdleDriver` cell so the topology validates;
    actual sensor readings come from a SPICE / cycle-accurate emulator
    when accuracy matters, or from Python-state prescription by the
    enclosing demo.  3.3 V part — do NOT drive directly from 5 V logic.
    """

    __slots__ = ('_refdes_number', '_drivers')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm"
    # I²C SDA — open-drain per protocol.  Pull-up to VCC (typically
    # 2.2-4.7 kΩ for the 400 kHz fast mode the chip supports) required.
    # AUX_DA is the auxiliary I²C SDA for the on-board master function;
    # same drive type.
    PIN_DRIVE_TYPES: ClassVar[dict[str, "DriveType"]] = {
        'SDA':    DriveType.OPEN_DRAIN,
        'AUX_DA': DriveType.OPEN_DRAIN,
    }

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
        # Drive every OUT pin with an IdleDriver so the topology
        # validates.  AUX_CL and INT are Digital; REGOUT and CPOUT
        # are Analog rails the chip's internal LDO / charge pump
        # generates.
        self._drivers = {
            'AUX_CL': IdleDriver(Digital, idle_value=False, domain=domain),
            'REGOUT': IdleDriver(Analog,  idle_value=1.8,   domain=domain),
            'INT':    IdleDriver(Digital, idle_value=False, domain=domain),
            'CPOUT':  IdleDriver(Analog,  idle_value=0.0,   domain=domain),
        }
        by_name = {pin.id.name: pin for pin in pins}
        for name, drv in self._drivers.items():
            wire(drv.ports['out'], by_name[name].internal)
        super().__init__(pins=pins, cells=list(self._drivers.values()))

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
