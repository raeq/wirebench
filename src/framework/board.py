from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.circuit import Circuit
from framework.connector import Connector
from framework.factor import FactorNode
from framework.refdes import RefdesNumber, validate_refdes
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

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        name: Annotated[str, Field(min_length=1)],
        revision: Annotated[str, Field(min_length=1)],
        components: list[FactorNode] | None = None,
        refdes_number: RefdesNumber,
    ) -> None:
        # Board's own state (name / revision / refdes_number) lives in
        # Board.__slots__, so these assignments never pollute the
        # instance __dict__ that auto-collect will scan in a moment.
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._name          = name
        self._revision      = revision
        self._refdes_number = refdes_number

        # Auto-collect: if the subclass omits __slots__ and assigns
        # parts as `self.x = Y(...)` before calling super().__init__(),
        # `components=None` scans `self.__dict__` for FactorNode-typed
        # values (one level of tuple/list/dict unpacking).  Same rules
        # as Circuit's auto-collect.
        if components is None:
            components = self._auto_collect_factor_nodes()

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
