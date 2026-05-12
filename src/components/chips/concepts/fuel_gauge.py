from typing import Annotated

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital

from components.passives.cell import soc_from_ocv


class FuelGauge(FactorNode):
    """Steady-state state-of-charge estimator for a 1S Li-Ion pack.

    The real BQ27546-G1 estimates state-of-charge with TI's patented
    Impedance Track™ algorithm: it integrates current through a sense
    resistor over time (coulomb counting) and combines that with a
    voltage-vs-SoC table and an internal impedance model.  None of
    that fits in a voltage-only, time-less graph — there is no current
    to integrate and no `t` to integrate over.

    What this cell can do honestly is the *power-on* fallback: invert
    the open-circuit-voltage curve to get a coarse SoC from the
    measured cell voltage alone.  Real fuel gauges do exactly this
    until enough current has flowed for the integrator to take over.
    The cell exposes the result via Python state (so the wrapping
    chip can re-expose it as a property — stand-in for an I²C read).

    Beyond the soft-state SoC, the cell also drives one *real* digital
    output: the SE (shutdown-enable) pin.  In the datasheet SE is a
    push-pull output that asserts to put the system into low-power
    mode; here it drops LOW when the estimated SoC falls below a
    configurable shutdown threshold — a faithful first-order model of
    "battery dead, ask the host to wind down."

    Ports
    -----
        bat              Analog IN  — cell-voltage measurement input.
        ts               Analog IN  — thermistor input (read but unused
                                      in SoC estimation; a placeholder
                                      so the chip's TS pin has somewhere
                                      to land).
        srp, srn         Analog IN  — coulomb-counter inputs.  Read but
                                      unused (no current in our graph).
        vcc_out          Analog OUT — regulated VREG25 output.  Driven
                                      to a constant 2.5 V whenever the
                                      gauge has a valid BAT measurement.
        se               Digital OUT — shutdown-enable, push-pull.
                                       HIGH = run, LOW = shut down.

    Python state
    ------------
        state_of_charge      0.0..1.0 — most-recent estimate.
        shutdown_threshold   default 0.05 (5 %); below this SE goes LOW.
    """

    __slots__ = ('_ports', '_state_of_charge', '_shutdown_threshold')

    DEFAULT_SHUTDOWN_THRESHOLD: float = 0.05
    VREG25_VOLTAGE: float = 2.5

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        shutdown_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = (
            DEFAULT_SHUTDOWN_THRESHOLD
        ),
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._shutdown_threshold = float(shutdown_threshold)
        self._state_of_charge: float = 0.0
        self._ports = {
            'bat':     Port('bat',     Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'ts':      Port('ts',      Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'srp':     Port('srp',     Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'srn':     Port('srn',     Direction.IN,  domain,
                            mandatory=False, signal_type=Analog),
            'vcc_out': Port('vcc_out', Direction.OUT, domain,
                            mandatory=False, signal_type=Analog),
            'se':      Port('se',      Direction.OUT, domain,
                            mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def state_of_charge(self) -> float:
        return self._state_of_charge

    @property
    def shutdown_threshold(self) -> float:
        return self._shutdown_threshold

    def evaluate(self) -> None:
        v_bat = self._ports['bat'].value
        if v_bat is None:
            # Pin undriven — no measurement, no estimate, no VCC.
            # Matches a real chip pre-POR.
            self._state_of_charge = 0.0
            self._ports['vcc_out'].drive(None)
            self._ports['se'].drive(None)
            return
        self._state_of_charge = soc_from_ocv(float(v_bat))
        # Internal LDO regulates BAT down to the VREG25 rail whenever
        # the cell can supply enough headroom; below ~2.45 V the
        # datasheet drops the output, but the curve is well above
        # that for any SoC > 0 % so we always drive the nominal value.
        self._ports['vcc_out'].drive(self.VREG25_VOLTAGE)
        self._ports['se'].drive(
            self._state_of_charge > self._shutdown_threshold
        )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, v_bat: float | None) -> dict[str, float | bool | None]:
        """Standalone-test invocation: drive the BAT pin, evaluate,
        and return the SoC estimate and SE pin state."""
        self._assert_no_inputs_wired()
        self._ports['bat'].drive(v_bat)
        self.evaluate()
        return {
            'state_of_charge': self._state_of_charge,
            'se':              self._ports['se'].value,
        }

    def __repr__(self) -> str:
        return (f"FuelGauge(state_of_charge={self._state_of_charge!r}, "
                f"shutdown_threshold={self._shutdown_threshold!r})")
