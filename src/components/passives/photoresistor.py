from typing import Annotated, Any, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.units import Ohms
from framework.registry import register


@register('Photoresistor')
class Photoresistor(Part):
    """Cadmium-sulphide light-dependent resistor (LDR / photocell).

    A real LDR is a passive whose resistance falls as incident light
    increases: typical specimens (the cheap ORP12-equivalents still
    on every hobbyist bench) sit in the mega-ohm range in darkness
    and drop to a few hundred ohms in bright sunlight.  Both
    terminals are voltage nodes; the framework treats the device as
    opaque under graph evaluation (same shape as `Resistor`) — its
    illuminated-resistance value is informational for sizing the
    accompanying divider / threshold network.

    The two declared values bracket the device's operating range.  A
    real circuit's threshold sits somewhere between them and the
    divider partner is chosen so the trip point lands at the desired
    light level.

        Photoresistor(dark_ohms=Megohms(1.0), light_ohms=Ohms(500))

    Substrate / mounting: through-hole, axial leads, 5–10 mm round
    package (the classic ORP12 / VT93N2 form factor).

    Pin numbers track the Resistor convention (t1 → 1, t2 → 2) so
    the breadboard renderer treats the cell as a generic axial 2-lead
    part.  The KiCad symbol is `Device:R_Photo`.
    """

    __slots__ = ('_dark_ohms', '_light_ohms', '_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'R'
    FOOTPRINT: ClassVar[str | None] = "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}
    # Round-trip through the generic ExtensionRecord path — no
    # dedicated Pydantic record class for the LDR.  See
    # framework/format_extension.py for the lookup convention; the
    # private `_dark_ohms` / `_light_ohms` slots are read by name.
    # `domain` is not serialised; an LDR is always in the electrical
    # ground domain (the device's photo-effect is between its two
    # terminals — no domain-crossing equivalent).
    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('dark_ohms', 'light_ohms')

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'axial_2lead',
        'lead_spacing_holes': 3,
    }

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Measure the LDR's dark and light resistance with your "
        "multimeter before installing.** Set the meter to the kΩ or "
        "MΩ range, probe across the two leads, then cover the sensor "
        "with your finger — the reading should climb steeply (typical "
        "ORP12 specimens reach 100 kΩ–1 MΩ in shade). Uncover and "
        "shine a torch at it — the reading should fall to a few "
        "hundred ohms or less. A reading that doesn't move with "
        "light has either failed open (always OL) or is the wrong "
        "part. Photocells are not polarised; either lead goes in "
        "either hole.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**The LDR's resistance varies over orders of magnitude — "
        "pick the divider resistor to put the threshold where the "
        "scene's light level changes.** Size R_divider ≈ "
        "geometric mean of (R_LDR_dark, R_LDR_light): for an ORP12 "
        "this is roughly 10 kΩ for indoor twilight. Wrong divider "
        "values mean the trip point lives in the wrong part of the "
        "scene's range and the alarm / switch either fires "
        "continuously or never fires.",
        "**LDRs are slow.** Response time at full transitions is "
        "tens to hundreds of milliseconds (CdS is a slow photoeffect). "
        "Useful for ambient-light sensing, dawn/dusk switching, and "
        "burglar-alarm tripwires; useless for anything that needs to "
        "follow a flicker faster than ~10 Hz. Reach for a photodiode "
        "(BPW34, BPW21) or phototransistor (BPW77, BPX38) when you "
        "need optical bandwidth above audio frequencies.",
        "**Modern CdS-cell ban in the EU / RoHS regions** — newer "
        "designs reach for a photodiode + transimpedance amplifier "
        "instead. For hobby use and educational replication of "
        "vintage projects an ORP12 / GL5528 / VT93N2 is still the "
        "drop-in part; treat the bench supply as one-off and don't "
        "expect to find these in a current production parts catalogue.",
    )

    @property
    def is_through_hole(self) -> bool:
        return True

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        dark_ohms:  Annotated[float, Field(gt=0)] | Ohms,
        light_ohms: Annotated[float, Field(gt=0)] | Ohms,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._dark_ohms:  Ohms = Ohms(dark_ohms)
        self._light_ohms: Ohms = Ohms(light_ohms)
        self._ports = {
            't1': Port('t1', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
            't2': Port('t2', Direction.BIDIR, domain, mandatory=True, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def dark_ohms(self) -> Ohms:
        return self._dark_ohms

    @property
    def light_ohms(self) -> Ohms:
        return self._light_ohms

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        # Light-modulated resistance can't be derived from terminal
        # voltages alone — same opacity as Resistor under graph
        # evaluation.  External composites that simulate the LDR's
        # light response do it via a behavioural cell.
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> tuple[Ohms, Ohms]:
        # Sizing calculator: return the (dark, light) resistance pair
        # so the surrounding design can pick its divider partner.
        return (self._dark_ohms, self._light_ohms)

    def __str__(self) -> str:
        return (f"LDR: {float(self._dark_ohms)} Ω dark / "
                f"{float(self._light_ohms)} Ω light")

    def __repr__(self) -> str:
        return (f"Photoresistor("
                f"dark_ohms={float(self._dark_ohms)!r}, "
                f"light_ohms={float(self._light_ohms)!r}, "
                f"refdes={self.refdes!r})")
