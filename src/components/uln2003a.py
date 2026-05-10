from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog, Digital


class ULN2003A(FactorNode):
    """Seven-channel NPN Darlington transistor array (TI ULN2003A).

    Each channel: 2.7 kΩ series input resistor driving an NPN Darlington pair.
    Output is open-collector with an implied external pull-up resistor.

    Output pin voltage (what this model reports):
      HIGH (True)  — input ≤ V_THRESHOLD: transistor off, pull-up holds pin high
      LOW  (False) — input > V_THRESHOLD: transistor conducting, pin pulled to near GND

    Real-world notes for builders
    ------------------------------
    V_CE_SAT ≈ 0.9 V: when the transistor is conducting the output is NOT a
    clean 0 V — it sits at ~0.9 V.  This model outputs a logical LOW (False)
    for simplicity, but account for V_CE_SAT when sizing load resistors or
    checking logic-level compatibility of downstream inputs.

    I_OUT_MAX = 500 mA per channel.  Each channel also needs a pull-up resistor
    to Vcc on the COM pin; omitting it leaves the output floating when the
    transistor is off.
    """

    __slots__ = ['_out', '_ports']

    CHANNELS:    int   = 7
    V_THRESHOLD: float = 1.0   # V — minimum input voltage to turn on a channel
    I_OUT_MAX:   float = 0.500 # A — maximum sink current per channel

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._out: tuple[bool, ...] = (True,) * self.CHANNELS
        self._ports = {
            **{f'in_{i+1}':  Port(f'in_{i+1}',  Direction.IN,  domain, mandatory=False, signal_type=Analog)  for i in range(self.CHANNELS)},
            **{f'out_{i+1}': Port(f'out_{i+1}', Direction.OUT, domain, mandatory=False, signal_type=Digital) for i in range(self.CHANNELS)},
        }

    @property
    def ports(self) -> dict:
        return self._ports

    @property
    def out(self) -> tuple[bool, ...]:
        """Output pin voltages as a tuple: True = HIGH, False = LOW."""
        return self._out

    @property
    def state(self) -> tuple[bool, ...]:
        """Alias for .out — same tuple of output pin voltages."""
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
        return f'ULN2003A(state={self._out})'
