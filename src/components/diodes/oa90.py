from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D_OA90')
class D_OA90(Diode):
    """Mullard OA90 — small-signal germanium point-contact diode.

    The OA90 (and its close cousins OA91, 1N34A, 1N60) is the canonical
    *crystal-radio* detector diode.  Two electrical characteristics
    set it apart from a silicon signal diode like the 1N4148:

      - Forward voltage drop ≈ 0.2 V (vs ~0.7 V for silicon).  The
        lower V_F is what makes germanium the right choice for
        rectifying the microwatt RF signals a crystal radio's
        antenna picks up; a silicon diode wouldn't see enough drive
        to conduct.

      - Higher reverse leakage and lower peak reverse voltage.  For
        envelope detection at audio frequencies these don't matter;
        for HF / VHF rectification they do.

    For topology validation the OA90 is treated like the 1N4148 —
    black-box, two ports, no behavioural model.  Per-class metadata
    (the differing V_F) flows through the BOM and assembly guide so
    a builder knows to source the germanium part, not silicon.

    Substitutes: 1N34A, OA91, 1N60.  All four behave the same to
    within a few mV of V_F drop and tens of µA of leakage.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    # Forward voltage (typical, room temp, light forward current).
    # The germanium-vs-silicon distinction lives in this constant —
    # downstream tooling that cares (a SPICE model picker, an
    # assembly-guide blurb) reads it here.
    V_F: ClassVar[float] = 0.2

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Use your multimeter's diode-test mode to confirm the "
        "OA90's forward drop.** Red probe on the anode (unmarked "
        "end), black on the cathode (banded end): a healthy "
        "germanium diode reads about 0.2 V — much lower than a "
        "silicon 1N4148's 0.6 V.  If you measure 0.6 V you've grabbed "
        "a silicon diode by mistake.  Both legs showing 0.2 V means "
        "the diode is shorted; both showing OL means it's open.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Use the OA90 specifically because its forward voltage is "
        "low.**  In a crystal radio, the antenna delivers tens of "
        "microvolts of RF signal — too little to forward-bias a "
        "silicon diode at all.  Germanium's 0.2 V V_F just barely "
        "rectifies it.  Drop a 1N4148 in here and the radio is "
        "*completely* silent; substitute a Schottky 1N5817 and you "
        "get the same low V_F as germanium with better reverse "
        "characteristics — a modern equivalent.",
        "**The OA90 is fragile.** Point-contact germanium diodes "
        "don't tolerate the soldering heat that silicon DO-35 parts "
        "shrug off.  Use a heat sink (a crocodile clip on the lead "
        "between the iron and the body) while soldering, and don't "
        "leave the iron on the lead for more than 2–3 seconds.  An "
        "overheated germanium diode reads short or open afterwards "
        "— the junction has failed permanently.",
        "**Original OA90s are increasingly rare.** New old stock "
        "from radio-restoration suppliers is the only reliable "
        "source; pulled-from-broken-radios specimens are common but "
        "often degraded.  For new builds, the 1N34A is the closest "
        "modern equivalent and is still in production; a Schottky "
        "1N5817 substitutes electrically with slightly different "
        "RF behaviour.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'anode':   Port('anode',   Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            'cathode': Port('cathode', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
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

    def evaluate(self) -> None:
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        return None

    def __repr__(self) -> str:
        return f"D_OA90(refdes={self.refdes!r})"
