from framework.signals import Analog


class _Unit(Analog):
    __slots__ = ()

    # Additive ops preserve unit type; mul/div intentionally return float (units change).
    def __add__(self, other):  return type(self)(float(self) + float(other))
    def __radd__(self, other): return type(self)(float(other) + float(self))
    def __sub__(self, other):  return type(self)(float(self) - float(other))
    def __rsub__(self, other): return type(self)(float(other) - float(self))
    def __neg__(self):         return type(self)(-float(self))
    def __abs__(self):         return type(self)(abs(float(self)))
    def __pos__(self):         return type(self)(+float(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({float(self)!r})"


class Amps(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} A"


class Milliamps(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} mA"


class Microamps(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} µA"


class Millivolts(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} mV"


class Volts(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} V"


class Ohms(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} Ω"


class Kilohms(_Unit):
    __slots__ = ()

    def __str__(self) -> str:
        return f"{float(self):.3g} kΩ"
