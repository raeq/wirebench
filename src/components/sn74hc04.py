from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class SN74HC04(FactorNode):
    """Texas Instruments SN74HC04 — hex inverting buffer.

    Six independent NOT gates in a single 14-pin package.
    Inputs: A1–A6.  Outputs: Y1–Y6.  Each Yi = NOT(Ai).

    Supply voltage: 2 V – 6 V.  Typical propagation delay: 7 ns at 5 V.
    All six gates share Vcc and GND pins; no per-gate power connection.

    __call__ accepts up to 6 logic values (one per channel in order) and
    returns a 6-tuple of inverted outputs.  Unspecified channels default to
    LOW input (output HIGH).
    """

    __slots__ = ['_ports']

    CHANNELS: int = 6

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            **{f'a{i+1}': Port(f'a{i+1}', Direction.IN,  domain, mandatory=False, signal_type=Digital)
               for i in range(self.CHANNELS)},
            **{f'y{i+1}': Port(f'y{i+1}', Direction.OUT, domain, mandatory=False, signal_type=Digital)
               for i in range(self.CHANNELS)},
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        for i in range(self.CHANNELS):
            v = self._ports[f'a{i+1}'].value
            self._ports[f'y{i+1}'].drive(None if v is None else not bool(Digital(v)))

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"SN74HC04 has {self.CHANNELS} channels; got {len(inputs)} inputs")
        for i, v in enumerate(inputs):
            self._ports[f'a{i+1}'].drive(v)
        for i in range(len(inputs), self.CHANNELS):
            self._ports[f'a{i+1}'].drive(False)
        self._evaluate()
        return tuple(self._ports[f'y{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._ports[f"y{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        return 'SN74HC04()'
