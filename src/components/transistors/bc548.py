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

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Test as 'two diodes back-to-back sharing the base'.** Put "
        "the red probe on the base (middle pin) and touch the black "
        "probe to each of the other two pins in turn — both should "
        "read about 0.6 V forward (base-to-emitter, base-to-collector "
        "in forward bias). Reverse: red on one of the other pins, "
        "black on the base — both readings should be OL. Any 0 V or "
        "unexpected OL means the junction is damaged. (Mind the "
        "European C-B-E pinout: looking at the flat side with the "
        "leads down, the *middle* pin is the base for the BC548 the "
        "same as for the 2N3904, but the outer pins are swapped.)",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Hold the BC548 with the flat side facing you, leads pointing "
        "down — the pins are then Collector, Base, Emitter from left "
        "to right.** This is the European pinout (the whole BC54x "
        "family). The Americans wired their TO-92 parts in the mirror "
        "order — a 2N3904 or 2N2222 in the same package has the pins "
        "in *reversed* order: E, B, C from left to right. Swapping a "
        "BC548 for a 2N3904 in a hurry without rotating the part puts "
        "the emitter where the collector should be; nothing visibly "
        "fails, the circuit just stops working.",
        "**Always put a resistor in series with the base when driving "
        "from a logic pin.** The base-emitter junction is a diode; "
        "wired directly to a 5 V MCU pin it draws whatever current the "
        "pin can supply — which is more than the BC548's base can "
        "handle, and the part cooks. A 1 kΩ resistor in series limits "
        "base current to ~4 mA, plenty for switching a small load.",
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
