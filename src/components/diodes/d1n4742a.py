from typing import ClassVar

from pydantic import validate_call

from framework.diode import Diode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog


@register('D1N4742A')
class D1N4742A(Diode):
    """1N4742A — 1 W Zener voltage reference / regulator at 12 V (DO-41).

    Black-box package model: `anode` and `cathode` ports; no behavioural
    model.  V_Z = 12 V @ I_ZT = 21 mA; P_D = 1 W; I_ZM ~76 mA; tolerance +/-5%.
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'D'
    FOOTPRINT: ClassVar[str | None] = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

    # Silicon Zener — forward V_F is the standard silicon ~0.7 V; the
    # device's *operating point* is the reverse-breakdown V_Z.
    V_F: ClassVar[float] = 0.7
    V_BREAKDOWN_R: ClassVar[float | None] = 12.0

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            'anode':   Port('anode',   Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            'cathode': Port('cathode', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
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
        return f"D1N4742A(refdes={self.refdes!r})"
