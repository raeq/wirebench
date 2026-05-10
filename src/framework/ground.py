class GroundDomain:
    """A ground reference domain. Voltage is only defined between nodes in the same domain."""

    __slots__ = ['name']

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"GroundDomain('{self.name}')"

    def __str__(self) -> str:
        return self.name


ELECTRICAL = GroundDomain('electrical')
