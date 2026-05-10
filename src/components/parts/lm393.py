from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from components.concepts.comparator import Comparator


class LM393(Circuit):
    """Texas Instruments LM393 — dual differential voltage comparator.

    Two independent open-collector comparator cells in an 8-pin package.
    Each cell: output HIGH when V+ exceeds V−.  The cells share Vcc and
    GND but are otherwise independent — different references, polarities,
    and loads per channel.

    Pins
    ----
    v_plus_1, v_minus_1, out_1   — channel 1
    v_plus_2, v_minus_2, out_2   — channel 2

    Real-world note: the LM393 outputs are open-collector and require an
    external pull-up resistor to register a logic HIGH.  This model
    drives a clean digital level for simulation; size the pull-up
    (typically 1–10 kΩ) when building the physical circuit.
    """

    __slots__ = ['_cells']

    CHANNELS: int = 2

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._cells = tuple(Comparator(domain) for _ in range(self.CHANNELS))
        inputs = {}
        outputs = {}
        for i, c in enumerate(self._cells, start=1):
            inputs[f'v_plus_{i}']  = c.ports['v_plus']
            inputs[f'v_minus_{i}'] = c.ports['v_minus']
            outputs[f'out_{i}']    = c.ports['out']
        super().__init__(
            factor_nodes=list(self._cells),
            inputs=inputs,
            outputs=outputs,
        )

    def __call__(self, v_plus_1, v_minus_1, v_plus_2=None, v_minus_2=None) -> tuple:
        self._inputs['v_plus_1'].drive(v_plus_1)
        self._inputs['v_minus_1'].drive(v_minus_1)
        self._inputs['v_plus_2'].drive(v_plus_2)
        self._inputs['v_minus_2'].drive(v_minus_2)
        self._evaluate()
        return (self._outputs['out_1'].value, self._outputs['out_2'].value)

    def __repr__(self) -> str:
        return "LM393()"
