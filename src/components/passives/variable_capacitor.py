from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Farads
from framework.registry import register


@register('VariableCapacitor')
class VariableCapacitor(Part):
    """Tuning capacitor — a mechanical variable capacitor.

    A real variable capacitor consists of two sets of parallel plates,
    one fixed (the *stator*) and one mounted on a rotating shaft (the
    *rotor*).  As the rotor turns, the overlap area changes and so
    does the capacitance.  The standard form factor for medium-wave
    crystal-set tuning is a solid-dielectric variable capacitor
    (Jackson Dielecon class) with a 250 pF or 300 pF maximum.

    For wirebench's topology validation the part is opaque under
    graph evaluation, just like `Capacitor`.  The two values
    `min_farads` / `max_farads` bracket the operating range; a real
    circuit's tuning behaviour is informational metadata for the
    surrounding design (the LC tank's resonant frequency sweeps from
    `1 / (2π √(L · max_F))` to `1 / (2π √(L · min_F))`).

    The two terminals are the rotor and the stator.  Standard pin
    numbering (`t1` → rotor → 1, `t2` → stator → 2) matches the
    `Capacitor` convention so the breadboard renderer treats it as
    a generic 2-lead part.

        VariableCapacitor(min_farads=10e-12, max_farads=300e-12,
                          refdes_number=1)   # 10–300 pF tuning cap
    """

    __slots__ = ('_min_farads', '_max_farads', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'C'
    # Variable tuning capacitor is panel-mounted with flying leads to two
    # breadboard tie strips — model the breadboard side as a 2-pin
    # header.  The actual variable cap is documented in the BOM with the
    # part number (Jackson Dielecon class) and lives off-board; the
    # previous Capacitor_THT:CP_Radial_* footprint mis-modelled it as a
    # polarised electrolytic on a 10 mm radial pad.
    FOOTPRINT: ClassVar[str | None] = "Connector:Conn_01x02_Pin"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'off_board_flying_lead',
        'lead_spacing_holes': 2,
        'description': (
            'Panel-mounted variable tuning capacitor; two flying leads '
            'connect rotor and stator to breadboard tie strips.'
        ),
    }

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('min_farads', 'max_farads')

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Use a capacitance meter to confirm the rotor sweeps "
        "between the stated min and max values.**  Connect the meter "
        "across the two terminals, turn the rotor fully one way and "
        "note the reading; turn it fully the other way and note the "
        "reading.  A typical 300 pF tuning cap reads ~5–10 pF at the "
        "low end (plates fully open) and 280–300 pF at the high end "
        "(plates fully meshed).  Out-of-range readings mean the part "
        "is mis-labelled or damaged.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Variable capacitors are mechanically delicate.**  The "
        "plates are spaced by hundredths of a millimetre; dropping "
        "the part can warp the plates so they short.  Test the part "
        "with a continuity / Ω meter across the terminals before "
        "installing — anything below ~100 MΩ at the closed-plate end "
        "means the rotor is touching the stator, and the cap is "
        "shorted across part of its range.",
        "**The rotor (shaft) is the high-impedance contact in most "
        "designs.**  Connect the rotor to the lowest-noise side of "
        "the tuned tank (typically the antenna side, not the ground "
        "side); the rotor's shaft makes a fine accidental antenna "
        "for hum and stray RF.  Crystal-set practice is to ground "
        "the rotor frame so the human hand's capacitance to ground "
        "(when adjusting the dial) doesn't detune the tank.",
    )

    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        min_farads: Annotated[float, Field(gt=0)] | Farads,
        max_farads: Annotated[float, Field(gt=0)] | Farads,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._min_farads: Farads = Farads(min_farads)
        self._max_farads: Farads = Farads(max_farads)
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def min_farads(self) -> Farads:
        return self._min_farads

    @property
    def max_farads(self) -> Farads:
        return self._max_farads

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> tuple[Farads, Farads]:
        return (self._min_farads, self._max_farads)

    def __str__(self) -> str:
        return (f"VC: {float(self._min_farads)}–{float(self._max_farads)} F")

    def __repr__(self) -> str:
        return (f"VariableCapacitor("
                f"min_farads={float(self._min_farads)!r}, "
                f"max_farads={float(self._max_farads)!r}, "
                f"refdes={self.refdes!r})")
