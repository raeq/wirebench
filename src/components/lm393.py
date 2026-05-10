from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class LM393(FactorNode):
    __slots__ = ['_vref', '_ref_on_plus', '_ports']

    def __init__(self, vref, ref_on_plus: bool = True, domain: GroundDomain = ELECTRICAL) -> None:
        self._vref = vref
        self._ref_on_plus = ref_on_plus  # True: Vref on V+, sensor on V−
        self._ports = {
            'v_plus':  Port('v_plus',  Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'v_minus': Port('v_minus', Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'out':     Port('out',     Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        vp = self._ports['v_plus'].value
        vm = self._ports['v_minus'].value
        if vp is not None and vm is not None:
            self._ports['out'].drive(vp > vm)
        else:
            self._ports['out'].drive(None)

    def __call__(self, sensor):
        if self._ref_on_plus:
            self._ports['v_plus'].drive(self._vref)
            self._ports['v_minus'].drive(sensor)
        else:
            self._ports['v_plus'].drive(sensor)
            self._ports['v_minus'].drive(self._vref)
        self._evaluate()
        return self._ports['out'].value

    def __str__(self) -> str:
        return f"{'<' if self._ref_on_plus else '>'} {self._vref}"

    def __repr__(self) -> str:
        return f"LM393(vref={self._vref!r}, ref_on_plus={self._ref_on_plus})"
