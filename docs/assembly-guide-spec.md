# Assembly Guide Exporter + Substrate-Compatibility Properties — Implementation Spec

## 1. Purpose

Two coordinated additions:

1. **A text-based bench-assembly-guide exporter** that emits a Markdown document structured like a cooking recipe: *Ingredients* (the parts list), *Method* (numbered build steps that map directly to breadboard holes and jumper paths), and *Notes & Gotchas* (per-component bench warnings derived from the parts actually used). The user reads it one step at a time at the bench and ends up with a working circuit.

2. **A uniform substrate-compatibility surface** on every component — `is_breadboard_compatible`, `is_pcb_compatible`, `is_perfboard_compatible`, `is_dead_bug_compatible`, plus the underlying `is_through_hole` / `is_smd` flags. Composable with logical `and` / `or`, computed from each part's existing `FOOTPRINT` metadata where possible, overridable per-class where physical reality is more nuanced than the footprint string alone implies.

The two pieces meet at one point: the assembly-guide exporter refuses to render a design containing any part whose `is_breadboard_compatible` is `False`, with a clear error naming the offending parts.

## 2. Scope

**In scope** — the compatibility properties on every component class; per-package physical-layout metadata sufficient for breadboard placement; the assembly-guide adapter under `framework/export/assembly_guide/` registering with the existing renderer registry; a `GOTCHAS` class attribute on every component class with bench-relevant warnings; the placement algorithm (deterministic, simple — anchor the largest DIP chip on the trough, pack the rest, route jumpers as text instructions); the output Markdown format with the three-section recipe shape.

