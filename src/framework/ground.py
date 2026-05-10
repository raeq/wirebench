class GroundDomain:
    """A ground reference domain. Voltage is only defined between nodes in the same domain.

    Interned by name: GroundDomain('electrical') always returns the same object,
    so identity comparison (port.domain is node.domain) is always correct.
    """

    __slots__ = ('name',)
    _registry: dict[str, 'GroundDomain'] = {}

    def __new__(cls, name: str) -> 'GroundDomain':
        if name in cls._registry:
            return cls._registry[name]
        instance = super().__new__(cls)
        cls._registry[name] = instance
        return instance

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"GroundDomain('{self.name}')"

    def __str__(self) -> str:
        return self.name


ELECTRICAL = GroundDomain('electrical')
