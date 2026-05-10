from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from .inverter import Inverter


class SN74HC04(Circuit):
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
    (output HIGH), matching the behaviour of an undriven CMOS input
    pulled to ground externally.
    """

    __slots__ = ['_gates']

    CHANNELS: int = 6

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._gates = tuple(Inverter(domain) for _ in range(self.CHANNELS))
        inputs  = {f'a_{i+1}': g.ports['a'] for i, g in enumerate(self._gates)}
        outputs = {f'y_{i+1}': g.ports['y'] for i, g in enumerate(self._gates)}
        super().__init__(
            factor_nodes=list(self._gates),
            inputs=inputs,
            outputs=outputs,
        )

    def __call__(self, *inputs) -> tuple:
        if len(inputs) > self.CHANNELS:
            raise ValueError(f"SN74HC04 has {self.CHANNELS} channels; got {len(inputs)} inputs")
        for i in range(self.CHANNELS):
            v = inputs[i] if i < len(inputs) else False
            self._inputs[f'a_{i+1}'].drive(v)
        self._evaluate()
        return tuple(self._outputs[f'y_{i+1}'].value for i in range(self.CHANNELS))

    def __str__(self) -> str:
        return ' '.join(
            f'G{i+1}:{"H" if self._outputs[f"y_{i+1}"].value else "L"}'
            for i in range(self.CHANNELS)
        )

    def __repr__(self) -> str:
        return 'SN74HC04()'
