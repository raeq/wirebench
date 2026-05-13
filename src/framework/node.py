from __future__ import annotations

from typing import TYPE_CHECKING, Any

from framework.ground import GroundDomain

if TYPE_CHECKING:
    from framework.port import Port


class Node:
    """A Kirchhoff junction node. Carries a potential value within one ground domain."""

    __slots__ = ('name', 'domain', '_value', '_ports')

    def __init__(self, name: str, domain: GroundDomain) -> None:
        self.name = name
        self.domain = domain
        self._value: Any = None
        # Ports attached to this node, in attachment order.  Populated
        # by `wire()` via `_attach`; used by Circuit's orphan-port
        # detector to walk the wiring graph from one part's
        # port across the shared node to every other port on the same
        # net.
        self._ports: list[Port] = []

    @property
    def value(self) -> Any:
        return self._value

    def drive(self, value: Any) -> None:
        self._value = value

    def _attach(self, port: Port) -> None:
        """Called by `wire()` when a port joins this node.  Underscore
        prefix because external callers should never invoke this —
        `wire()` is the only legitimate caller."""
        self._ports.append(port)

    @property
    def ports(self) -> tuple[Port, ...]:
        """All ports attached to this node, in attachment order."""
        return tuple(self._ports)

    def __repr__(self) -> str:
        return f"Node('{self.name}', domain='{self.domain.name}', value={self._value!r})"
