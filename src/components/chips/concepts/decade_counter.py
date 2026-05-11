from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


# Output pin names: q0..q9 for the ten decoded outputs, co for the
# divide-by-ten carry (HIGH for counts 0..4, LOW for counts 5..9).
_Q_NAMES  = tuple(f'q{i}' for i in range(10))
_CO_NAME  = 'co'
_IN_NAMES = ('clk', 'inhibit', 'reset')


class DecadeCounter(FactorNode):
    """Edge-triggered Johnson decade counter cell (CD4017 internals).

    Ten one-hot decoded outputs plus a divide-by-ten carry.  Counting
    advances on the rising edge of `clk`, gated by `inhibit` (active
    HIGH disables counting) and asynchronously cleared by `reset`
    (active HIGH forces count to 0).

    The cell remembers the previous `clk` level in Python state so it
    can detect the rising edge across successive evaluations of the
    enclosing circuit.  A None-valued clock counts as LOW for edge
    purposes — the first non-None HIGH after a None will not register
    as an edge, since there is no prior LOW to rise from.
    """

    __slots__ = ('_ports', '_count', '_prev_clk')

    OUTPUTS: int = 10

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports: dict[str, Port] = {
            'clk':     Port('clk',     Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'inhibit': Port('inhibit', Direction.IN,  domain, mandatory=False, signal_type=Digital),
            'reset':   Port('reset',   Direction.IN,  domain, mandatory=False, signal_type=Digital),
        }
        for name in _Q_NAMES:
            self._ports[name] = Port(name, Direction.OUT, domain,
                                     mandatory=False, signal_type=Digital)
        self._ports[_CO_NAME] = Port(_CO_NAME, Direction.OUT, domain,
                                     mandatory=False, signal_type=Digital)
        self._count: int = 0
        # Power-on clock line is presumed LOW (matches a real CMOS pin
        # held LOW by its pull-down or driven LOW by the previous
        # stage at rest).  This makes the very first tick HIGH the
        # detected rising edge — exactly what an oscillator's first
        # output transition does.
        self._prev_clk: bool = False

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def count(self) -> int:
        return self._count

    def evaluate(self) -> None:
        clk_val = self._ports['clk'].value
        clk     = bool(Digital(clk_val))
        inhibit = bool(Digital(self._ports['inhibit'].value))
        reset   = bool(Digital(self._ports['reset'].value))

        if reset:
            # Asynchronous level-triggered clear.
            self._count = 0
        elif self._prev_clk is False and clk is True and not inhibit:
            # Rising edge while enabled — advance.
            self._count = (self._count + 1) % self.OUTPUTS

        self._prev_clk = clk

        self._drive_outputs()
        # Cycle-limiting feedback (Q_N → RST is the common idiom for
        # constraining the counter to fewer than 10 states): after
        # driving the outputs, our own Q-drive may have just asserted
        # RST through the external wire.  Re-read RST and clamp once
        # more so the reset propagates in the same evaluate() pass
        # instead of leaving a 1-cycle Q_N transient.  Stops after one
        # fixup — if RST stays HIGH after we re-drive Q outputs at 0,
        # the next evaluate() reads it and clamps again, identical to
        # a normal level-triggered reset.
        if bool(Digital(self._ports['reset'].value)) and self._count != 0:
            self._count = 0
            self._drive_outputs()

    def _drive_outputs(self) -> None:
        for i, name in enumerate(_Q_NAMES):
            self._ports[name].drive(i == self._count)
        # Divide-by-ten output: HIGH while count is in the first half
        # of the cycle (0..4), LOW for the second half (5..9).  This is
        # the active phase of CO on a real CD4017.
        self._ports[_CO_NAME].drive(self._count < 5)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self,
                 clk: bool | None,
                 inhibit: bool | None = False,
                 reset: bool | None = False,
                 ) -> int:
        self._assert_no_inputs_wired()
        self._ports['clk'].drive(clk)
        self._ports['inhibit'].drive(inhibit)
        self._ports['reset'].drive(reset)
        self.evaluate()
        return self._count

    def __repr__(self) -> str:
        return f"DecadeCounter(count={self._count})"
