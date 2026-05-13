from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import MOSFET


@register('Q2N7000')
class Q2N7000(MOSFET):
    """N-channel enhancement-mode MOSFET, small-signal (200 mA, 60 V).

    Black-box package model: terminals expose `d`, `g`, `s` ports;
    no behavioural model.  TO-92 footprint, S-G-D pinout from the
    flat side (datasheet pins 1=S, 2=G, 3=D).
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'s': 1, 'g': 2, 'd': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**MOSFETs are static-sensitive.** Touch the bench frame or use "
        "an ESD strap before handling. A discharge through the gate-source "
        "oxide destroys the transistor silently — it still looks fine, it "
        "just doesn't switch any more. Leave the leads shorted with foil "
        "or in conductive foam until you install it.",
        "**TO-92 pinout, flat side facing you, leads down: S-G-D.** Easy "
        "to confuse with a BJT in the same package (E-B-C). Mis-installing "
        "an N-MOSFET as if it were an NPN puts the body diode across the "
        "supply and shorts your rail.",
        "**The 2N7000 is a logic-level part** (V_GS(th) ≈ 1–3 V), so 5 V "
        "drives it on hard. At 3.3 V it conducts but with higher R_DS(on); "
        "use a true logic-level FET (like the IRLB8721) for low-side "
        "switching from a 3.3 V MCU at meaningful currents.",
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
        return f"Q2N7000(refdes={self.refdes!r})"
