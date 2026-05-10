from __future__ import annotations
from enum import Enum
from framework.ground import GroundDomain
from framework.node import Node


class Direction(Enum):
    IN  = 'in'
    OUT = 'out'


class Port:
    """A typed connection point on a factor node.

    mandatory   — if True, the port must be connected before the circuit evaluates
    signal_type — the Python type this port carries (e.g. bool, float); wire()
                  enforces that all connected ports share the same type
    """

    __slots__ = ['name', 'direction', 'domain', 'mandatory', 'signal_type', '_node', '_local_value']

    def __init__(
        self,
        name: str,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type = float,
    ) -> None:
        self.name        = name
        self.direction   = direction
        self.domain      = domain
        self.mandatory   = mandatory
        self.signal_type = signal_type
        self._node: Node | None = None
        self._local_value       = None

    @property
    def connected(self) -> bool:
        return self._node is not None

    @property
    def node(self) -> 'Node | None':
        return self._node

    def connect(self, node: Node) -> None:
        if node.domain is not self.domain:
            raise ValueError(
                f"Ground domain mismatch: port '{self.name}' is in domain "
                f"'{self.domain.name}', node '{node.name}' is in domain '{node.domain.name}'"
            )
        self._node = node

    def drive(self, value) -> None:
        if self._node is not None:
            self._node.drive(value)
        else:
            self._local_value = value

    @property
    def value(self):
        return self._node.value if self._node is not None else self._local_value

    def __repr__(self) -> str:
        return (
            f"Port('{self.name}', {self.direction.value}, "
            f"domain='{self.domain.name}', type={self.signal_type.__name__})"
        )
