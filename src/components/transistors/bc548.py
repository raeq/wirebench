from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import BJT


@register('BC548')
class BC548(BJT):
    """NPN BJT, general-purpose small-signal (100 mA, 30 V).

    Same package and pinout as BC547 (TO-92, European CBE: 1=C, 2=B,
    3=E from the flat side) — the differences are gain bin and
    slightly lower Vce_max.  Black-box package model: terminals
    expose `c`, `b`, `e` ports; no behavioural model.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-92_Inline"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'c': 1, 'b': 2, 'e': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**TO-92 pinout, flat side facing you, leads down: C-B-E.** This "
        "is the European pinout (BC54x family). Don't confuse with the "
        "American 2N3904 / 2N2222 (E-B-C) — those are *mirrored*. Swapping "
        "without rotating 180° puts emitter where collector should be.",
        "**Base resistor is mandatory** when driving from a logic pin: "
        "the B-E junction is a diode and conducts whatever current the "
        "driving stage can supply. Without a ~1 kΩ in series, base "
        "current exceeds the absolute-max rating and cooks the part.",
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
        return f"BC548(refdes={self.refdes!r})"
