from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Farads
from framework.registry import register


@register('Capacitor')
class Capacitor(FactorNode):
    """Ideal capacitor.  Charge accumulates: Q = C × V, I = C × dV/dt.

    A real capacitor is passive: both terminals are voltage nodes and
    the current at any instant depends on the rate of change of the
    voltage across it.  A steady-state voltage-only simulator cannot
    derive that current, so a wired capacitor is opaque under graph
    evaluation — `evaluate()` is a no-op.  Use the value to size
    timing or decoupling networks; the BOM / netlist exporter
    reads it via the `farads` property.

        Capacitor(100e-9)                # 100 nF
        Capacitor(Farads(100e-9))        # same, explicit units
        Capacitor(Microfarads(0.1))      # 0.1 µF — bypass cap
    """

    __slots__ = ('_farads', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'C'
    FOOTPRINT: ClassVar[str | None] = "Capacitor_SMD:C_0603_1608Metric"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        farads: Annotated[float, Field(gt=0)] | Farads,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._farads: Farads = Farads(farads)
        # mandatory=False: opaque under evaluation, so wiring is not a
        # simulation requirement.  In a real circuit both terminals must
        # of course be connected — that's a hardware-design constraint
        # the framework does not enforce.
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def farads(self) -> Farads:
        return self._farads

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        # I = C × dV/dt cannot be derived from terminal voltages alone
        # in a steady-state graph, so a wired capacitor is opaque.
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> Farads:
        # No signal interface — return the stored value for sizing /
        # documentation.  Skips _assert_no_inputs_wired because it
        # touches no ports.
        return self._farads

    def __str__(self) -> str:
        return f"{float(self._farads)} F"

    def __repr__(self) -> str:
        return f"Capacitor(farads={float(self._farads)!r}, refdes={self.refdes!r})"
