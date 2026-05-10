from __future__ import annotations

from typing import Any

from framework.ground import GroundDomain


class Node:
    """A Kirchhoff junction node. Carries a potential value within one ground domain."""

    __slots__ = ('name', 'domain', '_value')

    def __init__(self, name: str, domain: GroundDomain) -> None:
        self.name = name
        self.domain = domain
        self._value: Any = None

    @property
    def value(self) -> Any:
        return self._value

    def drive(self, value: Any) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Node('{self.name}', domain='{self.domain.name}', value={self._value!r})"
