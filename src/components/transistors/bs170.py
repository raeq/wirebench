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

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Test for an intact gate oxide and a working body diode** — "
        "same procedure as for a 2N7000, but mind the BS170's "
        "*mirrored* pinout (D-G-S from the flat side, not S-G-D). "
        "Discharge yourself first, then in diode-test mode: gate to "
        "source should read OL both directions (continuity here means "
        "ESD has zapped the part). Drain to source should read ~0.6 V "
        "in one direction (body diode) and OL in the other.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Touch a grounded metal surface before picking up the BS170, "
        "every time.** MOSFETs are static-sensitive — a static spark "
        "too small to feel can damage the gate insulator silently. The "
        "part still looks fine afterwards but won't switch correctly, "
        "and you'll spend an hour blaming your wiring. Keep new "
        "MOSFETs in their conductive foam until you install them.",
        "**The BS170 has the *opposite* pinout from the otherwise-"
        "similar 2N7000.** Hold the part flat-side towards you, leads "
        "down — the BS170's pins are Drain, Gate, Source from left to "
        "right (the 2N7000 is Source, Gate, Drain). Swap one for the "
        "other without re-checking the pinout and the internal body "
        "diode lands across your supply, shorting the rail.",
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
