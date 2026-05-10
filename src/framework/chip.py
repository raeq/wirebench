from abc import abstractmethod
from framework.circuit import Circuit
from framework.factor import FactorNode
from framework.pin import Pin
from framework.port import Direction


class Chip(Circuit):
    """Abstract base for integrated circuits.

    A chip's external surface is its package pins, modelled as `Pin`
    instances.  Internal cells (NOR latches, comparators, inverters …)
    are private — consumers only ever wire to pins.

    The base class enforces the encapsulation barrier structurally:
    `__init__` accepts pins and cells separately, and the chip's `ports`
    are derived as `{pin.external.name: pin.external for pin in pins}`.
    There is no way to expose a leaf cell port as a chip pin.

    Subclasses provide their own __init__ to instantiate cells, create
    pins, and wire them together — then call `super().__init__(pins=...,
    cells=...)`.  Each subclass also implements `__call__` (the
    standalone-test invocation surface) and must call
    `self._assert_no_inputs_wired()` first to refuse silent overwrites
    of parent-driven pins.
    """

    __slots__ = []

    def __init__(self, *, pins: list[Pin], cells: list[FactorNode]) -> None:
        ports = {pin.external.name: pin.external for pin in pins}
        super().__init__(
            factor_nodes=list(pins) + list(cells),
            ports=ports,
        )

    def _assert_no_inputs_wired(self) -> None:
        """Raise if any input pin is already connected by an enclosing circuit.

        Calling __call__ on a wired chip would silently overwrite the
        parent's driven signal — refuse instead so the caller has to
        choose between standalone use and wired use.
        """
        wired = [n for n, p in self._ports.items()
                 if p.direction is Direction.IN and p.connected]
        if wired:
            raise RuntimeError(
                f"{type(self).__name__}.__call__ refused: input pin(s) wired "
                f"by an enclosing circuit ({', '.join(wired)}); drive via "
                f"the parent's evaluate() instead."
            )

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
