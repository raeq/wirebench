"""ASCII pinout diagrams for the assembly-guide Layout section.

For each placed part in a design we draw a compact top-down outline
that labels every pin or terminal.  The renderer picks a path based on
the part shape:

- Chip with an even pin count: DIP-style outline with the notch at
  the top, pin numbers in the centre column, and names flanking left
  and right.  Pin 1 is top-left, pin N top-right, descending each
  side — the convention every datasheet uses.
- Chip with an odd pin count (SIP-style sensors like the DHT11): a
  horizontal bar with the package label inside and pin numbers /
  names dropping out the bottom.
- 2-lead passive (Resistor, LED, Capacitor, Inductor, Diode): a
  single-line axial drawing with the value inlined.

The output of every renderer is a plain string with no Markdown
fencing — the caller wraps it in a fenced block so it renders in
monospace.
"""
from __future__ import annotations

import re

from framework.chip import Chip
from framework.part import Part

from framework.export.assembly_guide.placement import chip_pin_count


# Standard Arduino Uno R3 header layout — used when a Uno-prefixed
# chip subclass is encountered.  Pin names mirror the silkscreen on
# a real board; parenthesised names show the underlying ATmega328P
# pin so the builder can cross-reference jumper instructions that
# call out chip-level names elsewhere in the doc.
_UNO_HEADER_PANEL = """\
Arduino Uno R3 header pinout (top-down view, USB jack on the left):

         SCL  SDA  AREF GND  D13  D12  D11  D10  D9   D8       D7   D6   D5   D4   D3   D2   D1   D0
                            (PB5)(PB4)(PB3)(PB2)(PB1)(PB0)   (PD7)(PD6)(PD5)(PD4)(PD3)(PD2)(TX) (RX)
       ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  USB ─┤                                       Arduino Uno R3                                         │
       └──────────────────────────────────────────────────────────────────────────────────────────────┘
        IOREF RST  3.3V 5V   GND  GND  Vin                     A0   A1   A2   A3   A4   A5
                            (VCC)                            (PC0)(PC1)(PC2)(PC3)(SDA)(SCL)"""


# ATmega328P chip pin → Arduino Uno R3 header label.  When a jumper
# step lands on a Uno-prefixed chip, the framework's chip-level pin
# names (PD3, PB5, …) are translated to the labels the builder reads
# on the physical board (3, 13, …) so the instructions match the
# silkscreen.
_ATMEGA_TO_UNO_HEADER: dict[str, str] = {
    'PC6':  'RESET',
    'PD0':  'D0',  'PD1':  'D1',  'PD2':  'D2',  'PD3':  'D3',
    'PD4':  'D4',  'PD5':  'D5',  'PD6':  'D6',  'PD7':  'D7',
    'PB0':  'D8',  'PB1':  'D9',  'PB2':  'D10', 'PB3':  'D11',
    'PB4':  'D12', 'PB5':  'D13',
    'PC0':  'A0',  'PC1':  'A1',  'PC2':  'A2',  'PC3':  'A3',
    'PC4':  'A4',  'PC5':  'A5',
    'VCC':  '5V',  'AVCC': '5V',
    'GND':  'GND',
    'AREF': 'AREF',
}


def is_arduino_uno(part: Part) -> bool:
    """True if `part` is an Arduino Uno board (Uno-prefixed ATmega328P).

    The convention in this repo is to subclass `ATmega328P` with a
    `Uno_` class-name prefix when the design's intent is "the chip
    sits on an Arduino Uno board" rather than "the chip sits on a
    breadboard."  That distinction matters for assembly: the bare
    DIP plugs into the breadboard, but the Uno board doesn't fit —
    it sits beside the breadboard, with jumpers running into its
    header sockets."""
    return type(part).__name__.startswith('Uno_')


def uno_header_label(mcu_pin_name: str) -> str:
    """Map an ATmega328P pin name to its Arduino Uno header label.

    Unknown pins fall back to the MCU name unchanged."""
    return _ATMEGA_TO_UNO_HEADER.get(mcu_pin_name, mcu_pin_name)


def _dip_size_from_footprint(footprint: str | None) -> int | None:
    """Return N if FOOTPRINT names a DIP-N package, else None.

    Used as a tie-breaker only — the renderer picks DIP vs SIP from
    the modeled pin count, not the footprint string."""
    if not footprint:
        return None
    m = re.search(r'DIP-(\d+)', footprint)
    return int(m.group(1)) if m else None


