from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Volts
from framework.registry import register


# Five-point piece-wise linear open-circuit-voltage curve for a generic
# single-cell Li-Ion chemistry.  The real curve is monotonically
# increasing with state-of-charge, has a flat plateau around the middle
# of the range, and steep skirts near the extremes.  These five anchor
# points are enough to give a fuel-gauge cell something to invert and
# look right when plotted against scenario traces.
#
# Listed lowest SoC first so a linear-search interpolation reads
# naturally.  Values are typical of the cells the BQ27546-G1 targets
# (a 4.2 V fully-charged Li-Ion pack).
_OCV_CURVE: tuple[tuple[float, float], ...] = (
    (0.00, 3.000),    # empty — discharge cutoff
    (0.10, 3.400),    # knee
    (0.50, 3.700),    # mid-discharge plateau
    (0.90, 4.000),    # near-full
    (1.00, 4.200),    # fully charged
)


def _ocv_from_soc(soc: float) -> float:
    """Return open-circuit terminal voltage for a given state-of-charge.

    Linearly interpolates between the anchor points of the curve.
    Inputs outside `[0, 1]` are clamped — a real cell can't be more
    full than full or more empty than empty, and saturating is the
    physically honest response.
    """
    soc = max(0.0, min(1.0, soc))
    for (soc_lo, v_lo), (soc_hi, v_hi) in zip(_OCV_CURVE, _OCV_CURVE[1:]):
        if soc <= soc_hi:
            span = soc_hi - soc_lo
            if span == 0.0:
                return v_lo
            fraction = (soc - soc_lo) / span
            return v_lo + fraction * (v_hi - v_lo)
    return _OCV_CURVE[-1][1]


def soc_from_ocv(voltage: float) -> float:
    """Inverse of `_ocv_from_soc` — fuel-gauge SoC estimate from a
    cell's terminal voltage, using the same anchor points.

    Exported (no underscore) so the matching `FuelGauge` cell can
    share the chemistry curve without duplicating constants.  In a
    real BQ27546-G1 this inversion is the *steady-state* fallback
    used at power-on before enough current has been integrated for
    Impedance Track to take over.
    """
    if voltage <= _OCV_CURVE[0][1]:
        return 0.0
    for (soc_lo, v_lo), (soc_hi, v_hi) in zip(_OCV_CURVE, _OCV_CURVE[1:]):
        if voltage <= v_hi:
            span = v_hi - v_lo
            if span == 0.0:
                return soc_lo
            fraction = (voltage - v_lo) / span
            return soc_lo + fraction * (soc_hi - soc_lo)
    return 1.0


@register('Cell')
class Cell(FactorNode):
    """Single-cell Li-Ion battery, modelled as a voltage source.

    A real Li-Ion cell stores chemical energy and presents a terminal
    voltage that depends on its state-of-charge, temperature, and the
    instantaneous current drawn.  A voltage-only steady-state graph
    cannot represent current or capacity-versus-time, so this cell
    models only the *open-circuit* voltage curve: given a SoC set as
    Python state by the surrounding composite, it emits the
    corresponding terminal voltage on `pos` (with `neg` driving the
    reference 0 V).  The state can't move on its own — discharge has
    to be prescribed by the scenario, the same idiom `BLDCMotor` uses
    for rotor angle.

    Ports
    -----
        pos     Analog OUT — positive terminal.  Driven to OCV(SoC).
        neg     Analog OUT — negative terminal.  Driven to 0 V.

    Python state
    ------------
        state_of_charge   0.0..1.0; settable directly so a scenario
                          can walk the cell from full to empty.
    """

    __slots__ = ('_ports', '_state_of_charge', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'BT'
    FOOTPRINT: ClassVar[str | None] = "Battery:BatteryHolder_Keystone_1042_1x18650"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'pos': 1, 'neg': 2}

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        initial_state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._state_of_charge: float = float(initial_state_of_charge)
        self._ports = {
            'pos': Port('pos', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
            'neg': Port('neg', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def state_of_charge(self) -> float:
        return self._state_of_charge

    @state_of_charge.setter
    def state_of_charge(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"state_of_charge must be in [0, 1]; got {value!r}"
            )
        self._state_of_charge = float(value)

    @property
    def terminal_voltage(self) -> Volts:
        """OCV at the present state-of-charge."""
        return Volts(_ocv_from_soc(self._state_of_charge))

    def evaluate(self) -> None:
        self._ports['pos'].drive(float(self.terminal_voltage))
        self._ports['neg'].drive(0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)] | None = None,
    ) -> Volts:
        """Standalone-test invocation: optionally set a new SoC,
        evaluate, and return the resulting terminal voltage."""
        self._assert_no_inputs_wired()
        if state_of_charge is not None:
            self.state_of_charge = state_of_charge
        self.evaluate()
        return self.terminal_voltage

    def __repr__(self) -> str:
        return (f"Cell(state_of_charge={self._state_of_charge!r}, "
                f"refdes={self.refdes!r})")
