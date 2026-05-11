from __future__ import annotations

from typing import Any, cast

from framework.signals import Analog


class _Unit(Analog):
    """Numeric value carrying a SI scale factor.

    The stored float is always in the family's base unit (volts, amps, ohms).
    Display uses `_SCALE` to render the value back in the declared unit:

        Millivolts(100)         # stored as 0.1 V
        float(Millivolts(100))  # 0.1
        str(Millivolts(100))    # "100 mV"
        Volts(5) - Millivolts(100) == Volts(4.9)   # cross-unit arithmetic works
    """

    __slots__ = ()
    _SCALE: float = 1.0   # multiply by this to convert to base unit

    def __new__(cls, value: Any = 0.0) -> "_Unit":
        base = 0.0 if value is None else float(value) * cls._SCALE
        return cast("_Unit", Analog.__new__(cls, base))

    @classmethod
    def _from_base(cls, base: float) -> "_Unit":
        """Construct a unit instance from an already-base-unit float (no rescaling)."""
        return cast("_Unit", Analog.__new__(cls, base))

    # Additive ops preserve unit type; mul/div intentionally return float (units change).
    def __add__(self, other: float) -> "_Unit":  return type(self)._from_base(float(self) + float(other))
    def __radd__(self, other: float) -> "_Unit": return type(self)._from_base(float(other) + float(self))
    def __sub__(self, other: float) -> "_Unit":  return type(self)._from_base(float(self) - float(other))
    def __rsub__(self, other: float) -> "_Unit": return type(self)._from_base(float(other) - float(self))
    def __neg__(self) -> "_Unit":                return type(self)._from_base(-float(self))
    def __abs__(self) -> "_Unit":                return type(self)._from_base(abs(float(self)))
    def __pos__(self) -> "_Unit":                return type(self)._from_base(+float(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({float(self) / self._SCALE!r})"


class Amps(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} A"


class Milliamps(_Unit):
    __slots__ = ()
    _SCALE = 1e-3
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} mA"


class Microamps(_Unit):
    __slots__ = ()
    _SCALE = 1e-6
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} µA"


class Volts(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} V"


class Millivolts(_Unit):
    __slots__ = ()
    _SCALE = 1e-3
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} mV"


class Ohms(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} Ω"


class Kilohms(_Unit):
    __slots__ = ()
    _SCALE = 1e3
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} kΩ"


class Farads(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} F"


class Microfarads(_Unit):
    __slots__ = ()
    _SCALE = 1e-6
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} µF"


class Nanofarads(_Unit):
    __slots__ = ()
    _SCALE = 1e-9
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} nF"


class Picofarads(_Unit):
    __slots__ = ()
    _SCALE = 1e-12
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} pF"
