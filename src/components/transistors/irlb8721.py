from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import MOSFET


@register('IRLB8721')
class IRLB8721(MOSFET):
    """Logic-level N-channel power MOSFET (62 A, 30 V).

    Black-box package model: terminals expose `d`, `g`, `s` ports;
    no behavioural model.  TO-220AB footprint, front view: pin 1=G,
    pin 2=D (= tab), pin 3=S.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'g': 1, 'd': 2, 's': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**A 3.3 V or 5 V MCU pin drives this FET fully on, directly — "
        "no gate driver chip needed for slow switching.** That's what "
        "'logic-level' means in the part name. (For the curious: the "
        "gate threshold is around 1.8 V, well below typical logic "
        "HIGH.) For PWM faster than ~10 kHz, add a ~100 Ω gate "
        "resistor in series with the MCU pin to slow the edges and "
        "prevent gate ringing.",
        "**The metal tab on a TO-220 is electrically connected to the "
        "drain — treat it as a live wire.** Bolting the tab to a "
        "grounded heatsink directly shorts drain to ground. Use an "
        "insulating shoulder washer plus a thermal pad if the heatsink "
        "is grounded or shared with another part; isolated-tab "
        "variants exist for builds where this matters.",
        "**Add a 10 kΩ resistor between the gate and ground.** Without "
        "it, when the MCU resets or boots up the gate is briefly "
        "floating, and stray charge can turn the FET on unexpectedly — "
        "momentarily energising whatever is on the drain (motor, "
        "lamp, solenoid). The pull-down resistor holds the gate at a "
        "known LOW state until the MCU drives it.",
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
        return f"IRLB8721(refdes={self.refdes!r})"
