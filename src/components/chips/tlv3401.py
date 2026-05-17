from typing import ClassVar

from pydantic import validate_call

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.wire import wire
from .concepts.opamp import OpAmp


@register('TLV3401')
class TLV3401(Chip):
    """Texas Instruments TLV3401 — single nanopower open-drain CMOS comparator (SOT-23-5).

    Composes one private `OpAmp` cell wired to the chip's
    IN_POS / IN_NEG / OUT pins with VCC / GND as supply.  Real
    output is open-drain; the cell drives rail-to-rail for
    simulation purposes (add an external pull-up at the bench).
    """

    __slots__ = ('_refdes_number', '_cell')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_SMD:SOT-23-5"
    # Datasheet specifies an open-drain output stage; external pull-up
    # to VCC required for HIGH levels.  The cell drives rail-to-rail
    # for simulation purposes (the bench needs the pull-up).
    PIN_DRIVE_TYPES: ClassVar[dict[str, "DriveType"]] = {
        'OUT': DriveType.OPEN_DRAIN,
    }

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'OUT', Direction.OUT, Analog),
        (2, 'GND', Direction.IN,  Analog),
        (3, 'IN_POS', Direction.IN,  Analog),
        (4, 'IN_NEG', Direction.IN,  Analog),
        (5, 'VCC', Direction.IN,  Analog),
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
        self._cell = OpAmp(domain)
        by_name = {pin.id.name: pin for pin in pins}
        wire(by_name['IN_POS'].internal, self._cell.ports['v_in_pos'])
        wire(by_name['IN_NEG'].internal, self._cell.ports['v_in_neg'])
        wire(self._cell.ports['out'], by_name['OUT'].internal)
        wire(by_name['VCC'].internal, self._cell.ports['v_supply'])
        wire(by_name['GND'].internal, self._cell.ports['v_gnd'])
        super().__init__(pins=pins, cells=[self._cell])

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
        return f"TLV3401(refdes={self.refdes!r})"
