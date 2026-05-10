from abc import ABCMeta, abstractmethod
from framework.port import Direction


class FactorNode(metaclass=ABCMeta):
    """Base class for all circuit elements: components and composite circuits.

    A factor node expresses a constitutive relation over its ports. Leaf nodes
    are components (Resistor, LED, …). Composite nodes are circuits containing
    sub-components wired together.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def ports(self) -> dict[str, 'Port']:
        ...

    @abstractmethod
    def evaluate(self) -> None:
        ...

    def _assert_no_inputs_wired(self) -> None:
        """Raise if any input port is connected to a node.

        Direct invocation of `__call__` on a wired node would silently
        overwrite the externally driven signal — refuse instead. Every
        leaf component and every chip uses this guard so the silent-
        overwrite hazard is mechanically prevented across the codebase.
        """
        wired = [n for n, p in self.ports.items()
                 if p.direction is Direction.IN and p.connected]
        if wired:
            raise RuntimeError(
                f"{type(self).__name__}.__call__ refused: input port(s) wired "
                f"by an enclosing circuit ({', '.join(wired)}); drive via "
                f"the parent's evaluate() instead."
            )
