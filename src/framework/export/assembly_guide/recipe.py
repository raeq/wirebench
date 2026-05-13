"""Assemble the assembly-guide Markdown for one design.

The document structure is:

    # Build Guide: <DesignName>
    <optional one-paragraph description from the design's class docstring>

    ## Safety first
    <three universal bench-safety bullets>

    ## Parts
    <parts table + free-form prose for non-electronic items>

    ## How to verify
    <generic intro paragraph, then per-component multimeter checks
     so DOA parts are caught before they go on the breadboard>

    ## Method
    <numbered build steps>

    ## Notes & Gotchas
    <general bullets, then per-component bullets>

The Testing section is intentionally omitted in v1 — most designs
don't expose a self-describing test surface.

This module owns the structural assembly; placement details live in
`placement.py`; universal gotchas in `general_gotchas.py`.
"""
from __future__ import annotations

import textwrap
from collections import OrderedDict
from typing import Iterable

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.errors import BreadboardIncompatibleError
from framework.factor import FactorNode
from framework.pin import Pin
from framework.port import Port

from framework.export.assembly_guide.general_gotchas import general_gotchas
from framework.export.assembly_guide.placement import (
    ComponentPlacement, PinPlacement, chip_pin_count, place,
)


# ----------------------------------------------------------------- helpers


def _is_rail(node: FactorNode) -> bool:
    from components.passives.rail import Rail
    return isinstance(node, Rail)


def _refdes_or_none(node: FactorNode) -> str | None:
    return getattr(node, 'refdes', None)


def _walk_top_parts(design: FactorNode) -> list[FactorNode]:
    """Collect every top-level leaf part in `design`, including Rails.

    Chips and Boards aren't descended into — each is one part on the
    BOM.  Raw `Circuit` composites (the user's top-level design class)
    ARE descended into so their contained leaves appear.  Rails are
    kept so the jumper-generation step can detect rail nets; the
    Parts table filters them out later."""
    parts: list[FactorNode] = []
    stack: list[FactorNode] = [design]
    while stack:
        node = stack.pop(0)
        if isinstance(node, Board):
            parts.append(node)
            continue
        if isinstance(node, Chip):
            parts.append(node)
            continue
        if isinstance(node, Circuit):
            for child in node._factor_nodes:
                stack.append(child)
            continue
        # Leaf component — keep Rails, drop other refdes-less leaves
        # (Pin faces, internal concept cells, etc.).
        if _is_rail(node) or _refdes_or_none(node) is not None:
            parts.append(node)
    return parts


# ------------------------------------------------------------- refusal


def _check_breadboard_compatible(parts: list[FactorNode], design: FactorNode) -> None:
    """Raise `BreadboardIncompatibleError` if `parts` contains any
    SMD / multi-board / otherwise-unassemblable component.

    Also refuses any top-level `Board` or multi-board design, per spec
    §10 — multi-board assemblies aren't usefully built on a single
    breadboard."""
    if isinstance(design, Board):
        raise BreadboardIncompatibleError(
            "The assembly-guide exporter renders single-circuit designs onto "
            "a standard 830-pin solderless breadboard. The top-level design "
            f"is a Board ({type(design).__name__}) — a populated PCB. Use "
            "`export(board.circuit, 'assembly_guide', …)` to assemble the "
            "board's internal circuit, or use the `kicad` exporter for PCB "
            "layout."
        )
    nested_boards = [p for p in parts if isinstance(p, Board)]
    if nested_boards:
        raise BreadboardIncompatibleError(
            f"Multi-board design (top level is a {type(design).__name__} "
            f"containing {len(nested_boards)} Boards). Multi-board "
            "assemblies aren't usefully built on a single breadboard. "
            "Export each board's internal circuit separately."
        )
    incompat = [p for p in parts if not p.is_breadboard_compatible]
    if incompat:
        lines = [
            f"{len(incompat)} part"
            f"{'s' if len(incompat) != 1 else ''} "
            f"can't be assembled on a breadboard:"
        ]
        for p in incompat:
            refdes = getattr(p, 'refdes', '<no-refdes>')
            cls = type(p).__name__
            fp = getattr(p, 'FOOTPRINT', None) or '(no footprint)'
            lines.append(f"  - {refdes} ({cls}) — {fp}")
        lines.append("")
        lines.append(
            "Use `export(<design>, 'kicad', …)` for a PCB netlist, or rework "
            "the design with breadboard-friendly part variants (DIP packages, "
            "THT passives, 0.1\" headers)."
        )
        raise BreadboardIncompatibleError('\n'.join(lines))


