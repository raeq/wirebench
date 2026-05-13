from typing import ClassVar

from pydantic import Field, validate_call
from typing import Annotated

from framework.chip import Chip
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.wire import wire
from .concepts.linear_regulator import LinearRegulator


@register('LM317')
class LM317(Chip):
    """Texas Instruments LM317 — adjustable +1.25V to +37V positive regulator (TO-220).

    Composes a private `LinearRegulator` cell parameterised by the
    target output voltage the user passes in.  Real LM317 silicon
    holds a 1.25 V reference between OUTPUT and ADJ; users set the
    output by sizing an external R1 / R2 divider on the ADJ pin
    (typical pair: R1 = 240 Ω, R2 chosen to hit the target).  The
    framework's voltage-only graph doesn't compute the divider — the
    user asserts the target voltage at construction (the same value
    they sized R2 for) and the cell drives the OUTPUT pin to it.
    For accurate divider feedback / load-regulation simulation,
    substitute a SPICE .SUBCKT.
    """

    __slots__ = ('_refdes_number', '_regulator', '_output_voltage')

    REFDES_PREFIX: ClassVar[str] = 'U'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"

    DROPOUT_V: ClassVar[float] = 2.0

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The LM317 sets its output voltage from two resistors — R1 "
        "(OUT to ADJ) and R2 (ADJ to GND).** The math: output voltage "
        "= 1.25 × (1 + R2/R1). A typical pair is R1 = 240 Ω plus "
        "R2 chosen for the voltage you want — e.g. R2 = 720 Ω gives "
        "5 V output. Swap R1 and R2 around and the equation inverts; "
        "the regulator either tries to output less than its minimum "
        "or much more than the input can supply.",
        "**Always have at least ~10 mA flowing through the output — "
        "even at no load.** Below that current, the LM317 loses "
        "regulation and the output drifts upward. The R1/R2 divider "
        "you already need (sized around 240 Ω for R1) bleeds ~5 mA, "
        "and any actual load adds to that, so this usually takes "
        "care of itself.",
        "**Add a 10 µF capacitor from the ADJ pin (pin 1) to ground.** "
        "Without it, most of the supply's ripple comes straight through "
        "to the output — especially at low loads. The cap shunts the "
        "ripple to ground at the ADJ pin instead. This one-cap fix is "
        "famous enough that the datasheet calls it out explicitly.",
        "**If you have both a big output cap (>25 µF) *and* the ADJ "
        "bypass cap above, add two protection diodes.** When the supply "
        "shorts out at power-off, the caps can dump current back "
        "through the regulator and crack the chip. A 1N4001 from OUT "
        "to IN with the band pointing at IN, and another from OUT to "
        "ADJ with the band pointing at ADJ, gives the dump current "
        "somewhere to go.",
    )

    _PIN_TABLE: ClassVar[tuple[tuple[int, str, Direction, type], ...]] = (
        (1, 'ADJ',    Direction.IN,  Analog),
        (2, 'OUTPUT', Direction.OUT, Analog),
        (3, 'INPUT',  Direction.IN,  Analog),
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
        output_voltage: Annotated[float, Field(ge=1.25, le=37.0)] = 5.0,
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
        # ADJ is the reference pin on a real LM317 (V_OUT - V_ADJ ≈
        # 1.25 V).  Wire it to the cell's `gnd` port so ERC sees the
        # ADJ net as having a reader; the cell itself ignores v_gnd
        # in its drive calculation (the user asserts the absolute
        # output_voltage at construction).
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
        return f"LM317(refdes={self.refdes!r})"
