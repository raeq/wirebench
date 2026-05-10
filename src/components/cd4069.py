from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from .inverter import Inverter


class CD4069(Circuit):
    """Texas Instruments CD4069UB — hex unbuffered inverter.

    Six independent NOT gates in a single 14-pin package.
    Inputs: a_1–a_6.  Outputs: y_1–y_6.  Each y_i = NOT(a_i).

    Supply voltage: 3 V – 18 V.  Propagation delay: ~30 ns at 5 V.

    The 'UB' suffix means unbuffered — one inversion stage, not three.
    This makes each gate usable as a linear amplifier or oscillator element
    when biased in the transition region, unlike the SN74HC04 which is
    hard-switched.  For pure logic inversion the two parts are equivalent.

    __call__(*inputs) accepts up to 6 logic values and returns a 6-tuple
    of inverted outputs.  Unspecified channels default to LOW input
    (output HIGH).
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
            raise ValueError(f"CD4069 has {self.CHANNELS} channels; got {len(inputs)} inputs")
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
        return 'CD4069()'
