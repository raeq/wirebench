from __future__ import annotations

from abc import abstractmethod
from typing import Any, Sequence

from pydantic import validate_call

from framework.circuit import Circuit
from framework.factor import FactorNode
from framework.pin import Pin
from framework.port import Port
from framework.port_map import PortMap


class Chip(Circuit):
    """Abstract base for integrated circuits.

    A chip's external surface is its package pins, modelled as `Pin`
    instances.  Internal cells (NOR latches, comparators, inverters …)
    are private — consumers only ever wire to pins.

    The base class enforces the encapsulation barrier structurally:
    `__init__` accepts pins and cells separately.  Pin lookup is by
    datasheet pin number (`chip.ports_by_number[<n>]`) as the canonical
    addressing scheme — a name-based view (`chip.ports[<name>]`) is
    provided for convenience and raises clearly if a name is shared by
    multiple pins.  There is no way to expose a leaf cell port as a
    chip pin.

    Subclasses provide their own __init__ to instantiate cells, create
    pins, and wire them together — then call `super().__init__(pins=...,
    cells=...)`.  Each subclass also implements `__call__` (the
    standalone-test invocation surface) and must call
    `self._assert_no_inputs_wired()` first to refuse silent overwrites
    of parent-driven pins.
    """

    __slots__ = ('_ports_by_number', '_port_map')

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, *, pins: Sequence[Pin], cells: Sequence[FactorNode]) -> None:
        by_number = {pin.id.number: pin.external for pin in pins}
        self._ports_by_number = by_number
        self._port_map = PortMap(by_number)
        # The parent Circuit's `_ports` mapping is the disambiguated
        # name-keyed dict — keeps Circuit._validate iteration, save/load
        # port references, and toposort working without special-casing.
        super().__init__(
            factor_nodes=list(pins) + list(cells),
            ports=dict(self._port_map.items()),
        )

    @property
    def ports(self) -> PortMap:  # type: ignore[override]
        return self._port_map

    @property
    def ports_by_number(self) -> dict[int, Port]:
        """Canonical pin lookup: datasheet pin number → external Port."""
        return self._ports_by_number

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The chip's package pins, in declaration order. Exporters
        rely on this to enumerate the surface in datasheet-pin-number
        order via `sorted(chip.pins, key=lambda p: p.id.number)`."""
        return tuple(fn for fn in self._factor_nodes if isinstance(fn, Pin))

    # _assert_no_inputs_wired is inherited from FactorNode — every node
    # with input ports has the same silent-overwrite hazard.

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...