def _dip_diagram(chip: Chip, pin_count: int) -> str:
    """Render a DIP-N outline in landscape (left-to-right) orientation.

    Matches the chip's physical pose on a breadboard: the package's
    long axis runs horizontally, the notch is on the left, pin 1 is
    top-left, the rest of the top edge holds pins 2..N/2, and the
    bottom edge holds pins N..N/2+1 (reading left-to-right).  Pin
    names sit immediately above / below the package; pin numbers are
    one row further out so the builder reads `1` and `PC6` together
    at the top-left of the chip."""
    name_by_num: dict[int, str] = {p.id.number: p.id.name for p in chip.pins}
    names = [name_by_num.get(i, '—') for i in range(1, pin_count + 1)]
    half = pin_count // 2
    top_names = names[:half]
    bot_names = list(reversed(names[half:]))
    top_nums = list(range(1, half + 1))
    bot_nums = list(range(pin_count, half, -1))

    # +2 keeps a clear gap between adjacent names — single-space gaps
    # crowd 4-character names like AREF/AVCC together.
    cell = max(
        max(len(n) for n in top_names + bot_names),
        len(str(pin_count)),
    ) + 2
    inner = half * cell
    label = type(chip).__name__

    def cr(items: list[str]) -> str:
        """Centre each item within its cell column."""
        row = [' '] * inner
        for i, t in enumerate(items):
            mid = i * cell + cell // 2
            start = mid - len(t) // 2
            for j, ch in enumerate(t):
                if 0 <= start + j < len(row):
                    row[start + j] = ch
        return ''.join(row)

    pad = "    "       # 4-char left margin so the notch indicator fits
    lines = [
        f"{pad} {cr([str(n) for n in top_nums])}",
        f"{pad} {cr(top_names)}",
        f"{pad}┌{'─' * inner}┐",
        f"  U │{label.center(inner)}│",
        f"{pad}└{'─' * inner}┘",
        f"{pad} {cr(bot_names)}",
        f"{pad} {cr([str(n) for n in bot_nums])}",
    ]
    return '\n'.join(lines)


def _sip_diagram(chip: Chip, pin_count: int) -> str:
    """Render a SIP-style horizontal bar with pin numbers / names below.

    Used for parts whose physical pinout is a single row of pads
    (DHT11 is a 4-pin SIP).  Pin 1 is at the left."""
    name_by_num: dict[int, str] = {p.id.number: p.id.name for p in chip.pins}
    names = [name_by_num.get(i, '—') for i in range(1, pin_count + 1)]
    label = type(chip).__name__
    cell = max(max(len(n) for n in names), len(str(pin_count)), 4) + 2

    width = pin_count * cell
    top = f"┌{'─' * width}┐"
    body = f"│{label.center(width)}│"
    edge = "└" + "".join("┬" + "─" * (cell - 1) for _ in range(pin_count)) + "┘"

    def labelled_row(texts: list[str]) -> str:
        """Place each text centred on the `┬` tap for its pin (the
        column directly under the box edge's downward tick mark)."""
        row = [' '] * (width + 2)
        for i, t in enumerate(texts):
            center = 1 + i * cell    # column of the `┬` for pin i+1
            start = center - len(t) // 2
            for j, ch in enumerate(t):
                if 0 <= start + j < len(row):
                    row[start + j] = ch
        return ''.join(row).rstrip()

    pin_row = labelled_row([str(i + 1) for i in range(pin_count)])
    name_row = labelled_row(names)
    return '\n'.join([top, body, edge, pin_row, name_row])


def _two_lead_diagram(part: Part, value: str) -> str:
    """Single-line drawing of a 2-lead axial part with the value inlined."""
    from components.passives.led import LED
    from components.passives.capacitor import Capacitor
    from framework.diode import Diode
    port_names = list(part.ports.keys())[:2]
    if len(port_names) < 2:
        return ""
    p1, p2 = port_names
    if isinstance(part, LED):
        return f"{p1} (+, long lead) ─▶├─ {p2} (−, short lead)   [{value}]"
    if isinstance(part, Diode):
        return f"{p1} ─▶├─ {p2}   [{value}]"
    if isinstance(part, Capacitor):
        return f"{p1} ─┤├─ {p2}   [{value}]"
    # Resistor / Inductor / generic: value sits in the body.
    return f"{p1} ─┤▮ {value} ▮├─ {p2}"


def part_layout(part: Part, value: str) -> str:
    """Return the layout diagram for one part (no code fence).

    `value` is the BOM "Value / Spec" string from the recipe — passed
    in so 2-lead parts can inline it.  An empty string means the part
    has nothing useful to render."""
    from components.passives.rail import Rail
    if isinstance(part, Rail):
        return ""

    if isinstance(part, Chip):
        pin_count = chip_pin_count(part)
        if pin_count == 0:
            return ""
        # Even pin counts always render DIP-style — Display5641AS is a
        # 12-pin display whose physical pinout matches the DIP
        # convention even though its footprint string doesn't say
        # 'DIP'.  Odd counts (rare; SIP sensors) fall back to the
        # horizontal-bar SIP layout.
        if pin_count % 2 == 0:
            # Genuine SIPs would also have an even pin count.  Use the
            # SIP renderer when the footprint advertises a non-DIP
            # package (DHT11: 'Package_TO_SOT_THT:DHT11').
            fp = getattr(part, 'FOOTPRINT', None) or ""
            if _dip_size_from_footprint(fp) is None and 'DIP' not in fp:
                # Single-row SIPs are the only common non-DIP shape
                # we treat specially.  Display_7Segment packages are
                # mechanically DIP-like, so route them through DIP.
                if 'Display' not in fp:
                    return _sip_diagram(part, pin_count)
            dip = _dip_diagram(part, pin_count)
            if is_arduino_uno(part):
                # The chip-level DIP is still informative (so the
                # user can find a pin by datasheet name), but the
                # builder is wiring into Uno headers — append a
                # second panel showing those headers directly.
                return dip + "\n\n" + _UNO_HEADER_PANEL
            return dip
        return _sip_diagram(part, pin_count)

    return _two_lead_diagram(part, value)
