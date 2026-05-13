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
from .concepts.linear_regulator import LinearRegulator


@register('LP2950')
class LP2950(Chip):
    """Texas Instruments LP2950 — micropower +5V LDO regulator, 100mA (TO-92).

    Composes a private `LinearRegulator` cell wired between INPUT, GND,
    and OUTPUT.  Dropout is ~0.4 V at 100 mA (the part's defining
    feature — far lower than a 7805's 2 V), which makes it the LDO of
    choice for battery-powered builds where the supply voltage drifts
    toward 5 V as the cells discharge.
    """

    __slots__ = ('_refdes_number', '_regulator')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"

    OUTPUT_VOLTAGE: ClassVar[float] = 5.0
    DROPOUT_V:      ClassVar[float] = 0.4

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
        self._regulator = LinearRegulator(
            output_voltage=self.OUTPUT_VOLTAGE,
            dropout_v=self.DROPOUT_V,
            domain=domain,
        )
        by_name = {pin.id.name: pin for pin in pins}
        wire(by_name['INPUT'].internal,  self._regulator.ports['v_in'])
        wire(self._regulator.ports['v_out'], by_name['OUTPUT'].internal)
        wire(by_name['GND'].internal,    self._regulator.ports['gnd'])
        super().__init__(pins=pins, cells=[self._regulator])

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
        return f"LP2950(refdes={self.refdes!r})"
