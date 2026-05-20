from typing import Any, ClassVar

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.registry import register


@register('Earth')
class Earth(Part):
    """Earth-ground connection — the literal soil, the cold-water pipe,
    or the mains-protective-earth terminal.

    Distinct from `Rail(False)`: a low Rail is a declared bench-
    supply ground reference (a wire to the negative terminal of the
    9 V battery, say).  An Earth is a *physical earth* connection —
    a wire to the local soil through a buried rod, or to the
    cold-water plumbing's metallic pipework, or to a building's
    safety-earth bonding point.  In a crystal radio Earth is the
    return path for the microwatts of RF energy the Antenna
    collected; the radio runs on the *potential difference* between
    Antenna and Earth, with no declared supply rail involved.

    Pin numbering: single `out` port at pin 1.  No footprint — the
    actual earth connection is external to the board, terminated to
    a wire soldered to a board-edge pad and clipped to whatever
    earth reference the build uses.

        Earth(refdes_number=1)
    """

    __slots__ = ('_ports', '_refdes_number')

    # `'E'` matches the conventional schematic label for an *Earth*
    # terminal in vintage British schematics (which is what Penfold's
    # BP107 uses throughout).  Distinct from `Antenna.REFDES_PREFIX = 'A'`
    # so two parts can co-exist in one Circuit without colliding on a
    # shared number-space.
    REFDES_PREFIX: ClassVar[str] = 'E'
    FOOTPRINT: ClassVar[str | None] = None
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'out': 1}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'earth',
        'lead_spacing_holes': 1,
    }

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**A good earth is one of the two things that makes a "
        "crystal radio audible.**  Test the candidate earth point "
        "with a continuity meter to a known good earth (a mains-"
        "earth socket pin); the reading should be under 1 Ω.  "
        "A cold-water pipe is usually fine if it's metallic *all "
        "the way to the supply main*; modern plastic-piped houses "
        "won't work.  A copper rod driven 1 m into damp soil is the "
        "classical option.  Avoid mains protective earth — see the "
        "first GOTCHA below.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Don't use the mains protective earth in a crystal radio.**  "
        "Connecting an antenna lead to the protective-earth wire "
        "(via a wall socket's earth pin) introduces a path for "
        "induced antenna currents to flow through the household "
        "mains earth — which can trip RCDs and, in the worst case, "
        "carry harmful currents during nearby lightning strikes.  "
        "Use a dedicated radio earth (cold-water pipe, copper rod, "
        "balcony railing) that's electrically separate from the "
        "house mains.",
        "**A poor earth makes the radio sound noisy, not silent.**  "
        "If your set picks up strong stations but with significant "
        "background hiss / hum, the earth is the first thing to "
        "improve.  Wetting the soil around the earth rod, lengthening "
        "the earth lead, or substituting a cold-water pipe (if "
        "metallic) for the rod each makes a measurable difference.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            # Direction.OUT — Earth is the return-path driver from
            # the framework's perspective.  Its value is 0 V by
            # convention (the reference against which everything
            # else is measured).
            'out': Port('out', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def evaluate(self) -> None:
        # Drive `out` to 0.0 V (the conventional earth reference).
        # In the crystal-radio context this is what gives the tank's
        # one side a defined potential to compare the antenna's
        # induced voltage against.
        self._ports['out'].drive(0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return f"Earth(refdes={self.refdes!r})"
