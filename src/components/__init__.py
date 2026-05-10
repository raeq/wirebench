"""Real-world electronic components.

Two public sub-packages:
  - parts    — chips you'd buy by part number (CD4043, LM393, ULN2003A,
               SN74HC04, CD4069).  Each part exposes only its package
               pins; internal cells are private.
  - passives — resistors, LEDs (capacitors, inductors when added).

The cell-level abstractions a part is built from (NOR latches, tri-state
buffers, comparators) live under `components.parts.concepts` and are
deliberately not re-exported.  Reaching past a part's pins into its
silicon is not part of the consumer API.

Power rails (Vcc / GND ties) live in `framework.rail` — they model the
environment, not a real component.
"""
from .parts    import CD4043, CD4069, LM393, SN74HC04, ULN2003A
from .passives import LED, Resistor
