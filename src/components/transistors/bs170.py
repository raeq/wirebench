from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import MOSFET


@register('BS170')
class BS170(MOSFET):
    """N-channel enhancement-mode MOSFET, small-signal (500 mA, 60 V).

    Black-box package model: terminals expose `d`, `g`, `s` ports;
    no behavioural model.  TO-92 footprint, D-G-S pinout from the
    flat side (mirrored relative to 2N7000).
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'d': 1, 'g': 2, 's': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**MOSFETs are static-sensitive.** Touch the bench frame or use "
        "an ESD strap before handling. The gate-source oxide is thin and "
        "an electrostatic discharge punches through it silently — the "
        "part still looks fine, but it won't switch.",
        "**The BS170 is the 2N7000's mirror twin** (D-G-S vs S-G-D, flat "
        "side facing you, leads down). If you swap one for the other "
        "without re-checking the pinout, drain and source get reversed "
        "— the body diode conducts and the FET won't switch off.",
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
        return f"BS170(refdes={self.refdes!r})"