# ------------------------------------------------------------ ingredients


def _value_for_bom(part: FactorNode) -> str:
    """Format the BOM 'Value / Spec' column for one part."""
    from components.passives.resistor import Resistor
    from components.passives.capacitor import Capacitor
    from components.passives.inductor import Inductor
    from components.passives.led import LED
    if isinstance(part, Resistor):
        return f"{int(part.ohms)} Ω" if int(part.ohms) == float(part.ohms) else f"{float(part.ohms):g} Ω"
    if isinstance(part, Capacitor):
        return _format_capacitance(float(part.farads))
    if isinstance(part, Inductor):
        return _format_inductance(float(part.henries))
    if isinstance(part, LED):
        return f"{part.color}, 5 mm"
    # Chips and others — just the class name as a spec.
    return type(part).__name__


def _format_capacitance(farads: float) -> str:
    if farads >= 1e-6:
        return f"{farads * 1e6:g} µF"
    if farads >= 1e-9:
        return f"{farads * 1e9:g} nF"
    return f"{farads * 1e12:g} pF"


def _format_inductance(henries: float) -> str:
    if henries >= 1e-3:
        return f"{henries * 1e3:g} mH"
    return f"{henries * 1e6:g} µH"


def _bom_note(part: FactorNode) -> str:
    """One-line note for the BOM row.  Common hints — polarity, lead
    notes, package style — to ease procurement at the bench."""
    from components.passives.led import LED
    from components.passives.resistor import Resistor
    if isinstance(part, LED):
        return "Longer lead is the anode (+)"
    if isinstance(part, Resistor):
        return "¼ W carbon film is fine"
    return ""


def _ingredients_section(parts: list[FactorNode]) -> str:
    """Build the Parts section: a Markdown table + free-form
    prose listing non-electronic items."""
    lines: list[str] = [
        "## Parts", "",
        "| Refdes | Part | Value / Spec | Quantity | Notes |",
        "|--------|------|--------------|----------|-------|",
    ]
    # One row per part, sorted by refdes (alphabetical prefix, then
    # numeric suffix — same convention as the BOM exporter).
    def sort_key(p: FactorNode) -> tuple[str, int]:
        rd = p.refdes
        prefix = rd.rstrip('0123456789')
        n = rd[len(prefix):]
        return (prefix, int(n) if n else 0)

    for part in sorted(parts, key=sort_key):
        refdes = part.refdes
        cls = type(part).__name__
        val = _value_for_bom(part)
        note = _bom_note(part)
        lines.append(f"| {refdes} | {cls} | {val} | 1 | {note} |")

    lines.append("")
    lines.append(
        "Also: a standard 830-pin solderless breadboard, an assortment of "
        "jumper wires (red for the positive rail, black for ground rail, "
        "any colour for signals), and a 5 V supply."
    )
    return '\n'.join(lines)


# ----------------------------------------------------------------- method


def _supply_step() -> str:
    return (
        "Orient the breadboard with its long axis horizontal and the trough "
        "running left-to-right through the middle. Connect your 5 V supply: "
        "the positive lead to the top `+` rail (positive rail), the negative "
        "lead to the top `-` rail (ground rail)."
    )


