from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog
from framework.units import Ohms


class Resistor(FactorNode):
    """Ideal resistor. Ohm's law: V = I × R.

    A resistor is symmetric: current may flow either way and the device has
    no causal direction.  Both terminals are bidirectional ports — whichever
    one is driven this evaluation, the other carries the resulting drop.

    Pass resistance as a plain number (ohms) or as an Ohms/Kilohms unit value:

        Resistor(330)               # 330 Ω
        Resistor(Ohms(330))         # same, explicit units
        Resistor(Kilohms(4.7))      # 4700 Ω — use for pull-up resistors
    """

    __slots__ = ['_ohms', '_ports']

    def __init__(self, ohms: float | Ohms, domain: GroundDomain = ELECTRICAL) -> None:
        # Normalise to a plain base-unit float so repr is canonical regardless
        # of input type (Ohms(47), Kilohms(4.7), and 4700 all store as 4700.0).
        self._ohms = float(ohms)
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        v1 = self._ports['t1'].value
        v2 = self._ports['t2'].value
        if v1 is not None and v2 is None:
            self._ports['t2'].drive(v1 * self._ohms)
        elif v2 is not None and v1 is None:
            self._ports['t1'].drive(v2 * self._ohms)
        # both driven or neither → nothing to propagate

    def __call__(self, current):
        # __call__ commits to a t1 → t2 direction for this invocation: clear any
        # value left on t2 by a previous call so _evaluate propagates afresh.
        self._ports['t2']._local_value = None
        self._ports['t1'].drive(current)
        self._evaluate()
        return self._ports['t2'].value

    def __str__(self) -> str:
        return f"{self._ohms} Ω"

    def __repr__(self) -> str:
        return f"Resistor(ohms={self._ohms!r})"
