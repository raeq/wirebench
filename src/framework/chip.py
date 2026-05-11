from __future__ import annotations

from abc import abstractmethod
from typing import Any, Iterator, Sequence

from pydantic import validate_call

from framework.circuit import Circuit
from framework.factor import FactorNode
from framework.pin import Pin
from framework.port import Port


class _PortMap:
    """Name-keyed view of a Chip's surface ports with raise-on-ambiguity
    semantics.

    Pins are canonically identified by their datasheet pin number (use
    `Chip.ports_by_number` for that).  This view is a convenience for
    the common case where pin names are unique on the chip.  If two pins
    share a name (e.g. an MCU with multiple `VCC` pins), accessing
    `chip.ports['VCC']` raises with a clear message pointing at
    `ports_by_number`; the auto-disambiguated keys (`VCC_<pin_number>`)
    still resolve, so save/load and Circuit._validate iteration both
    continue to work uniformly.

    Iteration order matches pin-number order — deterministic for
    exporters that walk `items()`.
    """

    __slots__ = ('_by_number', '_canonical_to_pins', '_disambiguated')

    def __init__(self, by_number: dict[int, Port]) -> None:
        self._by_number = by_number
        # Group ports by canonical pin name to detect duplicates.
        self._canonical_to_pins: dict[str, list[int]] = {}
        for n, port in by_number.items():
            self._canonical_to_pins.setdefault(port.name, []).append(n)
        # Build the auto-disambiguated name-keyed dict. Unique-name pins
        # use their canonical name; duplicates use `<name>_<pin_number>`.
        self._disambiguated: dict[str, Port] = {}
        for name, numbers in self._canonical_to_pins.items():
            if len(numbers) == 1:
                self._disambiguated[name] = by_number[numbers[0]]
            else:
                for n in numbers:
                    self._disambiguated[f'{name}_{n}'] = by_number[n]

    def __getitem__(self, key: str) -> Port:
        if key in self._disambiguated:
            return self._disambiguated[key]
        pins = self._canonical_to_pins.get(key)
        if pins is not None and len(pins) > 1:
            raise KeyError(
                f"Port name {key!r} is ambiguous on this chip "
                f"(pins {sorted(pins)}); use `chip.ports_by_number[<n>]` "
                f"or one of {[f'{key}_{n}' for n in sorted(pins)]!r}"
            )
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        # True for both the auto-disambiguated keys and the canonical
        # names of duplicated pins.  Lets callers test existence
        # (`'VCC' in chip.ports`) without triggering the ambiguity
        # error that `chip.ports['VCC']` would raise.
        return key in self._disambiguated or key in self._canonical_to_pins

    def __iter__(self) -> Iterator[str]:
        return iter(self._disambiguated)

    def __len__(self) -> int:
        return len(self._disambiguated)

    def items(self):
        return self._disambiguated.items()

    def values(self):
        return self._disambiguated.values()

    def keys(self):
        return self._disambiguated.keys()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


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
        self._port_map = _PortMap(by_number)
        # The parent Circuit's `_ports` mapping is the auto-disambiguated
        # name-keyed dict — keeps Circuit._validate iteration, save/load
        # port references, and toposort working without special-casing.
        super().__init__(
            factor_nodes=list(pins) + list(cells),
            ports=dict(self._port_map.items()),
        )

    @property
    def ports(self) -> _PortMap:  # type: ignore[override]
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
