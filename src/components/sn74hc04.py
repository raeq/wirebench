from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class SN74HC04(FactorNode):
    """Texas Instruments SN74HC04 — hex inverting buffer.

    Six independent buffered NOT gates in a single 14-pin package.
    Inputs: a_1–a_6.  Outputs: y_1–y_6.  Each y_i = NOT(a_i).

    Supply voltage: 2 V – 6 V.  Typical propagation delay: 7 ns at 5 V.
    All six gates share Vcc and GND pins; no per-gate power connection.

    The SN74HC04 is buffered (three inversion stages internally), so it
    is a hard-switched logic part — unlike the CD4069UB, which is
    unbuffered and usable in linear/oscillator modes.

    __call__(*inputs) accepts up to 6 logic values and returns a 6-tuple
    of inverted outputs.  Unspecified channels default to LOW input
    (output HIGH).  In a real circuit unused inputs must always be tied
    to GND or Vcc — never left floating.
    """

    __slots__ = ['_ports']

    CHANNELS: int = 6

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            **{f'a_{i+1}': Port(f'a_{i+1}', Direction.IN,  domain, mandatory=False, signal_type=Digital)
               for i in range(self.CHANNELS)},
            **{f'y_{i+1}': Port(f'y_{i+1}', Direction.OUT, domain, mandatory=False, signal_type=Digital)
               for i in range(self.CHANNELS)},
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def evaluate(self) -> None:
        for i in range(self.CHANNELS):
            v = self._ports[f'a_{i+1}'].value
            self._ports[f'y_{i+1}'].drive(None if v is None else not bool(Digital(v)))

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"SN74HC04 has {self.CHANNELS} channels; got {len(inputs)} inputs")
        for i, v in enumerate(inputs):
            self._ports[f'a_{i+1}'].drive(v)
        for i in range(len(inputs), self.CHANNELS):
            self._ports[f'a_{i+1}'].drive(False)
        self.evaluate()
        return tuple(self._ports[f'y_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._ports[f"y_{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        return 'SN74HC04()'
