from __future__ import annotations

from typing import ClassVar

from framework.circuit import Circuit
from framework.connector import Connector
from framework.factor import FactorNode
from framework.refdes import validate_refdes
from framework.registry import register


@register('Board')
class Board(Circuit):
    """A printed circuit board: a populated PCB with name, revision,
    and a refdes (it is itself a part within a parent assembly).

    The board's external surface is the set of external pin faces of
    every `Connector` component on it.  Surface port names are qualified
    by the connector's refdes — e.g. 'J1.p3' — to guarantee uniqueness
    when a board carries more than one connector.

    Refdes scoping is correct for free: `Circuit._validate` (per the
    refdes spec) is non-recursive, so each Board contributes only its
    own refdes 'A1' / 'A2' to the parent assembly's namespace, while
    its internal R1/D1/U1 are private to itself.
    """

    REFDES_PREFIX: ClassVar[str] = 'A'

    __slots__ = ('_name', '_revision', '_connectors', '_refdes_number')

    def __init__(
        self,
        *,
        name: str,
        revision: str,
        components: list[FactorNode],
        refdes_number: int,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        if not isinstance(name, str) or not name:
            raise ValueError("Board name must be a non-empty string")
        if not isinstance(revision, str) or not revision:
            raise ValueError("Board revision must be a non-empty string")

        self._name          = name
        self._revision      = revision
        self._refdes_number = refdes_number
        self._connectors    = tuple(c for c in components if isinstance(c, Connector))

        # Surface = external faces of every connector, qualified by refdes.
        ports = {}
        for connector in self._connectors:
            for pin_name, port in connector.external_ports.items():
                qualified = f"{connector.refdes}.{pin_name}"
                if qualified in ports:
                    raise ValueError(
                        f"Duplicate surface port '{qualified}' — "
                        f"two connectors share refdes {connector.refdes}?"
                    )
                ports[qualified] = port

        super().__init__(factor_nodes=list(components), ports=ports)

    @property
    def name(self) -> str:
        return self._name

    @property
    def revision(self) -> str:
        return self._revision

    @property
    def connectors(self) -> tuple[Connector, ...]:
        return self._connectors

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    def __repr__(self) -> str:
        return (
            f"Board(name={self._name!r}, revision={self._revision!r}, "
            f"refdes={self.refdes!r})"
        )
