from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import BJT


@register('Q2N3904')
class Q2N3904(BJT):
    """NPN BJT, general-purpose small-signal (200 mA, 40 V).

    Black-box package model: terminals expose `c`, `b`, `e` ports;
    no behavioural model.  TO-92 footprint, JEDEC EBC pinout from the
    flat side (datasheet pins 1=E, 2=B, 3=C).
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'e': 1, 'b': 2, 'c': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**TO-92 pinout, flat side facing you, leads down: E-B-C.** This "
        "is the American JEDEC convention. European parts like the BC547/"
        "BC548 use the *opposite* C-B-E ordering — swapping a 2N3904 for "
        "a BC547 without rotating it 180° puts emitter where collector "
        "should be. The transistor still conducts, but as a high-loss "
        "common-base stage; nothing visibly fails, just stops working.",
        "**Always include a base resistor.** The base-emitter junction is "
        "a diode; driving it from a 5 V MCU pin without a series resistor "
        "(~1 kΩ for switching) lets the base draw whatever the MCU pin "
        "can source, exceeds the absolute-max base current, and cooks "
        "the transistor.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'c': Port('c', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'b': Port('b', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'e': Port('e', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
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
        return f"Q2N3904(refdes={self.refdes!r})"
