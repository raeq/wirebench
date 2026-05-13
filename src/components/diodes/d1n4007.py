from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N4007')
class D1N4007(Diode):
    """1N4007 — 1000 V / 1 A general-purpose silicon rectifier (DO-41).

    Black-box package model: `anode` and `cathode` ports; no behavioural
    model.  V_R max = 1000 V; I_F avg = 1 A; V_F typ ~1.0 V @ 1 A; I_FSM = 30 A.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The black band marks the cathode (− end).** Match the band "
        "to the bar in the schematic symbol; they mean the same thing. "
        "Reverse-installing a rectifier on a transformer secondary is "
        "one of the most reliable ways to pop both the diode and the "
        "fuse in the same switch-on event.",
        "**The 1N4007 is the workhorse mains rectifier and a great "
        "flyback diode for slow inductive loads.** It blocks 1000 V "
        "reverse, conducts 1 A continuous, and costs almost nothing. "
        "Use it for relay coils, solenoids, small motors at audio "
        "frequencies, and any AC rectification at line frequency. "
        "Slow recovery (~2 µs) means it's the wrong choice for "
        "switching power supplies above a few kHz; a Schottky like "
        "the 1N5817 handles those.",
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
        return f"D1N4007(refdes={self.refdes!r})"
