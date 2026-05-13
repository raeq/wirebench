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

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Diode-test the base-emitter junction — it should read about "
        "1.4 V, not the usual 0.6 V.** That doubled voltage is the "
        "signature of a Darlington (two BJTs in cascade share one "
        "base terminal). TO-220 pinout: pin 1 = Base, pin 2 = Collector, "
        "pin 3 = Emitter. Put red on base, black on emitter: ~1.4 V. "
        "Red on base, black on collector: ~0.6 V (only one junction "
        "this way). Reverse both: OL. A base-emitter reading of only "
        "0.6 V means you've grabbed a regular BJT by mistake.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The TIP120 needs about 1.4 V on its base to turn on — twice "
        "as much as an ordinary BJT.** That's because a Darlington is "
        "two BJTs cascaded inside one package. A pull-up resistor that "
        "would have switched a 2N3904 cleanly may leave the TIP120 "
        "stuck halfway on, dissipating heat. Size the base resistor "
        "for I_base ≈ I_load / 1000 (the Darlington's gain is roughly "
        "1000) and confirm the base voltage clears 1.4 V.",
        "**This part dissipates a lot of heat when switching.** A "
        "Darlington drops about 1 V across its collector-emitter "
        "junction when fully 'on', so at 1 A of load current the part "
        "dissipates 1 W — heat you can feel with a finger. A modern "
        "logic-level MOSFET (IRLB8721) drops only ~20 mV at the same "
        "current, so dissipates ~20 mW. Use the TIP120 only when you "
        "specifically want the current-gain (like a small motor speed "
        "controller) and don't mind a heatsink.",
        "**Put a diode across any inductive load — coil, relay, motor "
        "— with the band toward the + supply.** A 1N4001 is enough for "
        "relays and solenoids; a Schottky (1N5817) handles faster "
        "loads like motors. Without the flyback diode, the inductive "
        "load's collapsing field kicks the transistor's collector up "
        "to V_supply + 50 to 200 V on switch-off, blowing the "
        "transistor every time.",
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
