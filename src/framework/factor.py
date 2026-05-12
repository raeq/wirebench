from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, ClassVar

from framework.errors import WiredChipCallError
from framework.port import Direction, Port


class FactorNode(metaclass=ABCMeta):
    """Base class for all circuit elements: components and composite circuits.

    A factor node expresses a constitutive relation over its ports. Leaf nodes
    are components (Resistor, LED, …). Composite nodes are circuits containing
    sub-components wired together.
    """

    __slots__ = ()

    # If True, this component is a conductor: the framework treats its
    # internal and external faces as one logical net for ERC, and
    # Circuit._validate walks through the component when counting drivers.
    # Used for chip pins (bonded wire from silicon to package) and
    # connector contacts (spring contact in housing). Default False.
    IS_CONDUCTOR: ClassVar[bool] = False

    # If True, this component is *transparent* to the parent's
    # topological sort and evaluation: the parent walks into its
    # sub-components and orders them individually rather than treating
    # this component as a single eval step.  Used for connectors (a
    # connector's pins go in independent directions and need pin-level
    # toposort granularity).  Chips remain opaque (False); their pins +
    # cells live within their own Circuit.evaluate.
    IS_TRANSPARENT: ClassVar[bool] = False

    # Default footprint string for downstream exporters (KiCad, BOM,
    # Yosys). None means "no footprint declared" — exporters that
    # require one error out, exporters that don't simply omit the
    # field. Subclasses override either as a ClassVar (fixed-geometry
    # parts) or via @property (parameterised families that compute
    # from instance state like pin_count/pitch).  Declared as a
    # property here (rather than `ClassVar[str | None] = None`) so
    # that mypy permits the @property override in parameterised
    # subclasses; a literal class-attribute override still works.
    @property
    def FOOTPRINT(self) -> str | None:
        return None

    # Pin numbers for passive terminals whose ports are not wrapped in
    # Pin instances. Maps port name -> datasheet pin number. Chips and
    # connectors carry numbers on each Pin.id; passives declare them
    # here. See framework.export.base.pin_number_of for the unified
    # lookup used by exporters.
    PIN_NUMBERS: ClassVar[dict[str, int]] = {}

    def other_face(self, port: Port) -> Port:
        """Return the opposite face of this conductor, given one face.

        Only meaningful on IS_CONDUCTOR components (Pin).  The default
        raises — non-conductors have no notion of paired faces.
        """
        raise NotImplementedError(
            f"{type(self).__name__} is not a conductor; other_face() not defined"
        )

    @property
    @abstractmethod
    def ports(self) -> dict[str, Port]:
        ...

    @abstractmethod
    def evaluate(self) -> None:
        ...

    def _assert_no_inputs_wired(self) -> None:
        """Raise if any input or BIDIR port is connected to a node.

        Direct invocation of `__call__` on a wired node would silently
        overwrite the externally driven signal — refuse instead. Every
        leaf component and every chip uses this guard so the silent-
        overwrite hazard is mechanically prevented across the codebase.

        BIDIR ports are included because they may be written from
        __call__ (Resistor's __call__ does this today, but skips this
        guard deliberately because it doesn't actually touch ports).
        Any future BIDIR-driving __call__ inherits the protection.
        """
        wired = [n for n, p in self.ports.items()
                 if p.direction in (Direction.IN, Direction.BIDIR) and p.connected]
        if wired:
            raise WiredChipCallError(
                f"{type(self).__name__}.__call__ refused: port(s) wired "
                f"by an enclosing circuit ({', '.join(wired)}); drive via "
                f"the parent's evaluate() instead."
            )

    def __getattr__(self, name: str) -> Any:
        """Proxy port lookup as attribute access.

        `chip.PD3` resolves to `chip.ports['PD3']` when `PD3` is a port
        name and no real attribute by that name exists.  Lets wire()
        calls read as `wire(arduino.PD3, display.DIG_1)` instead of
        `wire(arduino.ports['PD3'], display.ports['DIG_1'])`.

        Only fires when normal attribute lookup misses, so slots,
        properties, methods, and class attributes are untouched.
        Private names (leading `_`) and `ports` itself short-circuit
        so that pickle, copy, and pydantic introspection don't trip
        the proxy and so that a missing `_ports` during __init__
        doesn't recurse.

        Return type is `Any` because the proxy is a fallback for any
        attribute the static type-checker can't see — including
        composite cells (`board.led`) and Python instance attributes
        set in `__init__` of subclasses that don't declare them in
        `__slots__`.  Annotating as `-> Port` would (incorrectly) tell
        mypy that *every* unknown attribute is a Port.
        """
        if name.startswith('_') or name == 'ports':
            raise AttributeError(name)
        try:
            ports = self.ports
        except Exception:
            raise AttributeError(name)
        try:
            return ports[name]
        except (KeyError, TypeError):
            raise AttributeError(name)
