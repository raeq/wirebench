from framework.circuit import Circuit
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital
from framework.wire import wire
from components.concepts.nor_latch import NORLatch
from components.concepts.tristate_buffer import TriStateBuffer


class CD4043(Circuit):
    """Texas Instruments CD4043B — quad NOR-based RS latch with tri-state outputs.

    Four independent NOR SR latches in one 16-pin CMOS package, sharing
    a single OE (output-enable) pin.

    Pins
    ----
    s_1, r_1 .. s_4, r_4         — set/reset inputs for each latch
    q_1, q_1_bar .. q_4, q_4_bar — outputs (tri-stated when OE=LOW)
    oe                           — chip-level output enable (active HIGH)

    OE behaviour
    ------------
    OE=1 — Q and /Q reflect each latch's state (normal operation).
    OE=0 — Q and /Q forced to high-impedance (None); downstream
            components see no signal.  Use this to share a bus with
            multiple chips.

    Internally each latch core is a NORLatch.  Its q/q_bar feed two
    TriStateBuffer cells whose enable inputs are all driven from the
    single chip OE pin — the same topology as the real silicon.

    If OE is left undriven the chip defaults to enabled.  In a real
    circuit OE must always be explicitly tied to VDD or a control
    signal — never left floating.
    """

    __slots__ = ['_latches', '_buf_q', '_buf_q_bar']

    CHANNELS: int = 4

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._latches   = tuple(NORLatch(domain)       for _ in range(self.CHANNELS))
        self._buf_q     = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))
        self._buf_q_bar = tuple(TriStateBuffer(domain) for _ in range(self.CHANNELS))

        for latch, bq, bqb in zip(self._latches, self._buf_q, self._buf_q_bar):
            wire(latch.ports['q'],     bq.ports['a'])
            wire(latch.ports['q_bar'], bqb.ports['a'])

        oe_pin = Port('oe', Direction.IN, domain, mandatory=False, signal_type=Digital)

        inputs  = {'oe': oe_pin}
        outputs = {}
        for i, (latch, bq, bqb) in enumerate(
            zip(self._latches, self._buf_q, self._buf_q_bar), start=1
        ):
            inputs[f's_{i}']      = latch.ports['s']
            inputs[f'r_{i}']      = latch.ports['r']
            outputs[f'q_{i}']     = bq.ports['y']
            outputs[f'q_{i}_bar'] = bqb.ports['y']

        factor_nodes = list(self._latches) + list(self._buf_q) + list(self._buf_q_bar)
        super().__init__(
            factor_nodes=factor_nodes,
            inputs=inputs,
            outputs=outputs,
        )

    def _evaluate(self) -> None:
        # Fan OE out to every tri-state buffer's enable. Undriven OE → enabled.
        oe_val = self._inputs['oe'].value
        oe_effective = True if oe_val is None else bool(Digital(oe_val))
        for buf in (*self._buf_q, *self._buf_q_bar):
            buf.ports['oe'].drive(oe_effective)
        super()._evaluate()

    def __call__(
        self,
        s_1=False, r_1=False,
        s_2=False, r_2=False,
        s_3=False, r_3=False,
        s_4=False, r_4=False,
        oe=True,
    ) -> tuple:
        sr = ((s_1, r_1), (s_2, r_2), (s_3, r_3), (s_4, r_4))
        for i, (s, r) in enumerate(sr, start=1):
            self._inputs[f's_{i}'].drive(s)
            self._inputs[f'r_{i}'].drive(r)
        self._inputs['oe'].drive(oe)
        self._evaluate()
        return tuple(
            (self._outputs[f'q_{i}'].value, self._outputs[f'q_{i}_bar'].value)
            for i in range(1, self.CHANNELS + 1)
        )

    def __repr__(self) -> str:
        latches = ', '.join(str(l._q) for l in self._latches)
        return f"CD4043(q=({latches}))"
