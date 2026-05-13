from typing import ClassVar

from pydantic import validate_call

from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog
from framework.transistor import BJT


@register('TIP120')
class TIP120(BJT):
    """NPN Darlington power transistor (5 A, 60 V).

    Black-box package model: terminals expose `c`, `b`, `e` ports;
    no behavioural model.  TO-220AB footprint, front view: pin 1=B,
    pin 2=C (= tab), pin 3=E.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'Q'
    FOOTPRINT: ClassVar[str | None] = "Package_TO_SOT_THT:TO-220-3_Vertical"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'b': 1, 'c': 2, 'e': 3}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Darlington V_BE is ~1.4 V**, not the usual ~0.7 V — it's two "
        "BJTs in cascade. A pull-up that just barely turned on a single "
        "transistor will leave the TIP120 sitting in its high-loss region. "
        "Size the base resistor for a base current of I_load / 1000 (β ≈ "
        "1000 typical) and confirm V_BE clears 1.4 V.",
        "**Darlingtons saturate at ~1 V V_CE(sat).** That's lossy: at 1 A "
        "the part dissipates 1 W in switching. A logic-level MOSFET "
        "(IRLB8721) dissipates ~50 mW at the same current. Use the Darlington "
        "only when you specifically need its current gain and don't mind "
        "the heat.",
        "**Inductive loads need a flyback diode** from collector to "
        "supply, cathode toward supply. Without it the inductor's collapsing "
        "field kicks the collector to +V_supply + 50–200 V and punctures "
        "the part. A 1N4001 across a relay or solenoid is enough; faster "
        "loads (motors) want a Schottky like the 1N5817.",
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
        return f"TIP120(refdes={self.refdes!r})"