def _chip_step(placement: ComponentPlacement) -> str:
    assert isinstance(placement.component, Chip)
    chip: Chip = placement.component
    package_pin_count = chip_pin_count(chip)
    # Some classes model only a subset of their package's pins (e.g.
    # ULN2003A skips GND/COMMON). The breadboard layout still spans
    # the *physical* DIP outline; report pin 1 and the last *modeled*
    # corner pin so the user has unambiguous anchors at the bench.
    pin1 = placement.pin(_pin_name_by_number(chip, 1))
    # Find the largest-numbered modeled pin we actually have a
    # placement for — that's the chip's bottom-left anchor.
    last_modeled = max((n for n, _ in placement.pins
                        if _pin_number_for_name(chip, n) is not None),
                       key=lambda n: _pin_number_for_name(chip, n) or 0,
                       default=None)
    if pin1 is None or last_modeled is None:
        return f"Plug {chip.refdes} ({type(chip).__name__}) into the breadboard."
    last = placement.pin(last_modeled)
    last_n = _pin_number_for_name(chip, last_modeled)
    if last is None or last_n is None:
        return f"Plug {chip.refdes} ({type(chip).__name__}) into the breadboard."
    return (
        f"Plug {chip.refdes} ({type(chip).__name__}, DIP-{package_pin_count}) "
        f"straddling the trough: pin 1 at {pin1.label()}, "
        f"pin {last_n} at {last.label()}. "
        f"The chip's notch / dot marks pin 1 — make sure it lines up."
    )


def _pin_number_for_name(chip: Chip, name: str) -> int | None:
    for pin in chip.pins:
        if pin.id.name == name:
            return int(pin.id.number)
    return None


def _pin_name_by_number(chip: Chip, n: int) -> str:
    for pin in chip.pins:
        if pin.id.number == n:
            return pin.id.name
    return ""


def _passive_step(placement: ComponentPlacement) -> str:
    part = placement.component
    cls = type(part).__name__
    if len(placement.pins) < 2:
        return f"Plug {part.refdes} ({cls}) into the breadboard."
    (n1, p1), (n2, p2) = placement.pins[0], placement.pins[1]
    return (
        f"Plug {part.refdes} ({cls}): one lead at "
        f"{p1.tie_strip_label}, the other at {p2.tie_strip_label}."
    )


def _jumper_steps(
    all_parts: list[FactorNode],
    placeable_parts: list[FactorNode],
    placements: dict[int, ComponentPlacement],
) -> list[str]:
    """Generate jumper instructions per logical net.

    `all_parts` includes Rails so rail-net detection works; `placeable_parts`
    excludes Rails (they're not physical and have no breadboard position).

    Every net gets walked once.  Nets containing a Rail are emitted as
    "to the top + rail" / "to the top - rail" jumpers, one per
    non-Rail endpoint.  Signal nets get chained jumpers between
    successive endpoints (a–b, b–c).  The placement algorithm does
    not co-locate same-net leads, so each net's parts genuinely need
    wires between them at the bench."""
    from components.passives.rail import Rail
    steps: list[str] = []
    # Port → tie-strip label for placeable parts only.
    port_to_label: dict[int, str] = {}
    for placement in placements.values():
        comp = placement.component
        for name, pin_place in placement.pins:
            try:
                port = comp.ports[name]
            except (KeyError, TypeError):
                continue
            port_to_label[id(port)] = pin_place.tie_strip_label

    # Build port → owner FactorNode lookup so we can spot rail-owned
    # ports without relying on Port._owner (which is only set for Pin
    # faces).
    port_owner: dict[int, FactorNode] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        for port in part.ports.values():
            port_owner[id(port)] = part

    # Collapse ports by Node — every port on the same node is on the
    # same logical net.  Include Rails so we can detect rail nets.
    node_to_ports: dict[int, list[Port]] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        for port in part.ports.values():
            if port.node is None:
                continue
            node_to_ports.setdefault(id(port.node), []).append(port)

    # Sort nets by a stable key derived from their ports — `id(node)`
    # changes run-to-run, so we use (sorted port refdes, port name)
    # tuples to deterministically order the emitted jumper steps.
    def _net_key(nid: int) -> tuple[tuple[str, str], ...]:
        ps = node_to_ports[nid]
        return tuple(sorted(
            (getattr(port_owner.get(id(p)), 'refdes', '') or
             type(port_owner.get(id(p), object)).__name__,
             p.name)
            for p in ps
        ))

    for nid in sorted(node_to_ports.keys(), key=_net_key):
        ports = node_to_ports[nid]
        rail_polarity: bool | None = None
        for p in ports:
            owner = port_owner.get(id(p))
            if isinstance(owner, Rail):
                rail_polarity = bool(owner.level)
                break
        labels = [port_to_label[id(p)] for p in ports if id(p) in port_to_label]
        labels = sorted(set(labels))
        if rail_polarity is not None and labels:
            rail_name = "top `+` rail" if rail_polarity else "top `-` rail"
            for label in labels:
                steps.append(
                    f"Run a jumper from {label} to the {rail_name}."
                )
        elif len(labels) >= 2:
            for i in range(len(labels) - 1):
                steps.append(
                    f"Run a jumper from {labels[i]} to {labels[i+1]}."
                )
    return steps


