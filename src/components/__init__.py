"""Real-world electronic components.

Two public sub-packages:
  - chips    — integrated circuits you'd buy by part number (CD4043,
               LM393, ULN2003A, SN74HC04, CD4069).  Each chip exposes
               only its package pins; internal cells are private.
  - passives — resistors, LEDs, rails (capacitors, inductors when added).

The cell-level abstractions a chip is built from (NOR latches, tri-state
buffers, comparators, inverters, …) live under `components.chips.concepts`
and are deliberately not re-exported.  Reaching past a chip's pins into
its silicon is not part of the consumer API.
"""
from .chips    import CD4043, CD4069, LM393, SN74HC04, ULN2003A
from .passives import LED, Rail, Resistor

__all__ = [
    'CD4043', 'CD4069', 'LM393', 'SN74HC04', 'ULN2003A',
    'LED', 'Rail', 'Resistor',
]
