"""Real-world electronic components.

`parts` is the public API: things you'd put on a BOM (chips like CD4043,
LM393, ULN2003A, SN74HC04, CD4069). Each part presents only its package
pins as a port surface.

The cell-level abstractions a part is built from (NOR latches, tri-state
buffers, comparators, and primitive discretes like LED / Resistor /
Rail) live under `components.parts.concepts` and are deliberately *not*
re-exported here or from `parts`. Reaching past a part's pins into its
silicon is not part of the consumer API; deep imports are the price of
admission.
"""
from .parts import CD4043, CD4069, LM393, SN74HC04, ULN2003A
