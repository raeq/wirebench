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
        "**Logic-level gate** (V_GS(th) ≈ 1.8 V). A 3.3 V or 5 V MCU pin "
        "drives it on hard — no gate driver needed for slow PWM. For PWM "
        "above ~10 kHz, add a small gate resistor (~100 Ω) and watch the "
        "edges on a scope; gate ringing can damage the part.",
        "**TO-220 tab is connected to the drain.** Tab-to-heatsink "
        "connections need insulating shoulder washers + a thermal pad if "
        "the heatsink is shared or grounded, otherwise the drain shorts "
        "to ground.",
        "**Pull the gate down with a resistor (~10 kΩ to GND).** Without "
        "it, the gate floats during MCU reset and the FET can turn on "
        "unexpectedly — momentarily energising whatever's on the drain.",
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
