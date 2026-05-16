"""Deterministic placement of breadboard parts.

For each refdes-bearing top-level component in a design, decide
*which* breadboard positions (1–63) and *which* rows (A–E or F–J) the
component's pins land at.  The algorithm is intentionally simple — its
output is "legible at the bench," not "optimal under any cost
function."  The placement is fully deterministic so golden tests can
assert byte-identical output run-to-run.

Coordinate system:

  - Positions 1–63 run along the long axis of the board.
  - Rows A–E sit above the trough; rows F–J sit below.
  - All five A–E holes of one position share a tie strip (one net).
  - All five F–J holes of one position share a separate tie strip.
  - The trough between row E and row F isolates the upper and lower
    tie strips of the same position.

Placement strategy:

  1. Chips straddle the trough, biggest first, starting at position 10.
     A DIP-N chip occupies positions p..p+N/2-1.  A 2-position gap
     follows before the next chip.
  2. 2-lead parts (Resistor, LED, Capacitor, Diode, Inductor) take the
     next free position pair after the chips.
  3. Each lead lands in a distinct tie strip (different position).
  4. Rails are not physically placed — they're the supply / ground
     strips along the top and bottom of the board.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from framework.chip import Chip
from framework.part import Part


# Single position number where the first chip's pin 1 lands.
_FIRST_CHIP_POSITION = 10
# Number of empty positions between adjacent chips (so jumpers can
# travel between them without piling up on the same tie strips).
_CHIP_GAP = 2
# Starting position for 2-lead parts placed to the right of the chip
# block.  Updated as parts are placed.
_PASSIVES_START_OFFSET = 2


@dataclass(frozen=True, slots=True)
class PinPlacement:
    """The breadboard position and row a single pin lands at.

    position : int   — 1..63 along the long axis
    row      : str   — one of 'A'..'J'
    """
    position: int
    row: str

    def label(self) -> str:
        """Render as a breadboard-coordinate label (e.g. '10E')."""
        return f"{self.position}{self.row}"

    @property
    def tie_strip_label(self) -> str:
        """Render as a tie-strip range label (e.g. 'position 10 (any of 10A–10E)')."""
        if self.row in 'ABCDE':
            return f"position {self.position} (any of {self.position}A–{self.position}E)"
        return f"position {self.position} (any of {self.position}F–{self.position}J)"


@dataclass(frozen=True, slots=True)
class ComponentPlacement:
    """The full placement of one component's pins."""
    component: Part
    pins: tuple[tuple[str, PinPlacement], ...]   # (pin_name, placement)

    def pin(self, name: str) -> PinPlacement | None:
        for n, p in self.pins:
            if n == name:
                return p
        return None


def _place_dip(start: int, pin_count: int) -> tuple[tuple[int, str], ...]:
    """Return (position, row) tuples for pins 1..pin_count of a DIP-N chip
    starting at `start`.  Pin 1 lands at (start, 'E').  Pins 1..N/2 run
    above the trough left-to-right; pins N/2+1..N return below the
    trough right-to-left.  Pin N is at (start, 'F'), opposite pin 1
    across the trough."""
    if pin_count % 2 != 0:
        # Datasheets always pair pin counts on DIPs (DIP-8, DIP-14, …).
        # If a chip ever declares an odd count, fall back to a sensible
        # placement so the exporter doesn't crash on a malformed design.
        pin_count = pin_count + 1
    half = pin_count // 2
    result: list[tuple[int, str]] = []
    for i in range(half):
        result.append((start + i, 'E'))
    for i in range(half):
        result.append((start + half - 1 - i, 'F'))
    return tuple(result)


def chip_pin_count(chip: Chip) -> int:
    """How many pins the chip's physical DIP package has.

    Many classes don't model every pad (CMOS chips routinely omit
    their Vdd / Vss supply pins, for example).  Parsing the FOOTPRINT
    string `Package_DIP:DIP-N_…` gives the package's pin count
    directly; falling back to the max modeled pin number covers
    classes whose FOOTPRINT is non-standard."""
    fp = chip.FOOTPRINT
    if fp:
        import re
        m = re.search(r'DIP-(\d+)', fp)
        if m:
            return int(m.group(1))
    return max((p.id.number for p in chip.pins), default=0)


