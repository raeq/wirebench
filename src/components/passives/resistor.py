from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Analog
from framework.units import Amps, Ohms, Volts


class Resistor(FactorNode):
    """Ideal resistor. Ohm's law: V = I × R.

    A real resistor is passive: both terminals are voltage nodes; the
    current through the device is determined by the rest of the circuit.
    A voltage-only simulator cannot solve for that current, so a wired
    resistor is opaque under graph evaluation — `evaluate()` is a
    no-op.

    `__call__(current)` is a sizing calculator, not a signal interface:
    given a known current through the resistor, return the resulting
    voltage drop.  It does not write to the terminal ports — there is
    no node value that "the drop" corresponds to (a drop is a delta
    between t1 and t2, not a value at either).

        Resistor(330)                     # 330 Ω
        Resistor(Ohms(330))               # same, explicit units
        Resistor(Kilohms(4.7))            # 4700 Ω — pull-up size
        Resistor(330)(Milliamps(10))      # Volts(3.3)
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
        # Current through a resistor cannot be derived from terminal
        # voltages alone, so a wired resistor is opaque under graph
        # evaluation.  Use __call__ directly when the current is known.
        pass

    def __call__(self, current: float | Amps) -> Volts:
        # Calculator, not actuator: returns Volts; does not touch ports.
        # Deliberately skips _assert_no_inputs_wired — there's no port
        # write, so calling a wired resistor cannot overwrite anything.
        # Every other __call__ in the codebase guards; this one doesn't,
        # by design.
        return Volts(float(current) * self._ohms)

    def __str__(self) -> str:
        return f"{self._ohms} Ω"

    def __repr__(self) -> str:
        return f"Resistor(ohms={self._ohms!r})"
