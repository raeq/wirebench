"""Linear-regulator behavioural cell.

The internal model that every fixed-output positive linear regulator
(7805, 7812, AMS1117-3.3, AMS1117-5.0, LP2950, …) instantiates inside
its chip's __init__.  Without this cell the regulator's OUTPUT pin
would be a passive BIDIR from the framework's perspective (Pin
external faces are conductors; the ERC walker looks through to the
*internal* face for a real driver), and any net touching the output
would be flagged as floating.

The cell drives v_out internally so the chip's OUTPUT Pin external
face acquires a real driver via the conductor walk.  Behaviour:

  - v_in unknown (None) → v_out = 0 V
  - v_in below dropout threshold → v_out tracks (v_in − DROPOUT_V)
  - v_in above (OUTPUT_VOLTAGE + DROPOUT_V) → v_out clamped at
    OUTPUT_VOLTAGE
  - v_in between → linear handover region

The model is steady-state and voltage-only; it ignores load current,
thermal shutdown, quiescent draw, and dropout-vs-load curves.  For
accurate analogue / timing-sensitive simulation, substitute a SPICE
.SUBCKT model — but at the topology / ERC level this cell is enough
to make the framework see the regulator as a driver.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class LinearRegulator(FactorNode):
    """Steady-state behavioural model of a fixed-output linear regulator.

    Ports
    -----
    v_in  (IN,  Analog) — unregulated input voltage, referenced to gnd
    v_out (OUT, Analog) — regulated output voltage
    gnd   (IN,  Analog) — reference / 0 V (always read; never driven by
                          this cell — the supply rail itself is what
                          ties gnd to 0 V externally)

    Subclasses or per-instance constructors set OUTPUT_VOLTAGE (the
    nominal regulated output, e.g. 5.0 V) and DROPOUT_V (the minimum
    input-to-output headroom, e.g. 2.0 V for a 7805, 0.4 V for an LDO
    like the LP2950).
    """

    __slots__ = ('_output_voltage', '_dropout_v', '_ports')

    # Defaults aren't useful in isolation — every concrete instance
    # must pass OUTPUT_VOLTAGE and DROPOUT_V.  The class-level slots
    # exist only to satisfy the documentation pattern; the real values
    # live on each instance.
    OUTPUT_VOLTAGE: ClassVar[float] = 5.0
    DROPOUT_V: ClassVar[float] = 2.0

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        output_voltage: float,
        dropout_v: float,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._output_voltage = float(output_voltage)
        self._dropout_v = float(dropout_v)
        self._ports = {
            'v_in':  Port('v_in',  Direction.IN,  domain,
                          mandatory=False, signal_type=Analog),
            'v_out': Port('v_out', Direction.OUT, domain,
                          mandatory=False, signal_type=Analog),
            'gnd':   Port('gnd',   Direction.IN,  domain,
                          mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def output_voltage(self) -> float:
        return self._output_voltage

    @property
    def dropout_v(self) -> float:
        return self._dropout_v

    def evaluate(self) -> None:
        v_in_raw = self._ports['v_in'].value
        v_in = float(v_in_raw) if v_in_raw is not None else 0.0
        v_unclamped = v_in - self._dropout_v
        v_regulated = max(0.0, min(self._output_voltage, v_unclamped))
        self._ports['v_out'].drive(v_regulated)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, v_in: float | None) -> float:
        self._assert_no_inputs_wired()
        self._ports['v_in'].drive(v_in)
        self.evaluate()
        result = self._ports['v_out'].value
        return float(result) if result is not None else 0.0

    def __repr__(self) -> str:
        return (f"LinearRegulator(v_out={self._output_voltage}, "
                f"dropout={self._dropout_v}, "
                f"out={self._ports['v_out'].value!r})")
