from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import MOSFET


@register('IRFZ44N')
class IRFZ44N(MOSFET):
    """Standard-gate N-channel power MOSFET (49 A, 55 V).

    Black-box package model: terminals expose `d`, `g`, `s` ports;
    no behavioural model.  TO-220AB footprint, front view: pin 1=G,
    pin 2=D (= tab), pin 3=S.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'g': 1, 'd': 2, 's': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The IRFZ44N is not a logic-level FET** (V_GS(th) up to 4 V). "
        "Driving it directly from a 3.3 V or 5 V MCU pin only partially "
        "turns it on — R_DS(on) is much higher than the datasheet number "
        "(which is spec'd at V_GS = 10 V) and the part dissipates heat "
        "instead of switching. For MCU-driven loads, use a true logic-level "
        "FET (IRLB8721) or a gate driver.",
        "**TO-220 tab is connected to the drain.** Bolting the tab to a "
        "heatsink without insulation puts the drain potential on the "
        "heatsink. If two FETs share a heatsink they end up tied "
        "drain-to-drain — use insulating shoulder washers and a thermal pad.",
        "**Power FETs need gate-current at switching edges.** The gate "
        "capacitance is ~1 nF; charging it through a 10 kΩ resistor takes "
        "microseconds. For PWM above a few kHz, drop the gate resistor to "
        "~100 Ω or use a dedicated gate driver — slow edges mean the FET "
        "spends time in its linear region, dissipating heat.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'd': Port('d', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'g': Port('g', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            's': Port('s', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
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
        return f"IRFZ44N(refdes={self.refdes!r})"
