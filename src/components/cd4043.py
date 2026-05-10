from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class CD4043(FactorNode):
    """CMOS NOR SR latch with tri-state output (one cell of the TI CD4043B quad).

    OE (output enable, active HIGH):
      OE=1 — Q and /Q reflect the latch state (normal operation).
      OE=0 — Q and /Q are forced to high-impedance (None); downstream
              components see no signal.  Use this to share a bus with
              multiple latches.

    If OE is left unconnected it defaults to HIGH (outputs enabled).
    In a real circuit OE must always be explicitly tied to VDD or a
    control signal — never left floating.
    """

    __slots__ = ['_q', '_ports']

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._q: bool | None = None
        self._ports = {
            's':     Port('s',     Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'r':     Port('r',     Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'oe':    Port('oe',    Direction.IN,  domain, mandatory=False, signal_type=Digital),
            'q':     Port('q',     Direction.OUT, domain, mandatory=False, signal_type=Digital),
            'q_bar': Port('q_bar', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        s = bool(Digital(self._ports['s'].value))
        r = bool(Digital(self._ports['r'].value))
        if s and not r:
            self._q = True
        elif r and not s:
            self._q = False
        elif s and r:
            raise ValueError("Invalid: S and R both active")
        # else: S=0, R=0 → hold

        oe_val = self._ports['oe'].value
        oe = oe_val if oe_val is not None else True  # unconnected → enabled
        if oe:
            self._ports['q'].drive(self._q)
            self._ports['q_bar'].drive(None if self._q is None else not self._q)
        else:
            self._ports['q'].drive(None)      # tri-stated
            self._ports['q_bar'].drive(None)  # tri-stated

    def __call__(self, s: bool, r: bool) -> bool | None:
        self._ports['s'].drive(s)
        self._ports['r'].drive(r)
        self._evaluate()
        return self._q

    def __str__(self) -> str:
        return str(self._q)

    def __repr__(self) -> str:
        return f"CD4043(q={self._q})"
