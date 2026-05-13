from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N4001')
class D1N4001(Diode):
    """1N4001 — 50 V / 1 A general-purpose silicon rectifier (DO-41).

    Black-box package model: `anode` and `cathode` ports; no behavioural
    model.  V_R max = 50 V; I_F avg = 1 A; V_F typ ~1.0 V @ 1 A; I_FSM = 30 A.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Use the multimeter's diode-test mode.** Red probe on the "
        "anode (unmarked end), black probe on the cathode (banded "
        "end): the meter reads about 0.6 V forward. Reverse the probes: "
        "OL. Both directions showing 0.6 V means a shorted diode; both "
        "showing OL means an open diode. Confirm the body marking "
        "matches what you wanted — 1N4001 / 1N4002 / … / 1N4007 all "
        "look identical externally; only the printed code distinguishes "
        "them, and they have different reverse-voltage ratings.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The black band marks the cathode (− end).** Same convention "
        "as every other diode — the band matches the bar in the "
        "schematic. Install a rectifier backwards on a transformer "
        "secondary and the diode conducts through its reverse-breakdown "
        "region; the diode usually pops and the fuse blows.",
        "**For mains-derived rectifiers, use the 1N4007 instead.** The "
        "1N4001 only blocks 50 V reverse, which sounds like a lot until "
        "a transformer secondary spike sails past that on switch-off. "
        "The 1N4007 is the same physical part with a 1000 V reverse "
        "rating; same price, much more headroom.",
        "**This is a slow diode — fine for 50/60 Hz mains but wrong for "
        "switching supplies.** Reverse recovery is around 2 µs, which "
        "is no problem at line frequency but a disaster at kHz "
        "switching rates. For switching-supply rectifiers reach for a "
        "Schottky (1N5817) or a fast-recovery part labelled UF400x.",
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
        return f"D1N4001(refdes={self.refdes!r})"
