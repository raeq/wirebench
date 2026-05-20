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

    # Typical forward voltage drop at 10 mA, room temperature.  Silicon
    # signal diode — the canonical ~0.7 V figure.
    V_F: ClassVar[float] = 0.7
    V_BREAKDOWN_R: ClassVar[float | None] = None

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Use the multimeter's diode-test mode on a silicon diode "
        "like the 1N4148.** Red probe on the anode (unmarked end), "
        "black probe on the cathode (banded end): the meter reads "
        "about 0.6 V — the diode's forward voltage drop. Swap the "
        "probes around and the meter reads OL: the diode blocks "
        "reverse current. Both directions showing 0.6 V means the "
        "diode is shorted; both showing OL means it's open. The body "
        "of the part should also have '1N4148' printed on it — a "
        "look-alike diode with the wrong markings is a mis-bag.",
    )

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
        return f"D1N4148(refdes={self.refdes!r})"
