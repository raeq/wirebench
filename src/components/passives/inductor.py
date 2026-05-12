from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Henries
from framework.registry import register


@register('Inductor')
class Inductor(FactorNode):
    """Ideal inductor.  Stores energy in a magnetic field: V = L × dI/dt.

    A real inductor is passive: both terminals are voltage nodes and
    the voltage across it at any instant depends on the rate of change
    of the current through it.  A steady-state voltage-only simulator
    cannot derive that current, so a wired inductor is opaque under
    graph evaluation — `evaluate()` is a no-op.  Use the value to size
    filter / energy-storage networks; the BOM / netlist exporter reads
    it via the `henries` property.

        Inductor(100e-6)                 # 100 µH
        Inductor(Henries(0.01))          # 10 mH, explicit unit base
        Inductor(Microhenries(47))       # 47 µH — choke
    """

    __slots__ = ('_henries', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'L'
    FOOTPRINT: ClassVar[str | None] = "Inductor_SMD:L_0603_1608Metric"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'axial_2lead',
        'lead_spacing_holes': 3,
    }

    # SMD 0603 by default for PCB export; hobby breadboard inductors are
    # typically axial through-hole chokes.
    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        henries: Annotated[float, Field(gt=0)] | Henries,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._henries: Henries = Henries(henries)
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
    def henries(self) -> Henries:
        return self._henries

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        # V = L × dI/dt cannot be derived from terminal voltages alone
        # in a steady-state graph, so a wired inductor is opaque.
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> Henries:
        # No signal interface — return the stored value for sizing /
        # documentation.  Skips _assert_no_inputs_wired because it
        # touches no ports.
        return self._henries

    def __str__(self) -> str:
        return f"{float(self._henries)} H"

    def __repr__(self) -> str:
        return f"Inductor(henries={float(self._henries)!r}, refdes={self.refdes!r})"
