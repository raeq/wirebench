from typing import Any, ClassVar

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Ohms
from framework.registry import register


@register('CrystalEarpiece')
class CrystalEarpiece(Part):
    """High-impedance piezo-crystal earpiece — the iconic transducer
    of the 1920s–1970s crystal radio set.

    A piezo earpiece is essentially a small parallel-plate capacitor
    (~1–10 nF) whose dielectric is a ferroelectric ceramic; an
    audio-band voltage across its terminals bends the crystal and
    radiates sound directly into the ear canal.  At 1 kHz the
    impedance is on the order of tens of kΩ — orders of magnitude
    higher than a moving-coil speaker, which is why a crystal radio
    can drive one from microwatts of detected RF energy.

    Pin numbering follows the standard 2-lead convention (t1 → 1,
    t2 → 2).  The earpiece is not polarised; either lead goes into
    either hole.

        CrystalEarpiece()                # default impedance ~32 kΩ
        CrystalEarpiece(impedance_ohms=Ohms(50_000))
    """

    __slots__ = ('_impedance_ohms', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'LS'
    FOOTPRINT: ClassVar[str | None] = "Buzzer_Beeper:Buzzer_12x9.5RM7.6"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'radial_2lead',
        'lead_spacing_holes': 2,
    }

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('impedance_ohms',)

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Confirm the earpiece is the high-impedance crystal kind, "
        "not a moving-coil headphone.** The DC resistance of a "
        "crystal earpiece is essentially infinite (open circuit on "
        "a multimeter); a moving-coil dynamic earpiece reads a few "
        "ohms to a few hundred ohms.  Crystal earpieces are still "
        "available from radio-restoration suppliers (look for the "
        "old 'crystal earphone' from a 1960s catalogue); modern "
        "piezo buzzers are the same physics in a different case.  "
        "Crystal radios need the high-impedance kind — driving a "
        "low-impedance speaker from a crystal-set detector means no "
        "audible sound.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Don't put a crystal earpiece in your ear at full volume "
        "from a powered amplifier — it will be uncomfortably loud.** "
        "Crystal earpieces are designed for the microwatt outputs of "
        "passive detectors (crystal radios, foxhole receivers).  An "
        "audio-amp output that drives a moving-coil speaker happily "
        "will drive a piezo earpiece to painfully loud levels — and "
        "may damage the crystal itself.  Use a piezo buzzer / "
        "speaker with proper level matching for amplifier outputs.",
        "**The crystal is fragile — the case is rugged but the "
        "transducer element inside is not.** Don't drop the "
        "earpiece, don't apply more than a few volts AC across its "
        "terminals, and don't expose it to temperatures above 60 °C "
        "for any length of time.  The ferroelectric ceramic "
        "depoles permanently above ~150 °C and the part stops "
        "working entirely — an irreversible failure.",
    )

    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        impedance_ohms: float | Ohms = Ohms(32_000.0),
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
        return f"Crystal earpiece: {float(self._impedance_ohms)} Ω"

    def __repr__(self) -> str:
        return (f"CrystalEarpiece("
                f"impedance_ohms={float(self._impedance_ohms)!r}, "
                f"refdes={self.refdes!r})")
