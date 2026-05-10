from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog


class Resistor(FactorNode):
    """Ideal resistor. Ohm's law: V = I × R.

    Drive port 'i' with current in amps; read the resulting voltage in volts
    from port 'v'.  Real resistors are bidirectional — current may flow either
    way — but this model fixes the direction: current enters 'i', and the
    voltage drop V = I × R appears at 'v'.  When building a real circuit,
    always add a current-limiting resistor in series with any LED or other
    current-sensitive load.
    """

    __slots__ = ['_ohms', '_ports']

    def __init__(self, ohms, domain: GroundDomain = ELECTRICAL) -> None:
        self._ohms = ohms
        self._ports = {
            'i': Port('i', Direction.IN,  domain, mandatory=True,  signal_type=Analog),
            'v': Port('v', Direction.OUT, domain, mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict:
        return self._ports

    def _evaluate(self) -> None:
        current = self._ports['i'].value
        if current is not None:
            self._ports['v'].drive(current * self._ohms)   # V = I × R

    def __call__(self, current):
        self._ports['i'].drive(current)
        self._evaluate()
        return self._ports['v'].value

    def __str__(self) -> str:
        return f"{self._ohms} Ω"

    def __repr__(self) -> str:
        return f"Resistor(ohms={self._ohms!r})"
