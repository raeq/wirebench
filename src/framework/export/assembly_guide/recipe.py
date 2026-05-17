"""Assemble the assembly-guide Markdown for one design.

The document structure is:

    # Build Guide: <DesignName>
    <optional one-paragraph description from the design's class docstring>

    ## Safety first
    <three universal bench-safety bullets>

    ## Parts
    <parts table + free-form prose for non-electronic items>

    ## Layout
    <per-part ASCII pinout diagram so the builder can orient each
     component before wiring it>

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
from typing import TYPE_CHECKING, Callable, Iterable

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.errors import BreadboardIncompatibleError
from framework.part import Part
from framework.pin import Pin
from framework.port import Direction, Port

from framework.export.assembly_guide.general_gotchas import general_gotchas
from framework.export.assembly_guide.layout import (
    is_arduino_uno, part_layout, uno_header_label,
)
from framework.export.assembly_guide.placement import (
    ComponentPlacement, chip_pin_count, place,
)
from framework.pin_function import PinFunction

if TYPE_CHECKING:
    from components.passives.rail import Rail


# ----------------------------------------------------------------- helpers


def _is_rail(node: Part) -> bool:
    from components.passives.rail import Rail
    return isinstance(node, Rail)


def _refdes_or_none(node: Part) -> str | None:
    return getattr(node, 'refdes', None)


def _walk_top_parts(design: Part) -> list[Part]:
    """Collect every top-level leaf part in `design`, including Rails.

    Chips and Boards aren't descended into — each is one part on the
    BOM.  Refdes-bearing Circuit composites that aren't the top-level
    design (a composite part that models itself as a small sub-design
    but appears on the BOM as one item) are also treated as single
    leaf parts — descent stops at the refdes boundary.  Raw, refdes-less `Circuit` composites (the
    user's top-level design class itself) ARE descended into so their
    contained leaves appear.  Rails are kept so the jumper-generation
    step can detect rail nets; the Parts table filters them out
    later."""
    parts: list[Part] = []
    stack: list[Part] = [design]
    while stack:
        node = stack.pop(0)
        if isinstance(node, Board):
            parts.append(node)
            continue
        if isinstance(node, Chip):
            parts.append(node)
            continue
        # Composite part with a refdes (e.g., a Diode-as-Circuit
        # wrapping a behavioural cell). Treat as a single leaf part
        # for the BOM and placement — don't recurse into its private
        # internal cells. The top-level design is excluded so its
        # contents still get walked.
        if (node is not design
                and isinstance(node, Circuit)
                and _refdes_or_none(node) is not None):
            parts.append(node)
            continue
        if isinstance(node, Circuit):
            for child in node.parts:
                stack.append(child)
            continue
        # Leaf component — keep Rails, drop other refdes-less leaves
        # (Pin faces, internal concept cells, etc.).
        if _is_rail(node) or _refdes_or_none(node) is not None:
            parts.append(node)
    return parts


# ----------------------------------------------- pin-function ERC helpers


def _build_rail_port_index(
    all_parts: Iterable[Part],
) -> "dict[int, Rail]":
    """Map `id(rail.ports['out'])` → the Rail itself.  The id is the
    cheap key the walker uses to detect "this face on the net is a
    Rail's drive port" without isinstance() checks inside the hot path.
    """
    from components.passives.rail import Rail
    return {id(p.ports['out']): p for p in all_parts if isinstance(p, Rail)}


def _build_port_owner_index(
    all_parts: Iterable[Part],
) -> dict[int, Part]:
    """Map `id(port)` → the leaf `Part` that owns the port.  Used by
    the RESET predicate to walk from a pin's net through a passive
    Resistor to the resistor's opposite terminal."""
    owner: dict[int, Part] = {}
    for p in all_parts:
        ports = getattr(p, 'ports', None)
        if ports is None:
            continue
        # ports may be a PortMap, dict, or other Mapping-shaped thing
        # exposing values().  Both real shapes are iterable that way.
        try:
            for port in ports.values():
                owner[id(port)] = p
        except AttributeError:
            continue
    return owner


# A pin-function predicate decides "is this pin acceptably wired?".
# False means the pin fails the role's rule and a failure-message line
# will be emitted.  True means the rule is satisfied for this pin.
_PinPredicate = Callable[[Pin, Chip], bool]


def _check_chip_pin_function(
    parts: list[Part],
    *,
    function: PinFunction,
    predicate: _PinPredicate,
    error_msg_prefix: str,
    failure_hint: str,
) -> None:
    """Walk every Chip in `parts`; for each pin classified as
    `function`, evaluate `predicate(pin, chip)`. Collect failures and
    raise `BreadboardIncompatibleError` if any.

    Off-board parts (Arduino Uno) are skipped — their pins aren't
    wired to breadboard rails, they're powered through USB / Vin.
    """
    failures: list[str] = []
    for part in parts:
        if not isinstance(part, Chip):
            continue
        if is_arduino_uno(part):
            continue
        for pin in part.pins:
            if type(part).pin_function(pin.id.name) is not function:
                continue
            if not predicate(pin, part):
                failures.append(
                    f"  - {part.refdes} pin {pin.id.number} ({pin.id.name}) "
                    f"[{function.value}] — {failure_hint}"
                )
    if failures:
        raise BreadboardIncompatibleError(
            f"{error_msg_prefix}\n" + '\n'.join(failures)
        )


def _make_rail_predicate(
    rail_port_ids: "dict[int, Rail]", *, want_high: bool,
) -> _PinPredicate:
    """The POWER / GROUND rule: the pin's net must contain a Rail port
    at the matching polarity.  Direct wiring only — Rails feeding
    through passives don't count here (a power pin "behind" a
    series resistor would have unmodelled current limits).
    """
    def pred(pin: Pin, chip: Chip) -> bool:
        node = pin.external.node
        if node is None:
            return False
        for face in node.ports:
            rail = rail_port_ids.get(id(face))
            if rail is not None and bool(rail.level) is want_high:
                return True
        return False
    return pred


def _make_reference_predicate(
    rail_port_ids: "dict[int, Rail]",
) -> _PinPredicate:
    """REFERENCE pin (AREF / VREF / VBG / BG_REF): the net must contain
    a stable analog source.  Accepted sources:
      - any Rail (POWER or GROUND — tying AREF directly to a supply
        rail is the simplest reference configuration)
      - any external OUT-direction port (regulator output, divider
        tap, another chip's REF_OUT) on the same net
    """
    def pred(pin: Pin, chip: Chip) -> bool:
        node = pin.external.node
        if node is None:
            return False
        for face in node.ports:
            if face is pin.external:
                continue
            if id(face) in rail_port_ids:
                return True
            if face.direction is Direction.OUT:
                return True
        return False
    return pred


def _make_reset_predicate(
    rail_port_ids: "dict[int, Rail]",
    port_owner: dict[int, Part],
) -> _PinPredicate:
    """RESET pin: at steady state the line must be defined.  Accepted:
      - a driver port on the same net (something actively asserts /
        deasserts the line)
      - direct wiring to a POWER Rail (tied to VCC = "never reset")
      - a path through a passive Resistor whose opposite terminal sits
        on a net containing a POWER Rail (pull-up).  This handles the
        canonical RC reset network: the R-to-VCC leg holds the pin
        defined at steady state; the parallel C-to-GND leg sits on a
        different net and is irrelevant to this static check.

    The "wire to ground via a resistor" case (active-high reset chips)
    is symmetric but rare; if it surfaces, add the mirror walk.
    """
    def pred(pin: Pin, chip: Chip) -> bool:
        node = pin.external.node
        if node is None:
            return False
        for face in node.ports:
            if face is pin.external:
                continue
            # Direct driver.
            if face.direction is Direction.OUT:
                return True
            # Direct POWER-rail wiring.
            rail = rail_port_ids.get(id(face))
            if rail is not None and bool(rail.level) is True:
                return True
            # Pull-up: face belongs to a Resistor; walk to its other
            # terminal and check the net there for a POWER Rail.
            from components.passives.resistor import Resistor
            owner = port_owner.get(id(face))
            if not isinstance(owner, Resistor):
                continue
            for other_port in owner.ports.values():
                if other_port is face:
                    continue
                other_node = other_port.node
                if other_node is None:
                    continue
                for other_face in other_node.ports:
                    other_rail = rail_port_ids.get(id(other_face))
                    if other_rail is not None and bool(other_rail.level) is True:
                        return True
        return False
    return pred


def _make_clock_in_predicate() -> _PinPredicate:
    """CLOCK_IN: net must contain a driver, OR the chip declares
    `INTERNAL_CLOCK_OK = True` (parallel to BARE_FIRMWARE_DRIVEN: an
    explicit opt-out for chips whose internal oscillator runs without
    an external clock).
    """
    def pred(pin: Pin, chip: Chip) -> bool:
        if getattr(type(chip), 'INTERNAL_CLOCK_OK', False):
            return True
        node = pin.external.node
        if node is None:
            return False
        for face in node.ports:
            if face is pin.external:
                continue
            if face.direction is Direction.OUT:
                return True
        return False
    return pred


def _nc_predicate(pin: Pin, chip: Chip) -> bool:
    """NC: strictly unwired.  An NC pin with anything on its net fails
    — datasheets that document "tie NC to GND for layout convenience"
    should declare the pin as a signal (`PIN_FUNCTIONS = {'NCx': None}`)
    rather than NC, because the framework can't tell which kind of NC
    each datasheet means.  Strict default; lenient interpretation is
    a future refinement only if a real demo trips this.
    """
    return pin.external.node is None


def _enforce_pin_function_rules(
    parts: list[Part], all_parts: list[Part] | None,
) -> None:
    """Run every PinFunction's ERC rule on the design.  Each rule
    raises `BreadboardIncompatibleError` on the first role that fails;
    the user fixes one role at a time."""
    universe = list(all_parts or parts)
    rail_port_ids = _build_rail_port_index(universe)
    port_owner    = _build_port_owner_index(universe)

    _check_chip_pin_function(
        parts,
        function=PinFunction.POWER,
        predicate=_make_rail_predicate(rail_port_ids, want_high=True),
        error_msg_prefix=(
            "Chips have unwired supply pins — the assembled circuit "
            "won't power up. Wire each pin below to its rail in the "
            "design source:"
        ),
        failure_hint="wire to the + rail",
    )
    _check_chip_pin_function(
        parts,
        function=PinFunction.GROUND,
        predicate=_make_rail_predicate(rail_port_ids, want_high=False),
        error_msg_prefix=(
            "Chips have unwired supply pins — the assembled circuit "
            "won't power up. Wire each pin below to its rail in the "
            "design source:"
        ),
        failure_hint="wire to the − rail",
    )
    _check_chip_pin_function(
        parts,
        function=PinFunction.REFERENCE,
        predicate=_make_reference_predicate(rail_port_ids),
        error_msg_prefix=(
            "Chips have undriven reference pins — the ADC / comparator "
            "will read garbage without a stable source. Wire each pin "
            "below to a Rail, a regulator output, or a divider tap in "
            "the design source:"
        ),
        failure_hint="wire to a stable reference source",
    )
    _check_chip_pin_function(
        parts,
        function=PinFunction.RESET,
        predicate=_make_reset_predicate(rail_port_ids, port_owner),
        error_msg_prefix=(
            "Chips have floating reset pins — the line is undefined at "
            "steady state and the chip will behave unpredictably. Wire "
            "each pin below either to a driver or through a pull-up "
            "resistor to the + rail in the design source:"
        ),
        failure_hint="wire to a driver or pull-up to + rail",
    )
    _check_chip_pin_function(
        parts,
        function=PinFunction.CLOCK_IN,
        predicate=_make_clock_in_predicate(),
        error_msg_prefix=(
            "Chips have unwired clock-input pins — the chip won't "
            "oscillate without an external clock. Wire each pin below "
            "to an oscillator / clock-output source in the design "
            "source, or set INTERNAL_CLOCK_OK = True on the chip class "
            "if its internal RC oscillator is acceptable for this use:"
        ),
        failure_hint="wire to an external clock source",
    )
    _check_chip_pin_function(
        parts,
        function=PinFunction.NC,
        predicate=_nc_predicate,
        error_msg_prefix=(
            "Chips have no-connect pins wired to something — the "
            "datasheet says these must remain unconnected. Remove the "
            "wiring in the design source, or — if the datasheet actually "
            "permits tying the pin to GND for layout convenience — "
            "declare it as a signal pin via "
            "`PIN_FUNCTIONS = {'NC1': None}` on the chip class:"
        ),
        failure_hint="this pin must not be connected",
    )


# ------------------------------------------------------------- refusal


def _check_breadboard_compatible(
    parts: list[Part], design: Part,
    *, all_parts: list[Part] | None = None,
) -> None:
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

    # Pin-function ERC: each PinFunction member has its own rule for
    # what "correctly wired" looks like on the bench.  POWER and GROUND
    # need a matching-level Rail on the net; REFERENCE needs a stable
    # analog source; RESET needs a driver or pull-up to a power rail;
    # CLOCK_IN needs a driver (unless the chip can use its internal
    # oscillator); NC must not be wired at all.  Each rule is a
    # separate _check_chip_pin_function call so the failure messages
    # stay role-specific.
    #
    # Runs after the SMD / Board refusals so the more fundamental
    # "this can't go on a breadboard at all" message takes precedence.
    _enforce_pin_function_rules(parts, all_parts)


# ------------------------------------------------------------ ingredients


def _value_for_bom(part: Part) -> str:
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


def _bom_note(part: Part) -> str:
    """One-line note for the BOM row.  Common hints — polarity, lead
    notes, package style — to ease procurement at the bench."""
    from components.passives.led import LED
    from components.passives.resistor import Resistor
    if isinstance(part, LED):
        return "Longer lead is the anode (+)"
    if isinstance(part, Resistor):
        return "¼ W carbon film is fine"
    return ""


def _ingredients_section(parts: list[Part]) -> str:
    """Build the Parts section: a Markdown table + free-form
    prose listing non-electronic items."""
    lines: list[str] = [
        "## Parts", "",
        "| Refdes | Part | Value / Spec | Quantity | Notes |",
        "|--------|------|--------------|----------|-------|",
    ]
    # One row per part, sorted by refdes (alphabetical prefix, then
    # numeric suffix — same convention as the BOM exporter).
    def sort_key(p: Part) -> tuple[str, int]:
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


# ----------------------------------------------------------------- layout


def _layout_section(parts: list[Part]) -> str:
    """Build the Layout section: one ASCII pinout per placeable part.

    Sorted by refdes (alphabetical prefix, numeric suffix) so the
    output is deterministic for the goldens.  Rails contribute no
    diagram and are filtered out."""
    lines: list[str] = [
        "## Layout", "",
        "Each part below is drawn the way it sits on the breadboard, "
        "with every pin labelled. Chips run left-to-right with the "
        "notch at the left; pin 1 is the top-left pin (closest to the "
        "notch). Sensors and modules are shown as a single horizontal "
        "row of pins. 2-lead passives are drawn axially with the value "
        "in line.",
        "",
    ]

    def sort_key(p: Part) -> tuple[str, int]:
        rd = p.refdes
        prefix = rd.rstrip('0123456789')
        n = rd[len(prefix):]
        return (prefix, int(n) if n else 0)

    placeable = [p for p in parts if not _is_rail(p)]
    for part in sorted(placeable, key=sort_key):
        diagram = part_layout(part, _value_for_bom(part))
        if not diagram:
            continue
        cls = type(part).__name__
        lines.append(f"### {part.refdes} — {cls}")
        lines.append("")
        lines.append("```")
        lines.append(diagram)
        lines.append("```")
        lines.append("")
    return '\n'.join(lines).rstrip() + '\n'


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
    if is_arduino_uno(chip):
        return (
            f"Place {chip.refdes} (Arduino Uno R3) beside the breadboard. "
            f"The board doesn't sit on the breadboard itself — its female "
            f"headers receive the jumpers listed below. Power the Uno via "
            f"its USB jack or a 7–12 V supply on the `Vin` header."
        )
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
    # SIPs (odd pin counts) sit entirely on one side of the trough
    # — they can't straddle, so the wording differs.
    if package_pin_count % 2 != 0:
        return (
            f"Plug {chip.refdes} ({type(chip).__name__}, "
            f"{package_pin_count}-pin SIP) into the breadboard with all "
            f"pins on the upper half: pin 1 at {pin1.label()}, "
            f"pin {last_n} at {last.label()}. "
            f"The lower-numbered position marks the pin-1 end."
        )
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
    (_, p1), (_, p2) = placement.pins[0], placement.pins[1]
    return (
        f"Plug {part.refdes} ({cls}): one lead at "
        f"{p1.tie_strip_label}, the other at {p2.tie_strip_label}."
    )


def _jumper_steps(
    all_parts: list[Part],
    placeable_parts: list[Part],
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
    # For each placeable port: the "U1 out_1" endpoint label (what to
    # connect, logically) and the tie-strip label (where to find it on
    # the board).  The logical endpoint leads in the emitted step;
    # coordinates trail as the bench-side reference.
    port_to_endpoint: dict[int, str] = {}
    port_to_label: dict[int, str] = {}
    for placement in placements.values():
        comp = placement.component
        for name, pin_place in placement.pins:
            try:
                port = comp.ports[name]
            except (KeyError, TypeError):
                continue
            # Reference each pin by what the builder actually sees on
            # the package.  Chips show only pin numbers on their
            # plastic — `out_1` / `SEG_C` etc. are framework
            # abstractions, useful for design code but invisible at
            # the bench.  2-lead passives (Resistor / LED / etc.) have
            # already-physical port names (t1, anode), so keep those.
            if isinstance(comp, Chip):
                num = _pin_number_for_name(comp, name)
                ep = f"{comp.refdes} pin {num}" if num else f"{comp.refdes} {name}"
            else:
                ep = f"{comp.refdes} {name}"
            port_to_endpoint[id(port)] = ep
            port_to_label[id(port)] = pin_place.tie_strip_label

    # Build port → owner Part lookup so we can spot rail-owned
    # ports without relying on Port._owner (which is only set for Pin
    # faces).
    port_owner: dict[int, Part] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        for port in part.ports.values():
            port_owner[id(port)] = part

    # Ports on off-board Uno boards: build a separate endpoint label
    # using the Arduino header silkscreen name (e.g. "U1 D3") instead
    # of the chip-level pin name ("U1 PD3").  These ports have no
    # breadboard coordinate; jumper steps will reference them by
    # header only.
    port_to_uno_endpoint: dict[int, str] = {}
    for part in all_parts:
        if isinstance(part, Pin):
            continue
        if not is_arduino_uno(part):
            continue
        for port in part.ports.values():
            port_to_uno_endpoint[id(port)] = (
                f"{part.refdes} {uno_header_label(port.name)} "
                f"(Arduino Uno header)"
            )

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

    # Sort nets so the bench builder works through each on-board chip
    # in ascending pin-number order — the natural sequence when
    # counting from the notch.  Each net's key is the lowest
    # (refdes, pin-number) of any on-board chip pin in the net.  Uno
    # endpoints are excluded from the key because they have no
    # breadboard position; nets with no chip pins fall through to a
    # passive-port key so they still sort deterministically.
    def _net_key(nid: int) -> tuple[int, tuple[str, int] | tuple[str, str]]:
        ps = node_to_ports[nid]
        chip_keys: list[tuple[str, int]] = []
        other_keys: list[tuple[str, str]] = []
        for p in ps:
            owner = port_owner.get(id(p))
            if owner is None or isinstance(owner, (Pin, Rail)):
                continue
            if isinstance(owner, Chip):
                if is_arduino_uno(owner):
                    continue
                num = _pin_number_for_name(owner, p.name)
                if num is not None:
                    chip_keys.append((owner.refdes, num))
            else:
                other_keys.append(
                    (getattr(owner, 'refdes', '') or '', p.name)
                )
        if chip_keys:
            return (0, min(chip_keys))
        if other_keys:
            return (1, min(other_keys))
        return (2, ('', ''))

    def _emit_subnet(sub_ports: list[Port]) -> None:
        """Emit jumper steps for one logical sub-net.  A sub-net is
        either a true net (no internal passive bridge) or one half of
        a net that's been split at a 2-lead passive's terminals."""
        rail_polarity: bool | None = None
        for p in sub_ports:
            owner = port_owner.get(id(p))
            if isinstance(owner, Rail):
                rail_polarity = bool(owner.level)
                break
        # For 2-lead passives where BOTH terminals appear in this
        # sub-net, the body of the passive already bridges t1 ↔ t2 —
        # emitting a jumper between them would be redundant (and
        # readers spot it immediately as a bench error).  Collapse
        # both terminals to one "canonical" port (the
        # alphabetically-first name, typically t1 / anode) so the
        # downstream rail / chain logic sees just one endpoint per
        # bridging passive.
        seen_ids = {id(p) for p in sub_ports}
        keep: set[int] = set()
        for p in sub_ports:
            owner = port_owner.get(id(p))
            if owner is None or isinstance(owner, (Pin, Chip, Rail)):
                keep.add(id(p))
                continue
            terms = list(owner.ports.values())
            if len(terms) != 2 or not all(id(t) in seen_ids for t in terms):
                keep.add(id(p))
                continue
            canonical = min(terms, key=lambda t: t.name)
            if id(p) == id(canonical):
                keep.add(id(p))
        bb_endpoints: list[tuple[str, str]] = sorted({
            (port_to_endpoint[id(p)], port_to_label[id(p)])
            for p in sub_ports
            if id(p) in port_to_endpoint and id(p) in keep
        })
        uno_endpoints: list[str] = sorted({
            port_to_uno_endpoint[id(p)]
            for p in sub_ports if id(p) in port_to_uno_endpoint
        })
        if rail_polarity is not None and (bb_endpoints or uno_endpoints):
            rail_name = "top `+` rail" if rail_polarity else "top `-` rail"
            for ep, pos in bb_endpoints:
                steps.append(
                    f"Run a jumper from {ep} at {pos} to the {rail_name}."
                )
            for ep in uno_endpoints:
                steps.append(f"Run a jumper from {ep} to the {rail_name}.")
        else:
            # Signal sub-net — chain endpoints together.  Uno↔breadboard
            # pairs emit no breadboard coord on the Uno side; pure-bb
            # chains emit coords on both sides; pure-Uno chains emit
            # neither.
            for uno_ep in uno_endpoints:
                for bb_ep, bb_pos in bb_endpoints:
                    steps.append(
                        f"Run a jumper from {bb_ep} at {bb_pos} to {uno_ep}."
                    )
            if not uno_endpoints and len(bb_endpoints) >= 2:
                for i in range(len(bb_endpoints) - 1):
                    ep1, pos1 = bb_endpoints[i]
                    ep2, pos2 = bb_endpoints[i + 1]
                    steps.append(
                        f"Run a jumper from {ep1} to {ep2} "
                        f"— {pos1} to {pos2}."
                    )
            elif not bb_endpoints and len(uno_endpoints) >= 2:
                for i in range(len(uno_endpoints) - 1):
                    steps.append(
                        f"Run a jumper from {uno_endpoints[i]} "
                        f"to {uno_endpoints[i + 1]}."
                    )

    def _bridging_passive(net_ports: list[Port]) -> Part | None:
        """Return the 2-lead passive whose BOTH terminals appear in
        `net_ports`, or None.

        Demos sometimes wire a passive's two terminals into the same
        logical net (e.g. `wire(arduino.PD3, r1.t1, r1.t2, display.DIG_1)`
        so the simulator's voltage-only solver can propagate through
        the resistor as a 0-Ω passthrough).  At the bench the resistor's
        body provides the connection between its leads — no jumper goes
        across t1↔t2 — so the assembly guide must split such a net
        into two sub-nets, one per terminal.

        Restricted to nets with exactly one such fully-internal
        passive; nets with two parallel passives fall through to the
        default chain logic."""
        seen_ids = {id(p) for p in net_ports}
        candidates: list[Part] = []
        for p in net_ports:
            owner = port_owner.get(id(p))
            if owner is None or owner in candidates:
                continue
            if isinstance(owner, (Pin, Chip, Rail)):
                continue
            terminal_ports = list(owner.ports.values())
            if len(terminal_ports) != 2:
                continue
            if all(id(t) in seen_ids for t in terminal_ports):
                candidates.append(owner)
        return candidates[0] if len(candidates) == 1 else None

    for nid in sorted(node_to_ports.keys(), key=_net_key):
        ports = node_to_ports[nid]
        bridge = _bridging_passive(ports)
        if bridge is None:
            _emit_subnet(ports)
            continue
        # Split the net at the passive's two terminals.  Non-passive
        # ports are sorted deterministically and distributed half-half
        # across the two terminals — without semantic direction info
        # (the wire() call merges everything onto one node), an even
        # split is the most defensible choice and lets the body of
        # the passive carry the current in series between the two
        # sides.
        terminals = list(bridge.ports.values())
        t1, t2 = terminals[0], terminals[1]
        non_passive = [p for p in ports if port_owner.get(id(p)) is not bridge]
        non_passive.sort(key=lambda p: (
            getattr(port_owner.get(id(p)), 'refdes', '') or '',
            p.name,
        ))
        half = (len(non_passive) + 1) // 2
        _emit_subnet(non_passive[:half] + [t1])
        _emit_subnet(non_passive[half:] + [t2])
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
    all_parts: list[Part],
    placeable_parts: list[Part],
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


def _verify_section(parts: list[Part]) -> str:
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


def _notes_section(parts: list[Part]) -> str:
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


def _design_blurb(design: Part) -> str:
    """Optional one-line description pulled from the design's class
    docstring (the first non-blank line)."""
    doc = (type(design).__doc__ or '').strip()
    if not doc:
        return ""
    return doc.splitlines()[0].strip()


def build_recipe(design: Part) -> str:
    """Assemble the full assembly-guide Markdown for `design`.

    Raises `BreadboardIncompatibleError` per spec §5.5 if any part is
    SMD-only or the top-level design is a multi-board assembly."""
    parts = _walk_top_parts(design)
    # Filter out Rails — they're nets, not physical parts.
    placeable = [p for p in parts if not _is_rail(p)]
    _check_breadboard_compatible(placeable, design, all_parts=parts)

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
    sections.append(_layout_section(placeable))
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