**Out of scope** — SVG visual rendering of the breadboard (the assembly guide is text-only; a future visualizer would consume the same placement data); auto-routing optimisation (the placement is "good enough to follow at the bench," not "minimum jumper length"); relationship-based gotchas (e.g. "LED wired without a series resistor" — start with presence-based, evolve later); compatibility properties for non-breadboard substrates beyond the four listed (no Eurorack, no Veroboard, etc. — add when there's real demand); a real-time visualizer that updates as the user builds.

**Prerequisites** — all previous specs implemented. This spec assumes the export framework's renderer registry, MRO dispatch, `compute_logical_nets`, the component registry with `@register`, and the `FOOTPRINT` metadata on every refdes-bearing component.

## 3. Constraints carried over from CLAUDE.md

- Physical fidelity primary. Compatibility properties describe physical facts about the part (through-hole leads on 0.1" pitch fit a breadboard; SMD pads don't). The placement algorithm describes where the part *would actually plug in* on a real 830-pin breadboard. The assembly steps describe what the bench user *would actually do*.
- `__slots__` discipline preserved on every new class.
- No setters; compatibility properties are read-only `@property` accessors.
- Pydantic `@validate_call` on every public framework function and method, per the existing discipline.
- Registry-mediated dispatch; the assembly-guide adapter follows the same shape as `spice/`, `kicad/`, `bom/`, etc.
- New class attributes (`GOTCHAS`, package layout) follow the same conventions as the existing `FOOTPRINT`, `PIN_NUMBERS`, `MATES_WITH` etc. — `ClassVar` for fixed data, `@property` if computed from instance state.

## 4. Substrate-compatibility properties

### 4.1 Two underlying flags

Every component class exposes two read-only properties describing its mounting technology:

- `is_through_hole: bool` — the part has leads designed to pass through holes (DIP, axial-lead resistors, TO-220 transistors, 0.1" pin headers, radial-lead capacitors, etc.).
- `is_smd: bool` — the part is surface-mount (SMD resistors, SOIC chips, QFN/QFP packages, USB-C receptacles, etc.).

Default implementations compute these from the part's `FOOTPRINT` string. Add a private helper to `framework/factor.py`:

```python
class FactorNode:
    # … existing class body …

    @property
    def is_through_hole(self) -> bool:
        """The part is through-hole (leads pass through holes)."""
        return _footprint_is_through_hole(self.FOOTPRINT)

    @property
    def is_smd(self) -> bool:
        """The part is surface-mount (pads on the PCB surface)."""
        return _footprint_is_smd(self.FOOTPRINT)
```

Where the private helpers in `framework/factor.py`:

```python
_THT_FOOTPRINT_MARKERS = (
    'Package_DIP:',
    'Package_TO_SOT_THT:',
    'Connector_PinHeader_2.54mm:',
    'Connector_PinHeader_1.27mm:',
    'TerminalBlock_Phoenix',
    'Capacitor_THT:',
    'Resistor_THT:',
    'LED_THT:',
    'Diode_THT:',
    'Connector_BarrelJack:BarrelJack_Horizontal',
)

_SMD_FOOTPRINT_MARKERS = (
    'Package_SO:', 'Package_SOIC:', 'Package_QFN:', 'Package_QFP:',
    'Package_BGA:', 'Package_LGA:', 'Package_TO_SOT_SMD:',
    'Resistor_SMD:', 'Capacitor_SMD:', 'LED_SMD:', 'Diode_SMD:',
    'Connector_USB:', 'Connector_Audio:',  # most USB / audio are SMD
)


def _footprint_is_through_hole(footprint: str | None) -> bool:
    if footprint is None:
        return False
    return any(footprint.startswith(m) for m in _THT_FOOTPRINT_MARKERS)


def _footprint_is_smd(footprint: str | None) -> bool:
    if footprint is None:
        return False
    return any(footprint.startswith(m) for m in _SMD_FOOTPRINT_MARKERS)
```

**For parts where neither default returns the right answer**, the component class overrides:

```python
class Rail(FactorNode):
    # Rail is a net abstraction, not a part. Vacuously compatible with
    # any substrate (it isn't soldered to anything).
    is_through_hole = True   # @property elided for ClassVar simplicity
    is_smd = False
```

But really for `Rail`, `GroundDomain`, etc. — they have `FOOTPRINT = None`, and both default properties return `False`. That's fine for the *part-level* compatibility check (Rail isn't a physical part), but the substrate-level compatibility (next section) treats `FOOTPRINT is None` as "vacuously compatible with everything."

### 4.2 Four substrate properties

Derived properties on `FactorNode`:

```python
@property
def is_breadboard_compatible(self) -> bool:
    """True if this part can plug directly into a standard 830-pin
    breadboard. Through-hole parts with 0.1" lead spacing qualify;
    SMD parts and exotic-pitch parts do not. Parts with no FOOTPRINT
    (Rail, Ground) are vacuously compatible — they're not physical
    parts, so they don't block breadboard assembly."""
    if self.FOOTPRINT is None:
        return True
    return self.is_through_hole

@property
def is_perfboard_compatible(self) -> bool:
    """True if this part can be soldered onto standard 0.1" perfboard.
    Currently equivalent to is_breadboard_compatible — same hole
    geometry. (Future: SMD-on-perfboard via adapter footprints could
    extend this; not modelled today.)"""
    return self.is_breadboard_compatible

@property
def is_pcb_compatible(self) -> bool:
    """True if this part can land on a custom PCB. Both through-hole
    and SMD parts qualify; the only exclusion is parts that aren't
    placeable (Rail, Ground, anything with FOOTPRINT=None — those are
    vacuously True since a PCB doesn't need to do anything to
    accommodate them)."""
    if self.FOOTPRINT is None:
        return True
    return self.is_through_hole or self.is_smd

@property
def is_dead_bug_compatible(self) -> bool:
    """True if this part can be wired point-to-point in dead-bug
    fashion (leads soldered directly to other leads or to floating
    pads, no PCB required). Through-hole parts with accessible leads
    qualify; most SMD parts don't without rework adapters.

    Equivalent to is_through_hole for the current library."""
    if self.FOOTPRINT is None:
        return True
    return self.is_through_hole
```

**Composability is automatic.** Python `and` / `or` work directly:

```python
# "Can I build this design on a breadboard AND order a PCB later?"
parts_ok = all(p.is_breadboard_compatible and p.is_pcb_compatible
               for p in design.factor_nodes)

# "Which parts can I solder onto perfboard?"
perfboard_parts = [p for p in design.factor_nodes
                   if p.is_perfboard_compatible]
```

### 4.3 Per-class overrides

When the footprint-based default is wrong, a class overrides:

```python
class MicroSDCardSlot(Connector):
    # … existing class body …

    # Most microSD slots are SMD; some hobby breakouts have THT leads.
    # The default footprint (Connector_Card:microSD_HC_Hirose_DM3D-SF)
    # is SMD. Override to False explicitly to make the intent visible.
    is_breadboard_compatible = False   # via @property
```

Per CLAUDE.md, overrides use `@property` rather than class attributes when the value is computed; but constant `True` / `False` overrides can be class attributes — they're physical facts about the part, not runtime behaviour.

The implementer should sweep the existing 122 components and decide per-class: does the FOOTPRINT-based default give the right answer? If not, override. Spot-checks the spec recommends:

- `MicroSDCardSlot`, `SDCardSlot` — default returns False (SMD), correct.
- `USBCReceptacle`, `USBAReceptacle`, etc. — default returns False, correct (SMD).
- `BarrelJack5p5x2p1`, `BarrelJack5p5x2p5` — these *are* through-hole on most hobby parts. If FOOTPRINT triggers the THT marker, default is True; verify and override only if wrong.
- `ATmega328P` — DIP-28 by default in the catalogue → THT True, correct.
- `ATmega2560`, `STM32F103C8T6`, `STM32F411CEU6`, `RP2040`, `ESP32_WROOM_32`, `ESP8266_12F` — all TQFP / QFN / module → SMD, breadboard-incompatible. These should return False; the FOOTPRINT-based default already handles them correctly.
- `Header2xNMale`, `Header2xNFemale`, `Header1xNMale`, `Header1xNFemale` — 0.1" headers → THT True, correct.
- All discrete transistors and diodes (TO-92, TO-220, DO-35) — THT True, correct.

The spec doesn't enumerate every class; the implementer's sweep generates a per-component summary in `docs/substrate-compatibility-audit.md` listing the four boolean values for each class and flagging any disagreements between the default and reality.

### 4.4 Why these names and not others

The user asked for `isBreadBoardCompatible` (camelCase). The codebase uses snake_case throughout (`refdes_number`, `pin_count`, `pitch_mm`, etc.); these properties follow the existing convention. The pattern users compose with `and` / `or` reads the same either way:

```python
part.is_breadboard_compatible and part.is_pcb_compatible
```

This matches every other boolean property in the codebase (`led.lit`, `pin.connected`, `port.mandatory`, etc.).

## 5. The assembly-guide exporter

### 5.1 Output shape

The exporter produces a single Markdown document with a recipe-style structure:

```markdown
# Build Guide: HelloLED

A small build to verify your breadboard, your parts, and your soldering iron all
agree on what "this LED should light up" means.

## Ingredients

| Refdes | Part        | Value / Spec   | Quantity | Notes                          |
|--------|-------------|----------------|----------|--------------------------------|
| R1     | Resistor    | 330 Ω          | 1        | ¼ W carbon film is fine        |
| D1     | LED         | Red, 5 mm      | 1        | Longer lead is the anode (+)   |

Also: a standard 830-pin breadboard, one red jumper wire, one black jumper wire,
and a 5 V supply (USB breakout, bench supply, or four AA cells in series).

## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: red lead to the
   top `+` rail, black lead to the top `-` rail.
2. Plug R1 with one lead in **position 5** (any of holes 5A through 5E) and
   the other lead in **position 10** (any of 10A through 10E). R1 now bridges
   two tie strips — separate electrical nets. The resistor isn't polarised;
   either way around works.
3. Plug D1's longer lead (the anode) into **position 10** (any of 10A–10E)
   so it joins R1's other lead — same tie strip, same net.
4. Plug D1's shorter lead (the cathode) into **position 12** (any of 12A–12E).
5. Run a jumper from the top `+` rail down to **position 5** (any of 5A–5E).
   This puts +5 V on R1's first lead.
6. Run a jumper from **position 12** (any of 12A–12E) to the top `-` rail.
   This pulls D1's cathode to ground.
7. Power on. D1 should light steadily. If it doesn't, see the gotchas.

Notice the pattern: every component spans **two different position numbers**,
because the five A–E holes within one position are already a single electrical
node (a "tie strip"). Plugging both leads of a part into the same position
would short the part across one tie strip and do nothing. The placement
algorithm in §5.2 enforces this — every component lead lands at a distinct
position.

## Notes & Gotchas

- **LED polarity matters.** The longer lead of a fresh LED is the anode (+);
  the shorter lead is the cathode (−). If yours has been trimmed, look for the
  flat side of the body — that's the cathode side. Reverse the LED and nothing
  happens; the framework's topology check can't catch this because both leads
  are valid wires.
- **The current-limit resistor is mandatory.** Without R1, the LED draws too
  much current at any sensible supply voltage and dies in a flash of light.
  R1 = 330 Ω is sized for ~10 mA at 5 V supply with a 2 V LED drop; smaller
  values run brighter (and shorter); larger values dim. 220 Ω–1 kΩ is fine.
- **Power-rail continuity.** Some 830-pin breadboards split the top `+` rail
  into two segments at the middle of the board, with a small gap. If your LED
  doesn't light and everything else looks right, jumper across the gap.
```

### 5.2 The placement algorithm

Deterministic and simple. The output isn't optimal; it's *legible* and the same for any given design.

```
1. Establish a coordinate system on the breadboard.  See Appendix A for the
   topology in full; the short version:
   - **Positions 1–63** along the long axis (sometimes labelled as column
     numbers on the board itself).
   - **Rows A–E** above the trough; **rows F–J** below the trough.
   - Holes A through E within a single position are one electrical node
     (a "tie strip"). Holes F through J within a single position are a
     separate tie strip. The trough between row E and row F separates them.
   - Different positions are not connected to each other.
   - **Power rails** (top `+`, top `-`, bottom `+`, bottom `-`) are long
     strips running parallel to the long axis, each one a single node along
     its full length (or a pair of half-length nodes on some boards — see
     Appendix A).

2. Identify the largest chip (most pins) among the design's components.
   If no chips, skip to step 5.

3. Place the largest chip straddling the trough:
   - Pin 1 at (position 10, row E).
   - For a DIP-N chip, pins 1..N/2 occupy positions 10..10+N/2-1, all in
     row E (above the trough).  Pins N/2+1..N return in row F (below the
     trough), with pin N/2+1 at position 10+N/2-1 and pin N at position 10.
   - So a DIP-14 occupies positions 10–16 inclusive: pins 1–7 on row E,
     pins 8–14 on row F, with pin 1 and pin 14 in the same position (10)
     on opposite sides of the trough.
   - Each pin lands in its own tie strip — pin 1's tie strip is
     {10A, 10B, 10C, 10D, 10E}; pin 14's tie strip is {10F, 10G, 10H, 10I,
     10J}.  These are separate nets joined only through the chip.

4. Place subsequent chips to the right of the previous one with a 2-position
   gap.  Same straddling pattern.

5. For each 2-terminal through-hole part (Resistor, LED, Capacitor, Diode,
   Transistor lead pair):
   - The part must span **two different positions** so its leads land in
     distinct tie strips.
   - If one terminal is wired to a chip pin, place that terminal in any
     A–D hole of the chip pin's position (same tie strip as the pin).
     Place the other terminal in any A–E hole of a different position.
   - If a terminal is wired to a Rail, place that terminal in a position
     with direct jumper access to the appropriate power rail (any
     position works; the jumper bridges the gap).
   - Two terminals wired together (same logical net) land in tie strips
     of the same position — e.g., R1's second lead and D1's anode both at
     position 10, rows A–E, joining at that tie strip.

6. For each wire in the circuit's logical-net set:
   - Identify the (position, row) of every endpoint.
   - Emit a jumper instruction:
     "Run a jumper from position X (any of XA–XE) to position Y (any of
     YA–YE)" — for tie-strip-to-tie-strip jumpers.
     "Run a jumper from position X (any of XA–XE) to the top `+` rail" —
     for power-rail jumpers.
   - The specific row letter doesn't matter as long as it's on the
     correct side of the trough: a jumper "from 5A" and "from 5D" are
     identical electrically.

7. Output the assembly steps in this order:
   - Step 1: orient the breadboard, connect the supply rails.
   - Steps 2..N: place each chip in placement order (largest first).
   - Steps N+1..M: place each 2-terminal component in the order it
     appears in the circuit's factor_nodes list.
   - Steps M+1..K: run each jumper wire.
   - Final step: "verify and power on."
```

The implementer is welcome to refine the algorithm but must keep it **deterministic** — golden tests will assert byte-identical Markdown output for each existing demo before and after any changes.

### 5.3 Per-component physical-layout metadata

For the placement algorithm to know "where is pin 1 of a TO-92 transistor relative to pins 2 and 3" or "how far apart are the two leads of a 1N4148," each through-hole component class declares a `LAYOUT` class attribute:

```python
class Resistor(FactorNode):
    # … existing body …

    # Bent-leaded through-hole resistor with 7.62 mm (0.3", 3 holes)
    # lead spacing. Standard ¼-W carbon film.
    LAYOUT: ClassVar[dict] = {
        'kind': 'axial_2lead',
        'lead_spacing_holes': 3,
    }

class LED(FactorNode):
    LAYOUT: ClassVar[dict] = {
        'kind': 'radial_2lead_polarised',
        'lead_spacing_holes': 1,    # standard 5 mm LED, 2.54 mm leads
        'positive_lead': 'anode',   # longer lead
    }

class SN74HC04(Chip):
    LAYOUT: ClassVar[dict] = {
        'kind': 'dip',
        'pin_count': 14,
    }

class Q2N3904(FactorNode):
    LAYOUT: ClassVar[dict] = {
        'kind': 'to92',
        'pin_order': ('emitter', 'base', 'collector'),
        'lead_spacing_holes': 1,
    }
```

Three layout kinds cover most of the breadboard-compatible library:

- `dip` — chip straddling the trough; only `pin_count` is needed.
- `axial_2lead` — two leads at fixed hole spacing; either end works (non-polarised).
- `radial_2lead_polarised` — two leads at fixed spacing; one is positive.
- `to92` — three leads in a row, with named pin ordering.
- `to220` — three leads with optional heatsink tab; like TO-92 with wider spacing.
- `header_pins` — 0.1" header strip, N pins in a row.

Classes whose `is_breadboard_compatible` is `False` don't need a `LAYOUT` — the assembly guide refuses to render their designs anyway.

For DIP packages the implementer doesn't need per-class pin coordinates: the package convention plus `pin_count` is enough. For irregular packages (TO-92, TO-220), the lead order is what varies and must be declared.

### 5.4 Per-component gotchas

Each component class declares a `GOTCHAS` class attribute — a tuple of Markdown-formatted strings, each one a bench-relevant warning the assembly guide should surface when this part appears in a design:

```python
class LED(FactorNode):
    # … existing body …

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**LED polarity matters.** The longer lead is the anode (+); "
        "the shorter lead is the cathode (−). Look for the flat side of "
        "the body if the leads have been trimmed.",
        "**Always use a current-limit resistor** in series with an LED. "
        "Without it, the LED draws too much current at any sensible "
        "supply voltage and burns out.",
    )

class ElectrolyticCapacitor(FactorNode):
    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Electrolytic capacitors are polarised.** The longer lead "
        "(or the side without the stripe) is the positive terminal. "
        "Reverse them and they fail violently — sometimes by venting "
        "electrolyte, sometimes by exploding.",
    )

class CD4069(Chip):
    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Tie unused CMOS inputs.** Any input pin not driven by the "
        "circuit must be wired to VCC or GND. Floating CMOS inputs "
        "drift unpredictably and can cause random behaviour.",
    )

class Q2N7000(FactorNode):
    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**MOSFETs are static-sensitive.** Touch the workbench frame "
        "before handling, or use an ESD strap. A discharge through the "
        "gate–source insulator destroys the transistor silently — "
        "it still looks fine, it just doesn't switch.",
    )

class Crystal(FactorNode):  # if/when it exists
    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Keep the crystal close to the MCU.** Long traces between "
        "the crystal and the XTAL pins add stray capacitance and "
        "detune the oscillator. On a breadboard, place the crystal "
        "no more than 2–3 rows from the chip.",
    )
```

The exporter walks the design, collects every unique gotcha string across all components used, deduplicates exact matches, and emits the result in the *Notes & Gotchas* section in stable order (by component class name, then by gotcha index).

Components without bench-relevant gotchas have `GOTCHAS = ()`. The base default on `FactorNode` is the empty tuple, so unspecified classes contribute nothing.

**Universal gotchas** that apply regardless of the design — "double-check supply voltage before powering up," "use the correct resistor wattage" — are emitted unconditionally in a *General* sub-section at the top of *Notes & Gotchas*. These live in a module-level `_GENERAL_GOTCHAS` tuple in the adapter, not on any component class.

### 5.5 Refusal: incompatible parts

If the design contains any part where `is_breadboard_compatible` is `False`, the exporter raises:

```python
class BreadboardIncompatibleError(FormatError, ValueError):
    """The design contains parts that can't be assembled on a standard
    breadboard. Use a different export (e.g. `kicad` for PCB layout)
    or rework the design with breadboard-friendly part variants."""
```

The error message names every incompatible part:

```
BreadboardIncompatibleError: 3 parts can't be assembled on a breadboard:
  - U1 (ATmega2560) — TQFP-100 surface-mount package
  - U3 (BMP280) — LGA-8 surface-mount package
  - J1 (USBCReceptacle) — SMD receptacle

Use `circuitry export <file> --format kicad` to produce a PCB netlist,
or rework the design with breadboard-friendly part variants (e.g. an
ATmega328P DIP-28 instead of an ATmega2560 TQFP-100, a DHT11 module
instead of a bare BMP280).
```

The error is part of the existing `FormatError` family in `framework/errors.py`. Add the class there per the established convention.

## 6. The Markdown output structure

The exporter emits exactly this section structure:

```markdown
# Build Guide: <DesignName>

<optional one-paragraph description from the design's class docstring>

## Ingredients

<table: Refdes | Part | Value/Spec | Quantity | Notes>

<paragraph naming any non-electronic items needed: breadboard, jumper
wires, power supply, etc.>

## Method

<numbered list of assembly steps>

## Notes & Gotchas

<General bullet list, then per-component bullets>

## Testing

<short paragraph: how to verify the design works>
```

The *Testing* section can be omitted for designs where the framework can't sensibly suggest a test (anything where the `__call__` surface isn't a clear driveable interface). The exporter checks for the presence of an `expected_outputs` or similar declarative testing surface and emits the section only if available.

## 7. File-by-file change list

**New files:**

- `src/framework/export/assembly_guide/__init__.py` — entry point: `export_assembly_guide(design, ctx) -> str`.
- `src/framework/export/assembly_guide/recipe.py` — the recipe assembler. Builds the ingredients table, runs the placement algorithm, emits the method steps, collects the gotchas.
- `src/framework/export/assembly_guide/placement.py` — the deterministic placement algorithm. Takes the design's factor_nodes and produces a `dict[FactorNode, BreadboardPosition]` map.
- `src/framework/export/assembly_guide/general_gotchas.py` — the unconditional bench warnings (supply voltage, resistor wattage, ESD basics).
- `tests/framework/export/assembly_guide/` — test directory mirroring the existing format-adapter test structure.
- `tests/golden/assembly_guide/<DesignName>.md` — one per existing demo's top-level design class.
- `docs/substrate-compatibility-audit.md` — generated by the implementer as part of the sweep; one row per component class listing the four substrate booleans.

**Modified files:**

- `src/framework/factor.py` — add `is_through_hole`, `is_smd`, `is_breadboard_compatible`, `is_perfboard_compatible`, `is_pcb_compatible`, `is_dead_bug_compatible` as properties; add the footprint-classification helpers; add `GOTCHAS: ClassVar[tuple[str, ...]] = ()` as default.
- `src/framework/errors.py` — add `BreadboardIncompatibleError(FormatError, ValueError)` with docstring per §5.5.
- `src/components/passives/{resistor,led,rail}.py` — add `LAYOUT` and `GOTCHAS` class attributes.
- `src/components/chips/*.py` — add `LAYOUT` (mostly just `{'kind': 'dip', 'pin_count': N}`); add `GOTCHAS` to CMOS chips and any chip with a notable bench failure mode (74HC family, CD4xxx, opamps with single-supply gotchas, etc.).
- `src/components/transistors/*.py` — add `LAYOUT` (TO-92 / TO-220 / SOT-23 depending on the part); add `GOTCHAS` for MOSFETs (static-sensitive) and Darlington / power BJTs (heat dissipation).
- `src/components/diodes/*.py` — add `LAYOUT` (`{'kind': 'axial_2lead_polarised', 'lead_spacing_holes': 3, 'positive_lead': 'anode'}`); add `GOTCHAS` for Zeners ("reverse-biased; the band marks the cathode") and Schottkys.
- `src/components/connectors/*.py` — `is_breadboard_compatible` overrides for the SMD-only connector classes (most USB / HDMI / audio jacks); `GOTCHAS` for connectors with non-obvious orientation (electrolytic-like polarity hints).
- `README.md` — mention the assembly-guide export in the "What comes out" table; add one row.
- `docs/learning-path.md` — mention that each demo can produce an assembly guide via `export(design, 'assembly_guide', '<Name>.md')`.

**Unmodified:**

- The existing six export adapters (`spice`, `kicad`, `dot`, `mermaid`, `yosys`, `bom`) — none touched.
- The framework's renderer-registry, `compute_logical_nets`, `walk_hierarchy`, `ExporterContext` machinery — none touched.
- Components whose `is_breadboard_compatible` is correctly handled by the FOOTPRINT-based default — only `LAYOUT` and `GOTCHAS` additions if applicable.

## 8. Test plan

**`tests/framework/test_substrate_compatibility.py`:**

1. **Through-hole defaults.** Walk every registered class; for those with a THT FOOTPRINT marker, assert `is_through_hole == True`, `is_smd == False`, `is_breadboard_compatible == True`. For SMD markers, assert the inverse. Parametrise across the catalogue.
2. **No-footprint vacuity.** `Rail`, `GroundDomain`, and anything else with `FOOTPRINT is None` returns `True` for all four substrate-compatibility properties. They don't block any substrate.
3. **Composability.** `Resistor(...).is_breadboard_compatible and Resistor(...).is_pcb_compatible` evaluates correctly to True for a THT resistor. Same with `or`.
4. **Override sticks.** Construct a component class that overrides `is_breadboard_compatible = False` despite a THT FOOTPRINT; assert the override wins.
5. **Per-class audit table.** Read `docs/substrate-compatibility-audit.md`; assert it has one row per registered class and that every row's four boolean values match what the live class properties return. This is the canary that the audit doc stays in sync.

**`tests/framework/export/assembly_guide/test_assembly_guide.py`:**

6. **End-to-end emit.** For each existing demo whose components are all `is_breadboard_compatible=True`, call `export(design, 'assembly_guide', tmp_path)` and assert the file is created, contains all four section headings (`# Build Guide`, `## Ingredients`, `## Method`, `## Notes & Gotchas`), and the BOM table has one row per refdes-bearing component.
7. **Refusal on SMD parts.** For a demo containing any `is_breadboard_compatible=False` component (e.g. `digital_thermometer` uses a DHT11 module which may or may not qualify; `bldc_motor` uses DRV8313 SOIC), assert `BreadboardIncompatibleError` is raised with the offending parts named.
8. **Gotchas appear.** A design containing an LED produces an assembly guide whose "Notes & Gotchas" section contains the LED polarity warning. A design containing a MOSFET produces the static-sensitivity warning. A design containing a CMOS chip produces the "tie unused inputs" warning. Spot-check across categories.
9. **No duplicate gotchas.** A design with three LEDs produces the LED polarity warning *once*, not three times.
10. **Deterministic output.** Build the same design twice; export the assembly guide twice; assert byte-identical Markdown both times.

**`tests/framework/export/assembly_guide/test_placement.py`:**

11. **Largest chip on trough.** For a design with one chip and several passives, the chip's pin 1 lands at row 10 column E by convention. The assembly-step text includes "row 10 column E."
12. **Multiple chips.** For a design with two DIPs, the second chip is placed to the right of the first with a 2-row gap. Verify by parsing the emitted text.
13. **Power-rail jumpers emitted.** Any wire to a `Rail(True)` produces a "to the top + rail" instruction; any wire to a `Rail(False)` produces a "to the - rail" instruction.

**`tests/golden/assembly_guide/`:**

14. **Golden files.** For each existing breadboard-compatible demo (`water_alarm`, `dice`, `digital_thermometer` if its DHT11 is breadboard-friendly, `doorbell_protector` if all parts qualify), commit a golden `.md` file. Assert byte-equality on each export. The `UPDATE_GOLDEN=1` escape hatch from previous golden tests applies.

**Cross-format regression checks:**

15. **Existing exports unchanged.** `WaterAlarm`, `WaterAlarmAssembly`, and every other demo continue to produce byte-identical `.bom.csv`, `.net`, `.cir`, `.mmd`, `.dot`, `.yosys.json` exports — the new metadata (`LAYOUT`, `GOTCHAS`, substrate properties) must not affect any existing format adapter's output.

**Existing test impact:** none. The work package adds capability; existing components and exports are functionally unchanged.

## 9. Acceptance criteria

1. `python -m pytest` passes; test count up by at least 15 (the tests above; small variations acceptable).
2. Every registered component class has `is_through_hole`, `is_smd`, `is_breadboard_compatible`, `is_perfboard_compatible`, `is_pcb_compatible`, `is_dead_bug_compatible` accessible as boolean properties.
3. The four substrate booleans compose under `and` / `or` exactly as the user requested: `part.is_breadboard_compatible and part.is_pcb_compatible` returns a `bool`.
4. `docs/substrate-compatibility-audit.md` exists and lists every registered class with its four substrate booleans; the audit test (Test 5) passes.
5. The `assembly_guide` format is registered in the renderer registry; `list_formats()` includes it; `circuitry export <file> --format assembly_guide --output guide.md` works at the CLI.
6. `export(design, 'assembly_guide', path)` produces a Markdown file with the four-section recipe structure for every breadboard-compatible demo.
7. The exporter refuses (with `BreadboardIncompatibleError`) any design containing SMD parts; the error message names every offending part.
8. Gotchas appear deduplicated, in stable order, in the *Notes & Gotchas* section.
9. Golden tests pass for every breadboard-compatible demo's assembly guide.
10. Every other format's golden tests continue to pass byte-identically.
11. No setters introduced; no new mutator methods; `__slots__` and `@validate_call` discipline preserved.
12. The `BreadboardIncompatibleError` class is in `framework/errors.py` under the `FormatError` family with multi-inheritance from `ValueError` per the established pattern.

## 10. Out of scope

- **SVG visual rendering of the breadboard.** The assembly guide is text-only. The placement algorithm produces enough metadata that a future SVG renderer could consume it; spec'ing the visualiser is a separate work package.
- **Relationship-based gotchas.** "LED wired without a series resistor" requires walking the wiring graph and detecting topological patterns. Start with presence-based gotchas; add relationship detection in a follow-on when there's a real consumer.
- **Compatibility with non-listed substrates.** Eurorack panels, Veroboard, point-to-point copper-tape — out of scope. The four substrates listed cover ≥99% of hobbyist workflows.
- **Auto-routing optimisation.** The placement is deterministic and simple; it doesn't minimise jumper length or avoid crossings. A future "good auto-router" would be a separate undertaking.
- **Per-instance footprint override.** Same as the existing footprint deferral — class-level only.
- **A "build difficulty" rating.** Estimating skill level required from the BOM is not a problem the framework should attempt.
- **Localisation of gotcha strings.** English only; gotchas as `tuple[str, ...]`. A future i18n pass could replace the strings with translation keys.
- **`assembly_guide` for `Board` and `Assembly`.** Multi-board designs aren't usefully assembled on a single breadboard. Refuse politely if the top-level design is a `Board` or `Assembly` rather than a `Circuit`.

## Appendix A — Breadboard topology primer

A standard 830-point solderless breadboard has four kinds of holes, in
three distinct connection groups:

**The terminal strips** (the main area). Five-hole tie strips running
perpendicular to the trough. The board has 63 positions along its long
axis. Each position contains two tie strips:

- The **upper** tie strip — five holes labelled A, B, C, D, E running
  away from the trough. All five holes are electrically the same node.
- The **lower** tie strip — five holes labelled F, G, H, I, J. Same
  rule: all five are one node.

The trough between row E and row F is a physical and electrical gap —
the upper and lower tie strips at the same position are separate nodes,
joined only by whatever component or jumper bridges them.

Holes at different positions are **always separate**. Position 5's
upper tie strip and position 6's upper tie strip are independent nodes;
the user must run a jumper to connect them.

**The power rails** (the long strips along the top and bottom edges).
Two parallel rails on each side, conventionally:

- Top rails: `+` (red, often marked with a `+` symbol) and `-` (blue or
  black, marked `-`).
- Bottom rails: same.

Each rail is a single long node. On some boards (most commonly the
breadboards intended for chained / extended use) each top rail is split
into two equal-length halves at the midpoint of the board, with a
visible break in the colored stripe — the two halves are independent
unless the user bridges them with a jumper. **The implementer should
assume split rails by default** and the assembly-guide output should
include the bridging-jumper instruction explicitly when the design uses
the full length of either rail; users with continuous-rail boards can
skip those jumpers without harm.

**Where a DIP chip goes.** A DIP-N chip straddles the trough. Pin 1's
hole is at one position, row E; pin 2 at the adjacent position, row E;
the row continues across positions until pin N/2 at position
`start + N/2 - 1`, row E. Pin N/2 + 1 sits in the same position as pin
N/2 but on the other side of the trough (row F), and the pins continue
back across positions to pin N at the starting position, row F.

For a DIP-14 starting at position 10, the pins land at:

| Pin | Position | Row |
|----:|---------:|----:|
|   1 |       10 |   E |
|   2 |       11 |   E |
|   3 |       12 |   E |
|   4 |       13 |   E |
|   5 |       14 |   E |
|   6 |       15 |   E |
|   7 |       16 |   E |
|   8 |       16 |   F |
|   9 |       15 |   F |
|  10 |       14 |   F |
|  11 |       13 |   F |
|  12 |       12 |   F |
|  13 |       11 |   F |
|  14 |       10 |   F |

Each pin's tie strip extends along that pin's full row letter range —
pin 1's tie strip includes 10A, 10B, 10C, 10D, and 10E. Any of those
five holes is a valid jumper destination for "pin 1 of U1."

**Where a 2-terminal part goes.** A through-hole resistor (or LED, or
capacitor, or diode) has two leads. The two leads must land in **tie
strips at different positions** — otherwise the part is plugged into
the same node at both ends and does nothing electrically.

The lead spacing varies by part:

- Bent ¼-W axial resistor: leads about 7.6 mm apart (≈ 3 hole pitches).
- Through-hole LED: leads at 2.54 mm pitch (1 hole pitch); they can
  also be bent further for breadboard convenience.
- TO-92 transistor: three leads in a row, 2.54 mm pitch.

The placement algorithm in §5.2 chooses lead spacing per `LAYOUT.kind`
on the component class.

**Polarity and orientation.** Diodes, LEDs, electrolytic capacitors,
and IC chips are polarised. The framework's topology check can't catch
a reversed polarised part — both leads are valid Ports — so the
`GOTCHAS` strings on each polarised component class spell out which
lead is which.

**Why this matters.** The assembly-guide output uses the language of
positions and tie strips throughout. The implementer should keep this
appendix open while writing the placement algorithm and the example
output, because the conventional language of "row" and "column" varies
across breadboard tutorials and is exactly the source of the kind of
silent-mistake the topology check is supposed to prevent.
