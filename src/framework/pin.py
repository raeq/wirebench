from framework.factor import FactorNode
from framework.ground import GroundDomain
from framework.port import Port, Direction


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
    """

    __slots__ = ('_role', '_external', '_internal')

    def __init__(
        self,
        name: str,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type,
    ) -> None:
        if direction is Direction.BIDIR:
            raise NotImplementedError("BIDIR pins are not yet supported")
        self._role = direction
        if direction is Direction.IN:
            # External: IN (consumer drives it). Internal: OUT (pin drives the mesh).
            self._external = Port(
                name, Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
            self._internal = Port(
                f'{name}_inner', Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
        else:  # OUT
            # External: OUT (pin drives consumer). Internal: IN (pin reads mesh).
            self._external = Port(
                name, Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
            self._internal = Port(
                f'{name}_inner', Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )

    @property
    def external(self) -> Port:
        return self._external

    @property
    def internal(self) -> Port:
        return self._internal

    @property
    def ports(self) -> dict:
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

    def __repr__(self) -> str:
        return f"Pin('{self._external.name}', {self._role.value})"
