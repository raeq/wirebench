from typing import Any, ClassVar

from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog
from framework.registry import register


@register('Antenna')
class Antenna(Part):
    """Long-wire or whip antenna — environment-fed signal source.

    Distinct from `Rail`: a Rail is a declared steady-state power
    supply (Vcc or GND), driven by the bench supply.  An Antenna is
    a *signal source* whose level is whatever EM field the
    environment provides at the antenna's location, integrated over
    its capture area.  For wirebench's static topology validation
    the Antenna is treated as a driver — its `out` port is
    Direction.OUT — but no specific value is propagated.

    A crystal radio's Antenna + Earth pair forms the entire power
    budget: tens of microwatts of RF energy collected by the
    antenna, returned through the earth connection.  No declared
    Rail need appear in the design — this is the boundary case the
    spec flags as the *passive-only-with-environment-source*
    topology.

    Pin numbering: single `out` port at pin 1.  No footprint —
    real antennas are external to the board, terminated to a wire
    soldered to a board-edge solder pad.

        Antenna(refdes_number=1)
    """

    __slots__ = ('_ports', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'A'
    FOOTPRINT: ClassVar[str | None] = None
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'out': 1}

    LAYOUT: ClassVar[dict[str, Any]] = {
        'kind': 'antenna',
        'lead_spacing_holes': 1,
    }

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**For a crystal radio, the antenna is the longer the "
        "better** — practical sets work with anything from a 3 m "
        "whip up to a 30 m long-wire stretched across the loft.  "
        "Hang it as high as you can; the higher the average position "
        "the larger the EM-field capture and the louder the "
        "station-in-the-earphone signal.  Mount the antenna terminal "
        "as a screw post or insulated banana socket so the wire can "
        "be removed when the radio is stored.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Disconnect the antenna during thunderstorms.**  A "
        "long-wire antenna can pick up induced voltages from "
        "nearby lightning strikes that exceed several hundred volts.  "
        "Modern crystal radios with no active components have nothing "
        "to damage, but the same antenna feeding a transistor receiver "
        "destroys input semiconductors.  A spark gap or gas-discharge "
        "tube across the antenna-to-earth pair provides cheap "
        "protection.",
        "**Don't run the antenna lead near mains wiring.**  Mains "
        "hum (50 / 60 Hz and its harmonics) couples into the antenna "
        "and overwhelms the signal of any but the strongest "
        "stations.  Keep the lead at least a metre from any mains "
        "cabling and route it perpendicular to (rather than parallel "
        "with) ceiling joists or wall studs that may carry mains "
        "behind them.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._ports = {
            # Direction.OUT marks the Antenna as a driver — the
            # crystal-set's tank network sees its t1 terminal as
            # driven, even though the actual drive value is RF-
            # modulated by the environment and not representable
            # under voltage-only graph evaluation.
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
        # No declared signal value — the antenna's output is whatever
        # the local EM field provides, which a voltage-only static
        # graph can't represent.  Left as None so downstream consumers
        # see "undriven" rather than a misleading bench voltage.
        pass

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self) -> None:
        return None

    def __repr__(self) -> str:
        return f"Antenna(refdes={self.refdes!r})"
