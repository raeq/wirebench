"""Universal bench warnings emitted by the assembly-guide exporter.

These apply to *every* breadboard build regardless of which components
the design uses.  Per-component gotchas live on each component class's
`GOTCHAS` ClassVar; this module holds only the universal lessons every
hobbyist needs reminded of.

The exporter prepends these to the per-component gotchas in the
"Notes & Gotchas" section, under a `### General` sub-heading.
"""
from __future__ import annotations


_GENERAL_GOTCHAS: tuple[str, ...] = (
    "**Double-check the supply voltage before powering up.** "
    "Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V "
    "from a bench supply destroys every chip on the board in microseconds. "
    "Set the supply, measure it with a multimeter, and only then connect.",
    "**Resistor wattage matters.** Standard ¼-W carbon-film resistors are "
    "fine below ~60 V across the part. Power resistors (½ W, 1 W) are "
    "needed for current-sense or load-dump positions; the BOM lists value "
    "only, not wattage — confirm against the schematic's expected current.",
    "**Tie unused CMOS inputs.** Any input pin not driven by the circuit "
    "must be wired to VCC or GND. Floating CMOS inputs drift unpredictably "
    "and can cause oscillation, excess supply current, or random behaviour. "
    "If your design has unused gates on a multi-gate chip, ground their "
    "inputs explicitly with a jumper.",
    "**Power-rail continuity.** Some 830-pin breadboards split each "
    "power rail into two segments at the middle of the board, with a "
    "visible break in the colored stripe. If your circuit uses the full "
    "rail length, bridge the gap with a jumper before powering on.",
)


def general_gotchas() -> tuple[str, ...]:
    """Return the universal bench gotchas as a tuple of Markdown
    strings, in stable emission order."""
    return _GENERAL_GOTCHAS
