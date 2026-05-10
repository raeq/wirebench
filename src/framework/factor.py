from abc import ABCMeta, abstractmethod


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
