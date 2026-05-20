from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Ohms
from framework.registry import register


@register('Speaker')
class Speaker(Part):
    """Low-impedance moving-coil loudspeaker.

    A real speaker presents an impedance that varies with frequency
    (it's an inductor with a tiny series resistance and a self-
    resonance peak), but for topology validation we treat it as a
    fixed-impedance Analog load between two terminals.  Common
    hobby-bench values are 4 Ω, 8 Ω, 16 Ω, and 32 Ω (the last is
    typical of small piezo speakers); the constructor takes any
    positive value.

    The two terminals are not polarised on the framework's level
    (acoustically inverted phase is a real concern, but doesn't
    affect topology).  The standard pin-number convention follows
    `Resistor` (t1 → 1, t2 → 2) so the breadboard renderer treats
    it as a generic 2-lead axial load.

        Speaker(8)                       # 8 Ω, default
        Speaker(Ohms(32))                # 32 Ω piezo earpiece
    """

    __slots__ = ('_impedance_ohms', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'LS'
    FOOTPRINT: ClassVar[str | None] = "Buzzer_Beeper:Speaker_Mallory_M9CP-916H_15mm"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'radial_2lead',
        'lead_spacing_holes': 2,
    }

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('impedance_ohms',)

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Measure the speaker's DC resistance with your multimeter.** "
        "Set the meter to the Ω range, probe across the two leads — a "
        "healthy moving-coil speaker reads slightly *less* than its "
        "nominal impedance (an '8 Ω speaker' typically reads around "
        "6.5 Ω DC; the difference is reactive at the rated audio "
        "frequency).  A reading of OL means the voice coil has burnt "
        "out; a reading at 0 Ω means it's shorted.  Touch the leads "
        "to a 1.5 V cell briefly — a working speaker emits a faint "
        "click as the cone moves and the DC current sets up.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Don't drive a speaker directly from a CMOS output — the "
        "chip can't source enough current.** A typical 4xxx-series "
        "or 74HC output is good for about 5 mA; a small speaker "
        "wants tens of milliamps to be audible.  Buffer the output "
        "with an NPN emitter-follower or a dedicated audio chip like "
        "the LM386, or use a piezo transducer (which is essentially "
        "a capacitive load that needs only a fraction of a milliamp "
        "of drive current).",
        "**AC-couple the speaker to any DC-biased signal stage.** "
        "The 555's output sits at half-supply on average; wiring it "
        "directly to a speaker means a continuous DC current through "
        "the voice coil, which heats the speaker and shifts the cone "
        "off centre (eventually damaging it).  Add a series capacitor "
        "(10–100 µF electrolytic for hobby work) so only the AC swing "
        "reaches the coil.  This is *the* most common 555-astable / "
        "speaker mistake.",
    )

    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        impedance_ohms: Annotated[float, Field(gt=0)] | Ohms = Ohms(8.0),
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._impedance_ohms: Ohms = Ohms(impedance_ohms)
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def impedance_ohms(self) -> Ohms:
        return self._impedance_ohms

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> Ohms:
        return self._impedance_ohms

    def __str__(self) -> str:
        return f"Speaker: {float(self._impedance_ohms)} Ω"

    def __repr__(self) -> str:
        return (f"Speaker(impedance_ohms={float(self._impedance_ohms)!r}, "
                f"refdes={self.refdes!r})")
