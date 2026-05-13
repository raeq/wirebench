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

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The banded end is the cathode (−).** Reverse-installing a "
        "rectifier silently blocks current under normal bias; on a "
        "transformer secondary it conducts through reverse breakdown — "
        "which often pops the diode and trips the fuse.",
        "**1N4001 is rated 50 V reverse / 1 A average.** For mains-derived "
        "rectifiers use the 1N4007 (1000 V) — transformer-secondary "
        "transients routinely peak well above nominal RMS, and a 1N4001 "
        "in a mains rectifier is one ringing event away from failure.",
        "**Slow recovery (~2 µs).** Fine for 50/60 Hz mains rectification; "
        "wrong choice for high-frequency switching supplies — use a "
        "Schottky (1N5817) or a fast-recovery diode there.",
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
