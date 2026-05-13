from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N4148')
class D1N4148(Diode):
    """1N4148 — fast signal switching diode (100 V / 200 mA, DO-35).

    Black-box package model: `anode` and `cathode` ports; no behavioural
    model.  Forward voltage ~0.7 V at 10 mA, reverse recovery ~4 ns.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The black band marks the cathode (the − end).** Match the "
        "band to the bar in the schematic symbol — they're the same "
        "thing. Install it backwards and under normal bias the diode "
        "blocks current the wrong way (your circuit silently does "
        "nothing); under reverse bias it conducts and shorts whatever "
        "the diode was meant to protect.",
        "**Use the 1N4148 for small signal jobs — not for power.** "
        "It's rated for 200 mA average and 1 A peak, which suits "
        "logic-level steering, voltage clamping, level-shifting, and "
        "high-speed switching. It's the wrong choice for rectifying "
        "mains-derived AC or absorbing motor flyback current; reach "
        "for a 1N4001 or 1N4007 there.",
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
        return f"D1N4148(refdes={self.refdes!r})"
