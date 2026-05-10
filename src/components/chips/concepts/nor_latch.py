from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


class NORLatch(FactorNode):
    """NOR-based SR latch (set-dominant-undefined).

    Inputs:  s (set), r (reset)
    Outputs: q, q_bar (always complementary)

    Behaviour:
      S=1, R=0  →  q := 1
      S=0, R=1  →  q := 0
      S=0, R=0  →  hold previous q
      S=1, R=1  →  forbidden (raises ValueError)

    On power-on q is None — the latch has no defined state until first
    set or reset.

    No output-enable; for tri-state behaviour, place a TriStateBuffer
    between this cell and the chip pin (as the CD4043B package does).
    """

    __slots__ = ('_q', '_ports')

    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._q: bool | None = None
        self._ports = {
            's':     Port('s',     Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'r':     Port('r',     Direction.IN,  domain, mandatory=True,  signal_type=Digital),
            'q':     Port('q',     Direction.OUT, domain, mandatory=False, signal_type=Digital),
            'q_bar': Port('q_bar', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def evaluate(self) -> None:
        s = bool(Digital(self._ports['s'].value))
        r = bool(Digital(self._ports['r'].value))
        if s and r:
            raise ValueError("Invalid: S and R both active")
        if s:
            self._q = True
        elif r:
            self._q = False
        # else: hold

        self._ports['q'].drive(self._q)
        self._ports['q_bar'].drive(None if self._q is None else not self._q)

    def __call__(self, s: bool, r: bool) -> bool | None:
        self._ports['s'].drive(s)
        self._ports['r'].drive(r)
        self.evaluate()
        return self._q

    def __str__(self) -> str:
        return str(self._q)

    def __repr__(self) -> str:
        return f"NORLatch(q={self._q})"
