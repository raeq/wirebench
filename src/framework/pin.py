from dataclasses import dataclass

from framework.factor import FactorNode
from framework.ground import GroundDomain
from framework.port import Port, Direction


@dataclass(frozen=True, slots=True)
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

    number: int
    name: str

    def __post_init__(self) -> None:
        # bool is a subclass of int in Python; reject explicitly.
        if isinstance(self.number, bool) or not isinstance(self.number, int):
            raise TypeError(f"PinId.number must be an int; got {type(self.number).__name__}")
        if self.number < 1:
            raise ValueError(f"PinId.number must be ≥ 1; got {self.number}")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError(f"PinId.name must be a non-empty string; got {self.name!r}")

    def __str__(self) -> str:
        # Human-readable: "pin 7 (GND)". Used in error messages and reprs.
        return f"pin {self.number} ({self.name})"


class Pin(FactorNode):
    """A chip pin: the bonded wire that bridges silicon and the outside world.

    Every chip pin has two faces:
      - external — the package pin a consumer wires to. Its direction is the
                   pin's *physical* role (IN, OUT, BIDIR).
      - internal — what the chip's internal cells wire to. Its direction is
                   the inverse of the external role: an external IN pin
                   drives the internal mesh (so its internal face is OUT);
                   an external OUT pin reads the internal mesh (so its
                   internal face is IN).

    Pin.evaluate copies signal across the boundary in the appropriate
    direction. This makes the chip's pin a real, modelled component —
    identical in spirit to a bonded wire on a die.

    A consumer of a chip never sees the internal face. From outside a chip
    the only port surface is `pin.external`. The chip's __init__ wires
    `pin.internal` to whatever cell ports implement the pin's behaviour.

    The first constructor argument is a `PinId` — both the datasheet
    pin number (e.g. 7) and the functional name (e.g. 'GND') in one
    immutable record. Exporters that emit netlists rely on the number;
    wiring code uses the name.
    """

    __slots__ = ('_id', '_role', '_external', '_internal')

    def __init__(
        self,
        id_: PinId,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type,
    ) -> None:
        if not isinstance(id_, PinId):
            raise TypeError(f"Pin requires a PinId; got {type(id_).__name__}")
        if direction is Direction.BIDIR:
            raise NotImplementedError("BIDIR pins are not yet supported")
        self._id   = id_
        self._role = direction
        if direction is Direction.IN:
            # External: IN (consumer drives it). Internal: OUT (pin drives the mesh).
            self._external = Port(
                id_.name, Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
        else:  # OUT
            # External: OUT (pin drives consumer). Internal: IN (pin reads mesh).
            self._external = Port(
                id_.name, Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )

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
        # FactorNode. This keeps Circuit._validate's error messages
        # honest ('Pin.oe' instead of 'Pin.external').
        return {self._external.name: self._external,
                self._internal.name: self._internal}

    def evaluate(self) -> None:
        if self._role is Direction.IN:
            self._internal.drive(self._external.value)
        else:
            self._external.drive(self._internal.value)

    def __str__(self) -> str:
        return f"{self._external.name}={self._external.value}"

    def __repr__(self) -> str:
        return f"Pin({self._id}, {self._role.value})"
