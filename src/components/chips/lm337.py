from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.wire import wire
from .concepts.linear_regulator import LinearRegulator


@register('LM337')
class LM337(Chip):
    """Texas Instruments LM337 — adjustable -1.25V to -37V negative regulator (TO-220).

    Composes a private `LinearRegulator` cell with a *negative*
    output_voltage so the sign-aware clamp keeps the output in the
    [OUTPUT_VOLTAGE, 0 V] range.  User asserts the target output at
    construction (the same value they sized the external R1 / R2
    pair to deliver via the ADJ reference pin) and the cell drives
    the OUTPUT pin to it.  Pin 2 is INPUT and pin 3 is OUTPUT —
    opposite of LM317.
    """

    __slots__ = ('_refdes_number', '_regulator', '_output_voltage')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"

    DROPOUT_V: ClassVar[float] = 2.0

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'ADJ',    Direction.IN,  Analog),
        (2, 'INPUT',  Direction.IN,  Analog),
        (3, 'OUTPUT', Direction.OUT, Analog),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
        output_voltage: Annotated[float, Field(ge=-37.0, le=-1.25)] = -5.0,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._output_voltage = float(output_voltage)
        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        self._regulator = LinearRegulator(
            output_voltage=self._output_voltage,
            dropout_v=self.DROPOUT_V,
            domain=domain,
        )
        by_name = {pin.id.name: pin for pin in pins}
        wire(by_name['INPUT'].internal,  self._regulator.ports['v_in'])
        wire(self._regulator.ports['v_out'], by_name['OUTPUT'].internal)
        wire(by_name['ADJ'].internal, self._regulator.ports['gnd'])
        super().__init__(pins=pins, cells=[self._regulator])

    @property
    def output_voltage(self) -> float:
        return self._output_voltage

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
        return f"LM337(refdes={self.refdes!r})"
