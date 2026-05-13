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
        "**Don't drive the IRFZ44N directly from a 3.3 V or 5 V MCU "
        "pin — it won't fully turn on.** The datasheet's impressively "
        "low on-resistance is spec'd at a 10 V gate drive; at 5 V "
        "(let alone 3.3 V) the FET only partly conducts, the chip "
        "dissipates the difference as heat, and your load runs warm "
        "and unpredictable. For MCU-driven loads, reach for a true "
        "logic-level FET (IRLB8721) or add a dedicated gate driver "
        "chip that delivers 10 V.",
        "**The metal tab on a TO-220 is electrically connected to the "
        "drain — treat it as a live wire.** If you bolt the tab to a "
        "grounded heatsink directly, you've shorted drain to ground. "
        "Use an insulating shoulder washer plus a thermal pad between "
        "tab and heatsink, or use isolated-tab variants of the part. "
        "Two FETs on the same heatsink without insulation end up "
        "drain-tied — usually not what you wanted.",
        "**Add a small resistor (~100 Ω) in series with the gate when "
        "switching at audio or PWM frequencies.** The FET's gate has "
        "about 1 nF of capacitance — charging that through a slow "
        "path means the FET spends time half-on during switching, "
        "which dissipates surprising amounts of heat. A 100 Ω gate "
        "resistor (from driver to gate) is the standard fix; for "
        "anything faster than a few kHz consider a dedicated "
        "gate-driver chip.",
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
