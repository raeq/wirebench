from __future__ import annotations

from enum import Enum
from typing import Any

from framework.errors import DomainCrossingError, SignalTypeMismatchError
from framework.ground import GroundDomain
from framework.node import Node


class Direction(Enum):
    IN    = 'in'
    OUT   = 'out'
    BIDIR = 'bidir'


class Port:
    """A typed connection point on a factor node.

    mandatory   — if True, the port must be connected before the circuit evaluates
    signal_type — the Python type this port carries (e.g. bool, float); wire()
                  enforces that all connected ports share the same type

    _owner      — back-reference to the FactorNode that "owns" this port at
                  the physical level (e.g. a Pin for Pin.external / Pin.internal).
                  Used by Circuit._validate's logical-net walker to find the
                  IS_CONDUCTOR property and the other_face() bridge.  Optional;
                  if None, the validator falls back to whichever factor-node
                  iteration produced this port.
    """

    __slots__ = (
        'name', 'direction', 'domain', 'mandatory', 'signal_type',
        '_node', '_local_value', '_owner',
    )

    def __init__(
        self,
        name: str,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type[Any],
    ) -> None:
        self.name        = name
        self.direction   = direction
        self.domain      = domain
        self.mandatory   = mandatory
        self.signal_type = signal_type
        self._node: Node | None = None
        self._local_value: Any = None
        self._owner: Any = None

    @property
    def connected(self) -> bool:
        return self._node is not None

    @property
    def node(self) -> Node | None:
        return self._node

    def connect(self, node: Node) -> None:
        if node.domain is not self.domain:
            raise DomainCrossingError(
                f"Ground domain mismatch: port '{self.name}' is in domain "
                f"'{self.domain.name}', node '{node.name}' is in domain '{node.domain.name}'"
            )
        self._node = node
        # Register on the node so orphan-port detection can walk the
        # wiring graph from any port to its node's full membership.
        node._attach(self)

    def drive(self, value: Any) -> None:
        # None is preserved as the high-impedance / undriven sentinel.
        # Any other value is coerced to the port's signal_type at drive
        # time, mirroring wire()'s connection-time type discipline.
        # Digital ports canonicalise to Python bool — the logical-truth
        # primitive — so downstream `is True/False` and `bool(v)` work
        # uniformly.  Analog ports store their declared subtype.
        if value is not None:
            from framework.signals import Digital
            if isinstance(self.signal_type, type) and issubclass(self.signal_type, Digital):
                value = bool(Digital(value))
            elif not isinstance(value, self.signal_type):
                try:
                    value = self.signal_type(value)
                except (TypeError, ValueError) as e:
                    raise SignalTypeMismatchError(
                        f"port '{self.name}' expects {self.signal_type.__name__}, "
                        f"got {type(value).__name__}: {e}"
                    ) from e
        if self._node is not None:
            self._node.drive(value)
        else:
            self._local_value = value

    @property
    def value(self) -> Any:
        return self._node.value if self._node is not None else self._local_value

    def __repr__(self) -> str:
        return (
            f"Port('{self.name}', {self.direction.value}, "
            f"domain='{self.domain.name}', type={self.signal_type.__name__})"
        )
