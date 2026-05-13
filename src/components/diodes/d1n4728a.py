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
        "**Zeners are installed *backwards* compared with an ordinary "
        "diode.** The black band (cathode) goes toward the *positive* "
        "rail, not toward ground. Zeners regulate by deliberately "
        "letting current flow in their reverse-breakdown region — "
        "install one with the band toward ground and it acts like a "
        "regular diode (no regulation happens at all).",
        "**A Zener always needs a series resistor between it and the "
        "supply.** The Zener clamps voltage but it does not limit "
        "current — without a resistor sizing the current, the Zener "
        "passes whatever the supply delivers, overheats, and burns out "
        "in seconds. Pick R = (V_in − V_z) / I_load for the smallest "
        "load you'll have on the regulated rail.",
        "**A 3.3 V Zener like this one drifts noticeably with "
        "temperature** — several mV per °C. Fine for simple voltage "
        "clamping or rough regulation; bad for anything precision. "
        "If you care about stability use a real voltage reference "
        "(TL431, LM4040). (For the curious: the temperature coefficient "
        "flips sign around 5.6 V — below that it's negative, above it's "
        "positive, and a 5.6 V Zener is the most temperature-stable.)",
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
