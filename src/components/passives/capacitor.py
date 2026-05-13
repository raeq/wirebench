from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Farads
from framework.registry import register


@register('Capacitor')
class Capacitor(Part):
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

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'radial_2lead',
        'lead_spacing_holes': 1,
    }

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**For an electrolytic capacitor, use your multimeter's diode-"
        "test or continuity mode to confirm it charges.** Put the red "
        "probe on the + lead (longer / unmarked side) and the black on "
        "the − lead (the side with the stripe). A healthy cap shows a "
        "voltage that climbs over a second or two and then settles to "
        "OL — the meter is charging the cap through its internal "
        "current source. Reverse the leads briefly to discharge and "
        "repeat. A cap that immediately reads zero (continuous beep) "
        "is shorted; one that reads OL from the first touch is open "
        "or has lost its capacitance.",
        "**Confirm the printed value matches what the design calls "
        "for** — capacitor markings are easy to misread. Big "
        "electrolytics print the value directly (e.g. '100 µF 25 V'); "
        "smaller ceramics use a three-digit code where the first two "
        "digits are the value in pF and the third is the number of "
        "trailing zeros ('104' means 100,000 pF = 100 nF = 0.1 µF). "
        "A capacitance meter (built into many DMMs) confirms the "
        "value within ±10%.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Electrolytic capacitors have a + and − end — always check "
        "which is which.** The longer lead is + (positive); the can "
        "has a stripe along the side near the − (negative) lead. "
        "Install one backwards and it heats up, vents boiling "
        "electrolyte, and sometimes pops loudly — this is the main "
        "reason 'always wear safety glasses' is a bench rule. Ceramic "
        "and film capacitors are not polarised and go in either way.",
        "**Always use a capacitor rated well above the voltage it will "
        "actually see.** Rule of thumb: pick a part rated for at least "
        "1.5 times the highest steady-state voltage in your circuit. "
        "A 16 V cap on a 12 V rail will die early as the supply rings "
        "or sags; a 25 V cap shrugs the same conditions off. (The "
        "rated voltage is the *working* maximum, not a nominal "
        "indicator.)",
        "**Different capacitor types do different jobs — match the "
        "type to the role.** Big electrolytics (microfarads) sit on "
        "supply rails as bulk reservoirs; small ceramics (10–100 nF) "
        "go right next to chip supply pins as local decouplers; "
        "film and polypropylene caps handle precision timing where "
        "drift matters. Putting an electrolytic where a ceramic "
        "belongs (and vice versa) is the single most common 'why "
        "does this circuit oscillate?' bench mistake.",
    )

    # SMD 0603 by default for PCB export, but hobby breadboard use is
    # overwhelmingly through-hole ceramic / electrolytic capacitors.
    @property
    def is_through_hole(self) -> bool:
        return True

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
