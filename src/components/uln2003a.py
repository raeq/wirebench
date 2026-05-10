from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class ULN2003A(FactorNode):
    """Seven-channel NPN Darlington transistor array (TI ULN2003A).

    Each channel: 2.7kΩ series input resistor driving an NPN Darlington pair.
    Output is open-collector with implied pull-up. Pin voltage:
      False (LOW)  — input > V_THRESHOLD, transistor conducting, output sinking current
      True  (HIGH) — input ≤ V_THRESHOLD, transistor off, output pulled high
    out and __call__ return output pin voltages, not transistor states.
    """

    __slots__ = ['_out', '_ports']  # _out: tuple of output pin voltages (True=HIGH, False=LOW)

    CHANNELS:    int   = 7
    V_THRESHOLD: float = 1.0   # V  — minimum input voltage to turn on a channel
    V_CE_SAT:    float = 0.9   # V  — collector-emitter saturation voltage when conducting
    I_OUT_MAX:   float = 0.500 # A  — maximum sink current per channel

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._out: tuple[bool, ...] = (True,) * self.CHANNELS
        self._ports = {
            **{f'in_{i+1}':  Port(f'in_{i+1}',  Direction.IN,  domain, mandatory=False, signal_type=Analog) for i in range(self.CHANNELS)},
            **{f'out_{i+1}': Port(f'out_{i+1}', Direction.OUT, domain, mandatory=False, signal_type=Digital)  for i in range(self.CHANNELS)},
        }

    @property
    def ports(self) -> dict:
        return self._ports

    @property
    def out(self) -> tuple[bool, ...]:
        return self._out

    def _evaluate(self) -> None:
        voltages = tuple(
            Analog(self._ports[f'in_{i+1}'].value)
            for i in range(self.CHANNELS)
        )
        # open-collector: conducting pulls pin LOW (False); off leaves pin HIGH (True)
        self._out = tuple(float(v) <= self.V_THRESHOLD for v in voltages)
        for i, high in enumerate(self._out):
            self._ports[f'out_{i+1}'].drive(high)

    def __call__(self, *inputs) -> tuple[bool, ...]:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"ULN2003A has {self.CHANNELS} channels; got {len(inputs)} inputs")
        for i, v in enumerate(inputs):
            self._ports[f'in_{i+1}'].drive(v)
        for i in range(len(inputs), self.CHANNELS):
            self._ports[f'in_{i+1}'].drive(0.0)
        self._evaluate()
        return self._out

    def __str__(self) -> str:
        return ' '.join(f'CH{i+1}:{"HIGH" if s else "LOW"}' for i, s in enumerate(self._out))

    def __repr__(self) -> str:
        return f'ULN2003A(out={self._out})'
