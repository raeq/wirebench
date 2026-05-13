from __future__ import annotations

from abc import abstractmethod
from typing import Any, ClassVar, Sequence

from pydantic import validate_call

from framework.circuit import Circuit
from framework.errors import PartConfigurationError
from framework.factor import FactorNode
from framework.pin import Pin
from framework.port import Direction, Port
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

    **Construction-time invariant:** every declared OUT pin must be
    driven by an internal cell.  The check runs after `super().__init__`
    completes and refuses to construct any subclass whose OUT pin's
    internal face has no real driver.  The opt-out is
    `BARE_FIRMWARE_DRIVEN = True` for chips whose OUT pins are driven
    by user firmware injected via subclassing (MCUs are the canonical
    case).  Cells follow the pattern in
    `src/components/chips/concepts/`: a `FactorNode` with input ports
    matching the chip's IN pins and an OUT port wired to the chip's
    OUT-pin internal face.
    """

    # Opt-out flag for chip classes that legitimately ship with `cells=[]`
    # and unmodelled OUT pins because user firmware drives those pins
    # via subclassing (see Phase 8 of the behavioural-cell audit).  Set
    # True on MCU classes; every other use should be flagged at code
    # review — add a behavioural cell instead.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = False

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
        if not self.BARE_FIRMWARE_DRIVEN:
            self._assert_every_out_pin_is_internally_driven(list(pins))

    def _assert_every_out_pin_is_internally_driven(
        self, pins: list[Pin],
    ) -> None:
        """Refuse to construct a Chip whose declared OUT pins aren't
        backed by an internal driver.  Construction-time enforcement
        of the behavioural-cell contract.

        For each OUT pin, the *internal* face must sit on a logical
        net containing at least one OUT-direction port that isn't
        another face of the same Pin.  Drivers can be:

          - A cell's OUT port (the typical behavioural-cell case).
          - Another Pin's internal face whose external is IN —
            valid for pure pass-through chips where one pin's
            external drive propagates to another pin internally
            via direct wiring rather than a cell.

        Violations raise `PartConfigurationError` naming the offending
        pin and pointing the contributor at the audit spec.  Set
        `BARE_FIRMWARE_DRIVEN = True` on the class to opt out (only
        legitimate for firmware-driven parts).
        """
        for pin in pins:
            if pin._role is not Direction.OUT:
                continue
            internal = pin.internal
            node = internal.node
            if node is None:
                self._raise_undriven(pin)
                return
            # A driver is any OUT-direction port on the net that
            # isn't a face of *this same Pin* — other Pins' faces
            # (propagating an external drive through the chip) and
            # cells' OUT ports both count.
            has_real_driver = any(
                (p is not internal) and (p is not pin.external)
                and (p.direction is Direction.OUT)
                for p in node.ports
            )
            if not has_real_driver:
                self._raise_undriven(pin)

    def _raise_undriven(self, pin: Pin) -> None:
        raise PartConfigurationError(
            f"{type(self).__name__} declares pin {pin.id.name!r} "
            f"(pin {pin.id.number}) as Direction.OUT but no behavioural "
            f"cell drives its internal face.  Add a cell to __init__ "
            f"that drives this pin's internal face, or — if this chip "
            f"is firmware-driven — set BARE_FIRMWARE_DRIVEN = True on "
            f"the class.  See `src/components/chips/concepts/` for "
            f"established cell patterns (LinearRegulator, OpAmp, "
            f"Comparator, Inverter, …)."
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