def _place_chips(chips: list[Chip]) -> tuple[list[ComponentPlacement], int]:
    """Place every chip in `chips` left-to-right starting at position
    _FIRST_CHIP_POSITION.  Returns (placements, next_free_position).

    Pins are mapped from their datasheet pin number directly to the
    physical-package coordinate slot — so a chip that doesn't model
    every pad (e.g. ULN2003A omits GND/COMMON) gets the *modeled* pins
    at their datasheet positions, leaving the missing slots simply
    unmentioned in the assembly steps.

    Off-board chips (Arduino Uno boards and similar) are placed with
    an empty pin tuple: they don't occupy a breadboard position; their
    headers receive jumpers but the board itself sits beside the
    breadboard.  No `_CHIP_GAP` reservation either — the next on-board
    chip starts at the same position the Uno would have used."""
    from framework.export.assembly_guide.layout import is_arduino_uno
    placements: list[ComponentPlacement] = []
    next_pos = _FIRST_CHIP_POSITION
    for chip in chips:
        if is_arduino_uno(chip):
            # Off-board: no pin placements, no position reserved.
            placements.append(ComponentPlacement(chip, ()))
            continue
        pin_count = chip_pin_count(chip)
        if pin_count % 2 != 0:
            # SIP: a single row of pins, all on the upper half of the
            # breadboard.  Can't straddle the trough — there'd be
            # no way to split an odd pin count evenly.  Pin 1 lands
            # at `next_pos` row 'E'; subsequent pins march right
            # along row 'E'.
            per_pin: list[tuple[str, PinPlacement]] = []
            for pin in sorted(chip.pins, key=lambda p: p.id.number):
                idx = pin.id.number - 1
                if 0 <= idx < pin_count:
                    per_pin.append(
                        (pin.id.name, PinPlacement(next_pos + idx, 'E'))
                    )
            placements.append(ComponentPlacement(chip, tuple(per_pin)))
            next_pos = next_pos + pin_count + _CHIP_GAP
            continue
        coords = _place_dip(next_pos, pin_count)
        per_pin = []
        for pin in sorted(chip.pins, key=lambda p: p.id.number):
            idx = pin.id.number - 1
            if 0 <= idx < len(coords):
                pos, row = coords[idx]
                per_pin.append((pin.id.name, PinPlacement(pos, row)))
        placements.append(ComponentPlacement(chip, tuple(per_pin)))
        next_pos = next_pos + max(pin_count // 2, 1) + _CHIP_GAP
    return placements, next_pos


def _place_2lead_part(
    component: Part,
    start_pos: int,
    spacing: int,
) -> tuple[ComponentPlacement, int]:
    """Place a 2-lead through-hole part with leads at `start_pos` and
    `start_pos + spacing`.  Both leads land above the trough (row 'A')
    so the user can see the part orientation at a glance.  Returns
    (placement, next_free_position)."""
    port_names = list(component.ports.keys())
    placements: list[tuple[str, PinPlacement]] = []
    for i, name in enumerate(port_names[:2]):
        placements.append((name, PinPlacement(start_pos + i * spacing, 'A')))
    next_pos = start_pos + spacing + 1
    return ComponentPlacement(component, tuple(placements)), next_pos


def place(
    chips: Iterable[Chip],
    passives_2lead: Iterable[Part],
) -> tuple[ComponentPlacement, ...]:
    """Deterministically place every component.

    `chips` are placed first (biggest first); `passives_2lead` after,
    each taking the next available position with spacing derived from
    their `LAYOUT.lead_spacing_holes` (defaulting to 1)."""
    chip_list = sorted(chips, key=lambda c: -chip_pin_count(c))
    chip_placements, next_pos = _place_chips(chip_list)
    next_pos = next_pos + _PASSIVES_START_OFFSET

    passive_placements: list[ComponentPlacement] = []
    for part in passives_2lead:
        layout = type(part).LAYOUT or {}
        spacing = int(layout.get('lead_spacing_holes', 1))
        # Make sure the part actually has 2 ports — otherwise skip.
        if len(part.ports) < 2:
            continue
        placement, next_pos = _place_2lead_part(part, next_pos, spacing)
        passive_placements.append(placement)
        # 1-position gap between adjacent 2-lead parts.
        next_pos += 1

    return tuple(chip_placements) + tuple(passive_placements)
