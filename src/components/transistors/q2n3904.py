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
        "**Hold the 2N3904 with the flat side facing you, leads "
        "pointing down — the pins are Emitter, Base, Collector from "
        "left to right.** This is the American JEDEC convention. The "
        "European BC547 / BC548 in the same TO-92 package have the "
        "*opposite* pin order (C, B, E). Drop a BC547 into a 2N3904's "
        "spot without rotating it 180° and emitter ends up where "
        "collector should be — the part still conducts a little, but "
        "the circuit silently doesn't work.",
        "**Always put a resistor in series with the base when driving "
        "from a logic pin.** The base-emitter junction is a forward-"
        "biased diode; wired directly to a 5 V MCU pin it conducts "
        "whatever current the pin can deliver, which exceeds the "
        "transistor's absolute-max base rating and burns it out. "
        "A 1 kΩ resistor limits the base current to about 4 mA — "
        "plenty to switch the transistor fully on for any small "
        "collector load.",
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