def _net_rail_polarity(ports: Iterable[Port]) -> bool | None:
    """Return True if any port on this net is owned by a HIGH Rail,
    False for a LOW Rail, or None for a signal net."""
    from components.passives.rail import Rail
    for p in ports:
        owner = p._owner
        if isinstance(owner, Rail):
            return bool(owner.level)
    return None


def _method_section(
    all_parts: list[FactorNode],
    placeable_parts: list[FactorNode],
    placements: tuple[ComponentPlacement, ...],
) -> str:
    """Build the numbered Method section."""
    lines: list[str] = ["## Method", ""]
    n = 1

    def step(text: str) -> None:
        nonlocal n
        # Wrap each step to keep the source readable; Markdown joins
        # lines within one list item.
        wrapped = textwrap.fill(text, width=78,
                                initial_indent=f"{n}. ",
                                subsequent_indent="   ")
        lines.append(wrapped)
        n += 1

    step(_supply_step())

    place_by_id: dict[int, ComponentPlacement] = {
        id(p.component): p for p in placements
    }
    # Chip steps first.
    for placement in placements:
        if isinstance(placement.component, Chip):
            step(_chip_step(placement))

    # Then 2-lead passive parts.
    for placement in placements:
        if not isinstance(placement.component, Chip):
            step(_passive_step(placement))

    # Jumper steps.
    for jumper in _jumper_steps(all_parts, placeable_parts, place_by_id):
        step(jumper)

    step(
        "Verify nothing is shorted by inspecting the rails with a multimeter "
        "(continuity beep between `+` and `-` means trouble). Then connect "
        "the supply and observe."
    )
    return '\n'.join(lines)


# --------------------------------------------------------- notes & gotchas


def _verify_section(parts: list[FactorNode]) -> str:
    """How-to-verify section: per-component pre-install multimeter checks.

    Emits an empty-but-titled section even when no part contributes a
    `VERIFY` tuple — the heading documents the missing surface rather
    than hiding it.  Per-component bullets are deduplicated and ordered
    by class name + tuple index so output is deterministic for the
    goldens."""
    lines: list[str] = [
        "## How to verify",
        "",
        "Before you start wiring, take five minutes to confirm each part "
        "actually works. A multimeter on the diode-test and resistance "
        "settings catches most pre-install failures: dead LEDs, "
        "mis-bagged parts, transistors damaged in shipping, batteries "
        "below their safe-discharge limit. The checks below cover what "
        "you can verify with a basic multimeter; chips and complex "
        "modules generally need a working test rig instead, so they're "
        "not listed here.",
        "",
    ]
    seen: OrderedDict[tuple[str, int], str] = OrderedDict()
    parts_sorted = sorted(parts, key=lambda p: (type(p).__name__, p.refdes))
    for part in parts_sorted:
        cls = type(part)
        checks = getattr(cls, 'VERIFY', ())
        for i, c in enumerate(checks):
            key = (cls.__name__, i)
            seen.setdefault(key, c)
    if seen:
        for c in seen.values():
            lines.append(f"- {c}")
    else:
        lines.append(
            "*(No standalone bench checks declared for the parts in this "
            "design — proceed directly to assembly and watch for trouble "
            "during the first power-up.)*"
        )
    return '\n'.join(lines).rstrip() + '\n'


