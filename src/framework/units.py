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
        # Canonical engineering notation: 47 Ω, 4.7 kΩ, 10 kΩ,
        # 100 kΩ, 1 MΩ, 10 MΩ, 1 GΩ. Schematic / bench convention
        # — a resistor labelled "10K" or "10 kΩ" reads instantly,
        # while "10000 Ω" forces the reader to count zeros and the
        # raw `:.3g` formatter would emit unreadable scientific
        # form ("1e+04 Ω") for clean kilo / mega multiples.
        v = float(self) / self._SCALE
        if v >= 1e9:
            return f"{v / 1e9:g} GΩ"
        if v >= 1e6:
            return f"{v / 1e6:g} MΩ"
        if v >= 1e3:
            return f"{v / 1e3:g} kΩ"
        return f"{v:g} Ω"


class Kilohms(_Unit):
    __slots__ = ()
    _SCALE = 1e3
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} kΩ"


class Farads(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        # Canonical engineering notation: 100 pF, 22 nF, 100 nF,
        # 1 µF, 10 µF, 470 µF, 1 mF, 1 F. Matches what a bench
        # builder reads off a capacitor body or sees on a schematic.
        # The raw `:.3g` formatter would emit unreadable scientific
        # form ("1e-07 F") for typical small-cap values.
        v = float(self) / self._SCALE
        if v >= 1.0:
            return f"{v:g} F"
        if v >= 1e-3:
            return f"{v * 1e3:g} mF"
        if v >= 1e-6:
            return f"{v * 1e6:g} µF"
        if v >= 1e-9:
            return f"{v * 1e9:g} nF"
        return f"{v * 1e12:g} pF"


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


class Henries(_Unit):
    __slots__ = ()
    _SCALE = 1.0
    def __str__(self) -> str:
        # Canonical engineering notation: 100 nH, 10 µH, 22 mH, 1 H.
        # Matches what a bench builder reads off an inductor body or
        # sees on a schematic.
        v = float(self) / self._SCALE
        if v >= 1.0:
            return f"{v:g} H"
        if v >= 1e-3:
            return f"{v * 1e3:g} mH"
        if v >= 1e-6:
            return f"{v * 1e6:g} µH"
        return f"{v * 1e9:g} nH"


class Millihenries(_Unit):
    __slots__ = ()
    _SCALE = 1e-3
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} mH"


class Microhenries(_Unit):
    __slots__ = ()
    _SCALE = 1e-6
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} µH"


class Nanohenries(_Unit):
    __slots__ = ()
    _SCALE = 1e-9
    def __str__(self) -> str:
        return f"{float(self) / self._SCALE:.3g} nH"
