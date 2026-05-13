from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N4728A')
class D1N4728A(Diode):
    """1N4728A — 1 W Zener voltage reference / regulator at 3.3 V (DO-41).

    Same family as 1N4733A (5.1 V) and 1N4742A (12 V) but at the
    low-voltage end of the series — used in the TIDA-00517 fan
    controller to drop a 24 V rail down to the TMP302's 1.4-3.6 V
    supply window.  Black-box package model: `anode` and `cathode`
    ports; no behavioural model.  V_Z = 3.3 V @ I_ZT = 76 mA;
    P_D = 1 W; tolerance ±5%.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Zeners are installed reverse-biased.** The banded end "
        "(cathode) goes toward the *positive* rail; the regulation "
        "happens through reverse breakdown. Mis-installing one with "
        "the bar to ground turns it into an ordinary forward-biased "
        "diode and the regulation simply doesn't happen.",
        "**A Zener regulator needs a series resistor.** The Zener clamps "
        "voltage but doesn't limit current — without a series R sized "
        "for `(V_in − V_z) / I_load`, the Zener dissipates the entire "
        "supply current as heat and exceeds its 1 W rating in seconds.",
        "**Zener V_Z drifts with temperature.** Below ~5 V the coefficient "
        "is negative; above ~5 V it's positive; ~5.6 V is the sweet spot "
        "where they cancel. The 1N4728A (3.3 V) drifts by several mV/°C — "
        "use a voltage reference (TL431, LM4040) where stability matters.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'anode':   Port('anode',   Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'cathode': Port('cathode', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
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
        return f"D1N4728A(refdes={self.refdes!r})"
