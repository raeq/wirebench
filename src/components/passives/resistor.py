from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog
from framework.units import Ohms


class Resistor(FactorNode):
    """Ideal resistor. Ohm's law: V = I × R.

    A real resistor is a passive 2-terminal device.  Both terminals are
    voltage nodes; current through the device is determined by external
    circuit constraints, which a voltage-only simulator cannot solve.

    `__call__(current)` is the device's signal interface: given a current
    flowing through the resistor (in amps), return the resulting voltage
    drop (in volts).  The drop is also published on the t2 port so that a
    downstream component can read it.

        Resistor(330)               # 330 Ω
        Resistor(Ohms(330))         # same, explicit units
        Resistor(Kilohms(4.7))      # 4700 Ω — use for pull-up resistors
    """

    __slots__ = ('_ohms', '_ports')

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

    def evaluate(self) -> None:
        # Current through a resistor cannot be derived from terminal voltages
        # alone, so a wired resistor is opaque under graph evaluation.  Use
        # __call__ directly when the current is known.
        pass

    def __call__(self, current: float) -> Analog:
        drop = Analog(float(current) * self._ohms)
        self._ports['t2'].drive(drop)
        return drop

    def __str__(self) -> str:
        return f"{self._ohms} Ω"

    def __repr__(self) -> str:
        return f"Resistor(ohms={self._ohms!r})"
