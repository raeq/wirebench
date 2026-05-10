from __future__ import annotations

from typing import Any


class Analog(float):
    """A continuous electrical signal (voltage, current, etc.)."""
    __slots__ = ()

    def __new__(cls, value: Any = 0.0) -> "Analog":
        return super().__new__(cls, 0.0 if value is None else float(value))


class Digital(int):
    """A discrete logic signal (low/high, False/True)."""
    __slots__ = ()

    def __new__(cls, value: Any = 0) -> "Digital":
        return super().__new__(cls, 0 if value is None else int(bool(value)))

    def __bool__(self) -> bool:
        return self != 0
