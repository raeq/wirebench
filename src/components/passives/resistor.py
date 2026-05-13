from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Amps, Ohms, Volts
from framework.registry import register


@register('Resistor')
class Resistor(Part):
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

        r = Resistor(330)
        r(Milliamps(10))                  # Volts(3.3)
    """

    __slots__ = ('_ohms', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'R'
    FOOTPRINT: ClassVar[str | None] = "Resistor_SMD:R_0603_1608Metric"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'axial_2lead',
        'lead_spacing_holes': 3,
    }

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Measure the resistance with your multimeter before "
        "installing.** Set the meter to the Ω (ohms) range, probe one "
        "lead, then the other; the reading should match the value "
        "printed on the part (or decoded from its colour bands) to "
        "within a few percent. A reading of OL (open / infinity) means "
        "the resistor is broken inside; a value wildly different from "
        "what's marked usually means someone has swapped parts in the "
        "bin and you've grabbed the wrong one.",
    )

    # The default KiCad footprint is a 0603 SMD pad — appropriate for
    # PCB export — but hobby use on breadboards / perfboards is
    # overwhelmingly through-hole carbon-film parts on axial leads.
    # Force the substrate flag to THT so the assembly-guide doesn't
    # refuse a perfectly normal breadboard build.
    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        ohms: Annotated[float, Field(gt=0)] | Ohms,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        # Store as Ohms (base-SI) for unit-system consistency.  Ohms(x)
        # canonicalises any input — Kilohms(4.7), Ohms(330), or a plain
        # number — to a base-SI float instance, so repr is canonical
        # regardless of input type.
        self._ohms: Ohms = Ohms(ohms)
        # mandatory=False because the device is structurally inert under
        # graph evaluation — evaluate() is a no-op, so wiring the
        # terminals is not a *simulation* requirement.  In a real
        # circuit both terminals must of course be connected; that is a
        # hardware-design constraint the framework does not enforce
        # because it cannot meaningfully act on it.
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def ohms(self) -> Ohms:
        return self._ohms

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        # Current through a resistor cannot be derived from terminal
        # voltages alone, so a wired resistor is opaque under graph
        # evaluation.  Use __call__ directly when the current is known.
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, current: float | Amps) -> Volts:
        # Calculator, not actuator: returns Volts; does not touch ports.
        # Deliberately skips _assert_no_inputs_wired — there's no port
        # write, so calling a wired resistor cannot overwrite anything.
        # Every other __call__ in the codebase guards; this one doesn't,
        # by design.
        #
        # `current * self._ohms` lets the unit machinery resolve the
        # conversion: every _Unit subclass stores its value in base SI,
        # and float's __mul__ returns a plain float in that base, so
        # Volts(...) wraps the answer correctly whether `current` came
        # in as Amps, Milliamps, or a plain number. Avoid float(current)
        # — it would still work today (Amps._SCALE == 1.0) but masks
        # the unit pathway and would silently break if the unit machinery
        # ever stops storing values in base SI.
        return Volts(current * self._ohms)

    def __str__(self) -> str:
        return f"{float(self._ohms)} Ω"

    def __repr__(self) -> str:
        return f"Resistor(ohms={float(self._ohms)!r}, refdes={self.refdes!r})"
