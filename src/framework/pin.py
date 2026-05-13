from typing import Annotated, ClassVar

from pydantic import Field, validate_call
from pydantic.dataclasses import dataclass

from framework.errors import PortContentionError, UnknownPortError
from framework.part import Part
from framework.ground import GroundDomain
from framework.port import Port, Direction


@dataclass(frozen=True, slots=True, config={"arbitrary_types_allowed": False})
class PinId:
    """The identity of a pin on a physical package: its 1-indexed pin
    number (its position on the package, as stamped on silkscreen and
    called out in the datasheet) plus its functional name (what the
    schematic label says — 'VBUS', 'a_1', 'y_3', 'GND').

    Two pins on the same package may share a name (multiple GND pins on
    a USB-C receptacle, for example) but never a number. Numbering
    matches the manufacturer's datasheet exactly: a 14-pin DIP has pins
    1..14, a 24-pin USB-C receptacle has pins 1..24, etc. The framework
    does not invent numbers — it copies them from the datasheet.
    """

    number: Annotated[int, Field(gt=0, strict=True)]
    name:   Annotated[str, Field(min_length=1)]

    def __str__(self) -> str:
        # Human-readable: "pin 7 (GND)". Used in error messages and reprs.
        return f"pin {self.number} ({self.name})"


class Pin(Part):
    """A chip pin or connector contact: the bonded wire that bridges
    silicon (or PCB trace) and the outside world.

    Every Pin has two faces:
      - external — the package pin a consumer wires to. Its direction is the
                   pin's *physical* role (IN, OUT, BIDIR).
      - internal — what the chip's cells (or the board's wiring) connect to.
                   For IN/OUT pins, internal's direction is the inverse of
                   external's: an external IN pin drives the internal mesh
                   (its internal face is OUT); an external OUT pin reads the
                   internal mesh (its internal face is IN).  For BIDIR pins,
                   both faces are BIDIR — the contact carries whichever way
                   the surrounding circuit dictates.

    Pin.evaluate copies signal across the boundary.  For BIDIR pins it also
    detects contention: if external and internal hold different non-None
    values, the contact has two writers fighting and ValueError is raised.

    A Pin is a *conductor* (IS_CONDUCTOR = True).  Circuit._validate walks
    through Pin instances when computing logical nets, so a chip's bonded
    wire and a connector's spring contact are transparent to ERC — drivers
    and readers attached at each end of the conductor are counted on the
    same extended net.  This mirrors the way KiCad / Altium / OrCAD ERC
    works on real PCBs.

    A consumer of a chip never sees the internal face.  From outside the
    only port surface is `pin.external`.

    The first constructor argument is a `PinId` — both the datasheet
    pin number (e.g. 7) and the functional name (e.g. 'GND') in one
    immutable record.  Exporters that emit netlists rely on the number;
    wiring code uses the name.
    """

    __slots__ = ('_id', '_role', '_external', '_internal', '_effective_role')

    IS_CONDUCTOR: ClassVar[bool] = True

    @validate_call(config={"arbitrary_types_allowed": True})
    def __init__(
        self,
        id_: PinId,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type,
    ) -> None:
        self._id   = id_
        self._role = direction
        if direction is Direction.IN:
            # External IN (consumer drives), internal OUT (pin drives the mesh).
            self._external = Port(
                id_.name, Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
        elif direction is Direction.OUT:
            # External OUT (pin drives consumer), internal IN (pin reads mesh).
            self._external = Port(
                id_.name, Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
        else:  # BIDIR
            # Both faces BIDIR — the contact is a wire, direction is set by
            # whatever's wired on either side.
            self._external = Port(
                id_.name, Direction.BIDIR, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.BIDIR, domain,
                mandatory=False, signal_type=signal_type,
            )

        # Back-reference so Circuit._validate's logical-net walker can find
        # the Pin (and its IS_CONDUCTOR / other_face) when reached through
        # a port at any composite level.
        self._external._owner = self
        self._internal._owner = self

        # Set by Circuit._topological_sort for BIDIR pins, once it can
        # resolve direction by walking through neighbouring conductors
        # to find a real driver/reader.  Treated as the effective role
        # at evaluate-time, overriding the declared BIDIR ambiguity.
        self._effective_role: Direction | None = None

    @property
    def id(self) -> PinId:
        return self._id

    @property
    def number(self) -> int:
        return self._id.number

    @property
    def name(self) -> str:
        return self._id.name

    @property
    def external(self) -> Port:
        return self._external

    @property
    def internal(self) -> Port:
        return self._internal

    @property
    def ports(self) -> dict[str, Port]:
        # Both faces are visible to the chip-internal eval graph (so the
        # topological sort wires the pin into the dependency order). Only
        # `external` should be exposed to consumers; that is the chip's
        # responsibility, not the pin's.
        #
        # Keys are the ports' own names — same convention as every other
        # Part. This keeps Circuit._validate's error messages
        # honest ('Pin.oe' instead of 'Pin.external').
        return {self._external.name: self._external,
                self._internal.name: self._internal}

    @validate_call(config={"arbitrary_types_allowed": True})
    def other_face(self, port: Port) -> Port:
        """Return the opposite face of this conductor, given one face.

        Used by Circuit._validate when walking logical nets across
        Pin boundaries.
        """
        if port is self._external:
            return self._internal
        if port is self._internal:
            return self._external
        raise UnknownPortError(f"port {port!r} is not a face of pin {self!r}")

    def evaluate(self) -> None:
        role = self._effective_role if self._effective_role is not None else self._role
        if role is Direction.IN:
            self._internal.drive(self._external.value)
        elif role is Direction.OUT:
            self._external.drive(self._internal.value)
        else:  # BIDIR with no resolved direction
            ext, intl = self._external.value, self._internal.value
            if ext is None and intl is None:
                return
            if ext is not None and intl is None:
                self._internal.drive(ext)
            elif intl is not None and ext is None:
                self._external.drive(intl)
            elif ext != intl:
                raise PortContentionError(
                    f"BIDIR pin '{self._external.name}' contention: "
                    f"external={ext!r}, internal={intl!r}"
                )
            # else both equal — no-op

    def __str__(self) -> str:
        return f"{self._external.name}={self._external.value}"

    def __repr__(self) -> str:
        return f"Pin({self._id}, {self._role.value})"
