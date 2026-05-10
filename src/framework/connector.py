from __future__ import annotations

from typing import Any, ClassVar

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Direction, Port
from framework.refdes import validate_refdes


class Connector(FactorNode):
    """A physical connector — a housing with a fixed set of named contacts.

    Each contact is a `Pin`, with an external face that mates with the
    partner connector and an internal face wired to the rest of the
    board.  Concrete subclasses correspond to real-world parts and
    declare their pin count, pitch, gender, contact pinout, and physical
    mating partner.

    A Connector is not a Circuit — it has no internal wiring graph; it
    is a housing of Pins.  Circuit._validate walks through each Pin
    (IS_CONDUCTOR=True) when computing logical nets, so the connector's
    contacts are transparent to ERC.

    A Connector is also IS_TRANSPARENT=True: the parent's topological
    sort expands the connector into its individual pins so cross-cutting
    signal paths (some pins driving inward, others driving outward) get
    pin-level ordering rather than treating the connector as one node
    in the dependency graph.  Without this, two pins on the same
    connector going in opposite directions would form a false cycle.
    """

    IS_TRANSPARENT: ClassVar[bool] = True

    __slots__ = ('_pins', '_refdes_number', '_pin_count', '_pitch_mm')

    REFDES_PREFIX:  ClassVar[str]                       # 'J' (female) or 'P' (male)
    GENDER:         ClassVar[str]                       # 'female' | 'male'
    # Set via declare_mating_pair() if the part has a board-to-board mate;
    # left None for user-facing receptacles (USB, audio, microSD, …).
    MATES_WITH:     ClassVar["type[Connector] | None"] = None

    # Subclasses set ONE of:
    #   - PIN_COUNT (ClassVar) and PITCH_MM (ClassVar) — fixed-geometry parts.
    #   - Neither — the constructor must then receive pin_count and pitch_mm
    #     for parameterised families like 0.1" snap-apart headers.
    PIN_COUNT:      ClassVar[int   | None] = None
    PITCH_MM:       ClassVar[float | None] = None

    # Subclasses provide a pinout in ONE of two ways:
    #   - PINOUT class attribute: a tuple of (PinId, direction, signal_type)
    #     for fixed-geometry parts where every contact has a known role.
    #   - Override `_build_pinout()` to synthesise it from pin_count
    #     (parameterised families).
    PINOUT: ClassVar[tuple[tuple[PinId, Direction, type], ...] | None] = None

    def __init__(
        self,
        *,
        domain: GroundDomain = ELECTRICAL,
        refdes_number: int,
        pin_count: int | None = None,
        pitch_mm: float | None = None,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number

        # Resolve pin_count and pitch_mm: explicit constructor argument
        # wins; otherwise inherit from the class attribute.  Each must
        # come from somewhere or the part is under-specified.
        resolved_pin_count = pin_count if pin_count is not None else self.PIN_COUNT
        resolved_pitch_mm  = pitch_mm  if pitch_mm  is not None else self.PITCH_MM
        if resolved_pin_count is None:
            raise TypeError(
                f"{type(self).__name__} requires pin_count "
                f"(neither constructor arg nor PIN_COUNT class attribute set)"
            )
        if resolved_pitch_mm is None:
            raise TypeError(
                f"{type(self).__name__} requires pitch_mm "
                f"(neither constructor arg nor PITCH_MM class attribute set)"
            )
        self._pin_count = resolved_pin_count
        self._pitch_mm  = resolved_pitch_mm

        self._pins = tuple(
            Pin(pin_id, direction, domain, mandatory=False, signal_type=sigtype)
            for pin_id, direction, sigtype in self._build_pinout()
        )

    def _build_pinout(self) -> tuple[tuple[PinId, Direction, type], ...]:
        """Return ((PinId, direction, signal_type), …) for every contact.

        Default implementation reads the PINOUT class attribute (fixed-
        geometry parts).  Parameterised families override to synthesise
        a generic BIDIR Analog pinout from pin_count.
        """
        if self.PINOUT is None:
            raise TypeError(
                f"{type(self).__name__} must either set PINOUT "
                f"or override _build_pinout()"
            )
        return self.PINOUT

    @property
    def pins(self) -> tuple[Pin, ...]:
        return self._pins

    @property
    def external_ports(self) -> dict[str, Port]:
        """Pin externals only — what the partner connector mates to,
        and what the board exposes on its surface."""
        return {pin.external.name: pin.external for pin in self._pins}

    @property
    def ports(self) -> dict[str, Port]:
        """Both faces of every pin — needed by Circuit._validate and
        Circuit._topological_sort inside the enclosing board."""
        out: dict[str, Port] = {}
        for pin in self._pins:
            out.update(pin.ports)
        return out

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def pin_count(self) -> int:
        return self._pin_count

    @property
    def pitch_mm(self) -> float:
        return self._pitch_mm

    def evaluate(self) -> None:
        for pin in self._pins:
            pin.evaluate()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(refdes={self.refdes!r}, "
            f"pin_count={self._pin_count}, pitch_mm={self._pitch_mm})"
        )


def declare_mating_pair(a: type[Connector], b: type[Connector]) -> None:
    """Mark two Connector subclasses as physical mates of each other.

    Called at module-bottom after both gendered halves of a connector
    family are defined, to set the symmetric `MATES_WITH` ClassVars
    without forward-reference awkwardness.
    """
    a.MATES_WITH = b
    b.MATES_WITH = a