def _notes_section(parts: list[FactorNode]) -> str:
    """Notes & Gotchas section: universal warnings first, then unique
    per-component warnings collected across the parts list."""
    lines: list[str] = ["## Notes & Gotchas", "", "### General", ""]
    for g in general_gotchas():
        lines.append(f"- {g}")
    lines.append("")

    # Collect per-component gotchas, deduplicated.  Iterate parts in
    # sorted order (by class name then refdes) so the emission is
    # deterministic for the golden tests.
    seen: OrderedDict[tuple[str, int], str] = OrderedDict()
    parts_sorted = sorted(parts, key=lambda p: (type(p).__name__, p.refdes))
    for part in parts_sorted:
        cls = type(part)
        gotchas = getattr(cls, 'GOTCHAS', ())
        for i, g in enumerate(gotchas):
            key = (cls.__name__, i)
            seen.setdefault(key, g)

    if seen:
        lines.append("### Per-component")
        lines.append("")
        for g in seen.values():
            lines.append(f"- {g}")

    return '\n'.join(lines).rstrip() + '\n'


# ----------------------------------------------------------------- top


def _design_blurb(design: FactorNode) -> str:
    """Optional one-line description pulled from the design's class
    docstring (the first non-blank line)."""
    doc = (type(design).__doc__ or '').strip()
    if not doc:
        return ""
    return doc.splitlines()[0].strip()


def build_recipe(design: FactorNode) -> str:
    """Assemble the full assembly-guide Markdown for `design`.

    Raises `BreadboardIncompatibleError` per spec §5.5 if any part is
    SMD-only or the top-level design is a multi-board assembly."""
    parts = _walk_top_parts(design)
    # Filter out Rails — they're nets, not physical parts.
    placeable = [p for p in parts if not _is_rail(p)]
    _check_breadboard_compatible(placeable, design)

    chips = [p for p in placeable if isinstance(p, Chip)]
    passives = [p for p in placeable if not isinstance(p, Chip)]
    placements = place(chips, passives)

    title = type(design).__name__
    blurb = _design_blurb(design)
    sections: list[str] = [f"# Build Guide: {title}", ""]
    if blurb:
        sections.append(blurb)
        sections.append("")
    sections.append(_safety_section())
    sections.append("")
    sections.append(_ingredients_section(placeable))
    sections.append("")
    sections.append(_verify_section(placeable))
    sections.append("")
    sections.append(_method_section(parts, placeable, placements))
    sections.append("")
    sections.append(_notes_section(placeable))
    return '\n'.join(sections).rstrip() + '\n'


def _safety_section() -> str:
    """Universal bench-safety preamble emitted before the parts list.

    Three baseline protections every engineer at the bench should put
    on regardless of the design: eye protection, ESD precautions, and
    insulating gloves. These are non-negotiable; the bullets follow the
    progressive-disclosure pattern (do-this → why → expert nuance) so
    a first-time builder isn't put off and an experienced one isn't
    patronised."""
    return '\n'.join([
        "## Safety first",
        "",
        "- **Put on safety glasses before powering anything up.** "
        "Electrolytic capacitors can vent boiling electrolyte if "
        "reverse-installed or over-volted; battery cells can flash "
        "violently on a short; small parts under tension (springs in "
        "switches, leads under a soldering iron) launch in unexpected "
        "directions. The glasses are cheap insurance against an "
        "afternoon you'd otherwise regret.",
        "- **Discharge static before touching chips.** Touch a grounded "
        "metal surface (the bench frame, a radiator, the case of a "
        "mains-powered tool that's plugged in but switched off) before "
        "picking up MOSFETs or CMOS logic. A static spark you can't "
        "feel — under 100 V from walking across a carpet — punches "
        "through a gate oxide silently. The part still looks fine; it "
        "just doesn't work, and you spend two hours blaming your wiring. "
        "An ESD wrist strap clipped to a grounded surface is the "
        "permanent fix.",
        "- **Wear insulating gloves when working above ~30 V or near "
        "mains.** Standard hobby breadboard work (3.3–24 V) doesn't "
        "need them; anything reaching into a wall-wart's primary side, "
        "a charged high-voltage capacitor, or a tube-amp B+ rail does. "
        "If the design includes a transformer, a switching supply's "
        "input stage, or a Cell pack above a few volts, treat it as "
        "hot until you've personally verified it's discharged.",
    ])
