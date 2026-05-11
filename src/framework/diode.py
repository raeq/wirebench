from __future__ import annotations

from typing import ClassVar

from framework.factor import FactorNode


class Diode(FactorNode):
    """Two-terminal rectifier — silicon, Schottky, or Zener.

    A black-box marker class: subclasses provide `anode` and `cathode`
    ports plus PIN_NUMBERS (1=anode, 2=cathode by convention).  No
    behavioural model — `evaluate` is a no-op.  SPICE emits a `.MODEL`
    reference by the class name; substitute a vendor model in
    `spice-models.lib` for accurate IV curves and breakdown behaviour.

    Zener diodes share this base class — there is no physical difference
    in pinout, only in how the device is biased.
    """

    __slots__ = ()

    REFDES_PREFIX: ClassVar[str] = 'D'
