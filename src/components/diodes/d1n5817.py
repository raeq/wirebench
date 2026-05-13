from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N5817')
class D1N5817(Diode):
    """1N5817 — Schottky barrier rectifier (20 V / 1 A, low V_F, DO-41).

    Category A passive: the diode itself ships with no behavioural
    cell.  Its directional role (forward conduction in a series
    rectifier, reverse blocking in an OR matrix, freewheel in a
    flyback path) is a property of the *circuit using it*, not of
    the part.  Each role pairs the passive diode with the matching
    circuit-level cell:

      - series rectifier → instantiate `SeriesRectifier` alongside;
      - wired-OR matrix → instantiate `DiodeOR` alongside;
      - flyback / freewheel → no cell needed (the cathode net is
        driven by its rail; the anode net is driven by whatever
        switches the inductive load).

    V_R max = 20 V; I_F avg = 1 A; V_F typ ~0.3 V at hobby-sized
    currents; I_FSM = 25 A.  See `docs/behavioural-cell-audit-spec.md`
    §7.2.2 for the decision rationale.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**A Schottky reads a lower forward voltage than a silicon "
        "diode on the multimeter's diode test.** Red probe on the "
        "anode (unmarked end), black on the cathode (banded end): a "
        "healthy 1N5817 reads about 0.2–0.3 V forward, not the 0.6 V "
        "you'd see from a 1N4001 — the low drop is the Schottky's "
        "defining feature. Reverse the probes and the meter reads OL. "
        "If you read 0.6 V forward, somebody put a silicon diode in "
        "the Schottky bin.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The black band marks the cathode (− end)** — same convention "
        "as silicon diodes. The Schottky's marking matches the bar in "
        "the schematic symbol.",
        "**Use the 1N5817 wherever you'd use a 1N4001 but need lower "
        "voltage drop or faster switching.** Schottkys drop only ~0.3 V "
        "in forward bias (versus ~0.7 V for a silicon diode), so a "
        "switching-supply rectifier or a battery-OR diode loses less "
        "power as heat. The trade-off: Schottkys leak a small reverse "
        "current even when 'off' — over weeks they slowly drain the "
        "lower of two OR'd batteries, so don't use them for long-term "
        "battery backup arrangements.",
        "**This part only blocks 20 V reverse — don't use it where "
        "voltages exceed that.** A mains-rectifier transformer "
        "secondary, a 24 V motor flyback path, or anywhere ringing "
        "transients might exceed 20 V will pop the 1N5817. The 1N5819 "
        "(same package, 40 V reverse) handles more; above that, use a "
        "silicon diode like the 1N4007 instead.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'anode':   Port('anode',   Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'cathode': Port('cathode', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
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
        return f"D1N5817(refdes={self.refdes!r})"
