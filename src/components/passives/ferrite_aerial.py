from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Henries
from framework.registry import register


@register('FerriteAerial')
class FerriteAerial(Part):
    """Ferrite-rod tuned aerial coil — the antenna *and* the inductor
    in one part.

    A ferrite aerial is a coil of fine enamelled wire wound around a
    ferrite rod (typically 8–10 mm diameter, 50–100 mm long).  In a
    crystal radio it serves two functions simultaneously:

      - **Aerial** — the ferrite rod concentrates the local magnetic
        component of an incoming radio wave, inducing a voltage in
        the coil.  Pointing the rod broadside to the transmitting
        station maximises reception; pointing the rod *at* the
        station makes the station inaudible (this directional null
        is the key reason ferrite aerials work without an external
        long-wire antenna).
      - **Inductor** — the coil + ferrite forms the L of an LC tank
        with the variable tuning capacitor.  The tank's resonant
        frequency selects which station is heard.

    Topologically a `FerriteAerial` is identical to an `Inductor`:
    two-terminal Analog passive, opaque under graph evaluation.  The
    distinct class exists so the BOM and assembly guide can tell a
    builder "this is the aerial-coil, not an in-circuit choke";
    sourcing the right part (Denco MW5FR class) matters.

        FerriteAerial(henries=400e-6, refdes_number=1)  # ~400 µH
    """

    __slots__ = ('_henries', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'L'
    # Ferrite aerial is a 50–100 mm rod with a coil wound around it,
    # mounted in a clip beside the breadboard; two flying leads connect
    # the coil's terminals to LC-tank tie strips.  The breadboard-side
    # connection is a 2-pin header pair; the aerial assembly itself is
    # sourced from the BOM (Denco MW5FR class or equivalent) and lives
    # off-board.  The previous Inductor_THT:L_Radial_* footprint
    # mis-modelled it as a 10 mm standing inductor whose 3-hole pitch
    # can't physically accommodate the 100 mm rod.
    FOOTPRINT: ClassVar[str | None] = "Connector:Conn_01x02_Pin"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'off_board_flying_lead',
        'lead_spacing_holes': 2,
        'description': (
            'Ferrite-rod tuned aerial coil — off-board with two flying '
            'leads to the LC-tank tie strips.  The rod itself sits in a '
            'clip beside the breadboard.'
        ),
    }

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('henries',)

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Check the coil's DC continuity with a multimeter.** Probe "
        "across the two enamelled-wire leads — the resistance should "
        "be a few ohms to a few tens of ohms (the wire is thin and "
        "many turns long).  OL means a broken wire (look for a snag "
        "where the wire leaves the rod); a hard short means the wire "
        "has chafed against the rod's varnish.",
        "**Confirm the ferrite rod itself is intact.**  Hold the "
        "rod up to a magnet — a healthy ferrite is mildly attracted "
        "but not magnetic in the strong-iron sense.  A cracked rod "
        "(common after a drop) looks fine externally but tunes "
        "weakly and across a narrower range; replace it.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Aerial coil orientation matters.** Lay the ferrite rod "
        "horizontally and rotate it to peak the signal from your "
        "chosen station; the rod has a null along its long axis (no "
        "signal at all from a station directly off the end of the "
        "rod) and a maximum broadside to the station.  Mount the rod "
        "loosely on the breadboard so it can be re-aimed.",
        "**Don't add an external long-wire antenna and an earth in "
        "parallel with the ferrite-aerial-only design unless you "
        "know what you're doing.**  An external aerial swamps the "
        "ferrite rod's directional null and degrades selectivity; "
        "the design becomes susceptible to local interference.  "
        "Penfold's BP107 P27 is deliberately *ferrite-only*: simpler "
        "to build, quieter, more selective.",
    )

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
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
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
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> Henries:
        return self._henries

    def __str__(self) -> str:
        return f"FerriteAerial: {float(self._henries)} H"

    def __repr__(self) -> str:
        return (f"FerriteAerial(henries={float(self._henries)!r}, "
                f"refdes={self.refdes!r})")
