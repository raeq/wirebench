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
        "**Touch a grounded metal surface before picking up a MOSFET, "
        "every time.** MOSFETs are static-sensitive in a way bipolar "
        "transistors aren't — a tiny spark you can't feel (under "
        "100 V from walking across a carpet) punches through the gate "
        "insulator and damages the part silently. The transistor still "
        "looks fine after the zap; it just won't switch correctly, and "
        "you'll spend an hour blaming your wiring. Keep new MOSFETs "
        "in their conductive foam until you install them.",
        "**Hold the 2N7000 flat-side towards you, leads down — the pins "
        "are Source, Gate, Drain from left to right.** This is easy to "
        "mix up with a BJT in the same TO-92 package (which is "
        "E-B-C). Wire an N-MOSFET as if it were an NPN and the chip's "
        "internal body diode ends up across your supply, shorting the "
        "rail.",
        "**This is a logic-level MOSFET — it turns on with a 5 V gate "
        "signal.** A 5 V MCU pin drives it fully into conduction. At "
        "3.3 V it still conducts but with higher resistance (and so "
        "more heat) — for low-side switching from a 3.3 V MCU at "
        "meaningful currents, prefer a true logic-level FET like the "
        "IRLB8721 instead. (Technically: V_GS(th) is 1–3 V, "
        "R_DS(on) is spec'd at 4.5 V gate drive.)",
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
