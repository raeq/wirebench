# Export Framework + SPICE Exporter — Implementation Spec

## 1. Purpose

Give the codebase a generic framework for emitting `.circuitry` designs to industry-standard netlist and schematic formats, and land **SPICE** as the first concrete consumer. The framework provides the shared mechanics — hierarchical walking, logical-net computation, refdes/net-name synthesis, per-component renderer registration — so each format adapter focuses only on its target syntax. Future formats (KiCad netlist, EDIF, Yosys JSON, netlistsvg, Graphviz) plug into the same machinery.

After this work, the workflow becomes: design in Python → save `.circuitry` → run `export(design, 'spice', 'design.cir')` → hand the output to ngspice, LTspice, KiCad's simulator, or any tool that imports SPICE.

## 2. Scope

**In scope** — the export framework (logical-net walker reused from `Circuit._validate`, hierarchical-walk helpers, `ExporterContext`, renderer registry, top-level `export()` / `export_to_string()` / `list_formats()` APIs); a complete SPICE adapter covering every component in the current library (passives, the five chips, all connectors, Boards, Assemblies); a default SPICE model library shipped with the package (`spice-models.lib`) providing models for the chips so generated `.cir` files simulate out of the box.

**Out of scope** — concrete adapters for KiCad netlist, EDIF, Yosys JSON, Graphviz, Mermaid, netlistsvg (each is a follow-on work package using this framework); real circuit simulation (we emit, we don't simulate); PCB-layout artefacts (no x/y, no footprints, no routing); SPICE-specific simulation directives beyond the structural minimum (`.AC`, `.TRAN`, `.DC` sweeps — the user adds those by hand if they want them); analog modelling of components whose current model is logic-level only (resistors emit numerically, but the simulator-fed behaviour matches the framework's no-op `evaluate()` rather than real Ohm's-law dynamics — this is a deliberate framework limitation, not a SPICE limitation).

**Prerequisites** — refdes, pin-id, board+connector, `.circuitry` format and pydantic adoption specs all implemented. This spec assumes `IS_CONDUCTOR`-based logical-net computation, the registry, `save_circuitry` / `load_circuitry`, every component's refdes and `PinId`, and `@validate_call` discipline all exist.

## 3. Constraints carried over from CLAUDE.md and prior specs

- Physical fidelity is primary. The export framework describes physical things — components with refdes, contacts with pin numbers, wires forming nets — in the syntax each target format expects. Exporters do not invent abstractions that don't correspond to a physical fact.
- `__slots__` discipline preserved on every new class (`LogicalNet`, `ExporterContext`).
- No setters; no mutators on the design model during export. Export reads; it never writes back to the design.
- Pydantic v2 for configuration shapes (`ExportConfig` etc.) and `@validate_call` on every public framework function.
- Registry-mediated dispatch. Renderers are looked up by `(component_class, format_name)` in an explicit registry, never via `importlib` or `eval`. Same security boundary as the component registry.
- The IS_CONDUCTOR walk is the canonical logical-net algorithm. Exporters use it, never re-derive their own.

## 4. Architecture overview

Three layers:

1. **Framework layer** — `src/framework/export/` package. Holds the renderer registry, the `ExporterContext`, the logical-net walker (extracted from `Circuit._validate` into a standalone function), hierarchical-walk helpers, and the top-level `export()` API. Format-agnostic.
2. **Adapter layer** — one module per target format under `src/framework/export/<format>/`. Each module registers renderers for every component class. The adapter knows the format's syntax; the framework calls into it via the registry.
3. **Format layer** — the actual text that goes to disk. Produced by the adapter, written by the framework.

Hierarchy is mirrored in the file system:

```
src/framework/export/
    __init__.py            # top-level export() API
    base.py                # ExporterContext, registry, walker entry points
    nets.py                # extracted logical-net walker
    walk.py                # hierarchical walk helpers
    spice/
        __init__.py        # SPICE adapter entry point
        renderers.py       # @register_renderer(...) for every component
        models.py          # SPICE .MODEL emission helpers
        spice-models.lib   # shipped default model library
```

Future formats add a sibling sub-package: `export/kicad/`, `export/edif/`, `export/yosys/`, etc.

## 5. The framework layer

### 5.1 Logical-net extraction (`framework/export/nets.py`)

The IS_CONDUCTOR walker currently lives as a method on `Circuit._validate`. Extract it into a standalone, reusable form:

```python
from dataclasses import dataclass
from framework.factor import FactorNode
from framework.port import Port

@dataclass(frozen=True, slots=True)
class LogicalNet:
    """An extended electrical net — the set of Nodes connected through
    IS_CONDUCTOR components plus the real (non-conductor) ports attached
    to it.

    id        — stable integer assigned during the walk; unique per
                 design.
    nodes     — set of Node ids (`id(node)`) that compose this logical
                 net.
    ports     — tuple of (owner, port) pairs of non-conductor ports
                 attached to this net. Order is sorted by owner refdes
                 (where applicable) then port name, for deterministic
                 emission.
    """
    id: int
    nodes: frozenset[int]
    ports: tuple[tuple[FactorNode, Port], ...]


def compute_logical_nets(design: FactorNode) -> list[LogicalNet]:
    """Walk `design` and return one LogicalNet per electrical net.

    The walker descends recursively through Circuit / Board / Chip
    composites and treats every FactorNode with IS_CONDUCTOR=True
    (Pin, primarily) as a pass-through. Two Nodes joined by a conductor
    are members of the same LogicalNet.
    """
```

The `Circuit._validate` per-net check is refactored to call `compute_logical_nets(self)` and inspect the result, so the algorithm exists in exactly one place.

### 5.2 Hierarchical walk (`framework/export/walk.py`)

Exporters often need to visit each composite (Assembly / Board / Chip) and emit a corresponding bracket in the output (a `.SUBCKT` block in SPICE, a hierarchical sheet in KiCad). The walker exposes:

```python
def walk_hierarchy(design: FactorNode, visitor: Callable[[Composite, Path], None]) -> None:
    """Depth-first walk of composite components.

    `visitor` is called for every Board / Chip / Assembly encountered,
    with the composite instance and the hierarchical refdes path that
    led to it ('A2.U1' for chip U1 inside board A2). Leaf components
    (passives, connectors) are not visited — they're handled by the
    adapter's per-component renderer.
    """
```

`Path` is a small frozen value object (`@dataclass(frozen=True, slots=True)`) carrying a tuple of refdes segments. Helpers: `Path.empty()`, `Path.with_child(refdes)`, `Path.qualified_refdes()` returning the dotted form.

### 5.3 The renderer registry (`framework/export/base.py`)

A typed dispatch table keyed by `(component_class, format_name)`:

```python
from typing import Callable, TypeVar
from framework.factor import FactorNode

T = TypeVar('T', bound=FactorNode)

_RENDERERS: dict[tuple[type[FactorNode], str], Callable] = {}


def register_renderer(
    component_class: type[T],
    *,
    format: str,
):
    """Decorator: register a function that renders an instance of
    `component_class` in the given `format`. The function signature is

        (component: T, ctx: ExporterContext) -> str

    The returned string is the format-specific text fragment for one
    component instance (typically one or more lines)."""
    def decorator(fn):
        key = (component_class, format)
        if key in _RENDERERS:
            raise ValueError(
                f"Renderer for {component_class.__name__} in format "
                f"{format!r} already registered."
            )
        _RENDERERS[key] = fn
        return fn
    return decorator


def lookup_renderer(component_class: type[FactorNode], format: str) -> Callable:
    """Look up a renderer by walking the class's MRO.

    Dispatch is by Python's standard method-resolution order: the most
    specific class with a registered renderer wins; fall back to parents
    if no exact match. This lets an abstract class (e.g. `Connector`)
    register a single default renderer that every concrete subclass
    inherits — while still allowing a specific subclass to override.
    Same semantics as functools.singledispatch."""
    for cls in component_class.__mro__:
        key = (cls, format)
        if key in _RENDERERS:
            return _RENDERERS[key]
    available = sorted({f for (cls, f) in _RENDERERS if cls is component_class})
    raise KeyError(
        f"No {format!r} renderer reachable via MRO for "
        f"{component_class.__name__}. Available formats registered "
        f"directly on this class: {available or '(none)'}."
    )
```

**Connector renderers register at the abstract `Connector` class, not per concrete subclass.** All ~30 concrete connector classes share the same SPICE rendering — they emit nothing, because the IS_CONDUCTOR walker has already collapsed their pins into the surrounding logical net. Registering once at `Connector` and letting MRO dispatch deliver it to `Header2xNFemale`, `USBCReceptacle`, `JSTPHBoardSide`, etc., reflects the physical fact that *the category* (not each individual part) is the transparent thing:

```python
@register_renderer(Connector, format='spice')
def render_connector_spice(c: Connector, ctx: ExporterContext) -> str:
    return ""
```

A specific connector class that needed non-trivial rendering in some future format would register its own entry; the MRO walk picks the more-specific one. This is the same pattern `functools.singledispatch` uses, and it's the right substrate for future formats (KiCad netlists *do* reference connector pins; a KiCad connector renderer also lives at `Connector` level, with the same one-line shape).

Renderers are discovered by importing the adapter sub-package. The adapter's `__init__.py` imports its `renderers` module, which executes the `@register_renderer` decorators at import time.

### 5.4 `ExporterContext`

Per-export shared state. Tracks net naming, refdes enumeration, output accumulation, and adapter-specific configuration.

```python
class ExporterContext:
    __slots__ = ('_design', '_format', '_logical_nets', '_net_names',
                 '_lines', '_config', '_models_used')

    def __init__(
        self,
        design: FactorNode,
        format: str,
        config: 'ExportConfig | None' = None,
    ) -> None:
        self._design = design
        self._format = format
        self._logical_nets = compute_logical_nets(design)
        self._net_names = self._assign_net_names()
        self._lines: list[str] = []
        self._config = config or ExportConfig()
        self._models_used: set[str] = set()

    def net_name(self, port_or_node) -> str:
        """Return the format-specific name for the net containing the
        given Port or Node. Adapter-overridable via config.net_namer."""
        ...

    def refdes_of(self, component: FactorNode) -> str:
        """Return the refdes for refdes-bearing components, or a
        synthesised id (`Rail_0`, `Ground_0`, …) for those that don't
        carry one."""
        ...

    def emit(self, text: str) -> None:
        """Append a line (or multi-line block) to the output."""
        self._lines.append(text)

    def register_model(self, model_name: str) -> None:
        """Note that this exporter run uses the named model. Used by
        SPICE to emit only the needed `.MODEL` / `.LIB` directives."""
        self._models_used.add(model_name)

    def output(self) -> str:
        return '\n'.join(self._lines) + '\n'
```

### 5.5 The top-level API (`framework/export/__init__.py`)

```python
from pathlib import Path
from pydantic import validate_call

@validate_call(config={'arbitrary_types_allowed': True})
def export(
    design: FactorNode,
    format: str,
    path: Path | str,
    config: 'ExportConfig | None' = None,
) -> None:
    """Export a design to a file in the given format.

    Discovers the adapter by importing framework.export.<format> (any
    side-effecting registry calls happen on import). Walks the design
    via compute_logical_nets and walk_hierarchy, invokes the registered
    renderer for each component, and writes the assembled output to
    `path`.

    Raises:
        ValueError — unknown format name (no adapter sub-package found).
        KeyError   — a component class in the design has no registered
                     renderer for the requested format. Error message
                     names the class and lists the registered formats.
    """

@validate_call(config={'arbitrary_types_allowed': True})
def export_to_string(
    design: FactorNode,
    format: str,
    config: 'ExportConfig | None' = None,
) -> str:
    """Same as export() but returns the formatted text instead of
    writing to disk. Useful for testing and for callers that route
    output elsewhere."""

def list_formats() -> list[str]:
    """List the names of every adapter sub-package found under
    framework.export/. Imports each one to trigger renderer
    registration."""
```

### 5.6 `ExportConfig`

A pydantic `BaseModel` carrying optional per-export tuning. Common fields:

```python
class ExportConfig(BaseModel):
    """Configuration for an export run. Most fields have sensible
    defaults; adapters read additional format-specific fields from
    `format_config` (a sub-model namespaced per format)."""

    include_header_comment: bool = True
    net_name_style: Literal['numeric', 'qualified', 'short_hash'] = 'numeric'
    include_unused_pins: bool = False  # connector pins not wired internally
    model_config = {'extra': 'forbid'}
```

Per-adapter config is added by subclassing (e.g., `SpiceExportConfig(ExportConfig)` with SPICE-specific fields like `model_library_path`, `default_supply_voltage`, `emit_models_inline`).

## 6. The SPICE adapter

### 6.1 SPICE format primer

A SPICE deck (`.cir` file) is a line-oriented text format:

- `* comment` — comment line.
- `.TITLE <text>` — first line, design name.
- `.MODEL <name> <type>(<params>)` — declare a SPICE model (diode, transistor, etc.).
- `.LIB <path>` — include an external model library.
- `.SUBCKT <name> <pin1> <pin2> ...` — start a subcircuit definition; pins listed in order.
- `.ENDS <name>` — end of subcircuit.
- `R<n> <node1> <node2> <value>` — resistor.
- `C<n> <node1> <node2> <value>` — capacitor.
- `D<n> <anode> <cathode> <model>` — diode (LED uses this with a diode model).
- `V<n> <node+> <node-> DC <voltage>` — voltage source.
- `X<n> <node1> <node2> ... <subcircuit_name>` — subcircuit instance.
- `0` is the reserved ground net.
- `.END` — end of deck.

Hierarchical designs use `.SUBCKT` definitions per Board / Chip, with `X` instances in the parent.

### 6.2 Net naming for SPICE

The default `net_name_style='numeric'` assigns `1`, `2`, … to logical nets in the order they appear during the walk. A `Rail(False)` instance on a net forces that net's name to `0` (SPICE's reserved ground). A `Rail(True)` instance forces its net to `vcc`. Other Rails get named `<refdes_or_id>_net`.

There is no `Ground` component class in the codebase; ground identity is carried entirely by `Rail(False)` presence on a logical net. This matches real EDA tools — KiCad's `GND` is a passive "power flag" symbol, not a soldered part; SPICE's ground is the reserved net `0`, not a component.

### 6.3 Per-component SPICE renderers

Each component class needs a SPICE renderer registered in `framework/export/spice/renderers.py`. The renderers read these read-only properties on components (added by this work package — see §8):

- `Resistor.ohms` (`@property` returning `float`).
- `LED.color` (`@property` returning `str`; complements the existing `LED.lit`).
- `Rail.level` (`@property` returning `bool`).

These are observable physical facts about the part (resistance value, LED colour, rail polarity) — read-only properties per CLAUDE.md's allowance for observing internal state.

**Resistor** (`R<refdes> <n1> <n2> <ohms>`):

```python
@register_renderer(Resistor, format='spice')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    n1 = ctx.net_name(r.ports['t1'])
    n2 = ctx.net_name(r.ports['t2'])
    return f"{r.refdes} {n1} {n2} {r.ohms}"
```

**LED** (diode with a diode model):

```python
@register_renderer(LED, format='spice')
def render_led(d: LED, ctx: ExporterContext) -> str:
    anode = ctx.net_name(d.ports['anode'])
    cathode = ctx.net_name(d.ports['cathode'])
    ctx.register_model('D_LED')
    return f"{d.refdes} {anode} {cathode} D_LED"
```

The shipped model library declares `D_LED` with a typical red-LED V_F.

**Rail** — `Rail(True)` emits a DC voltage source on its net; `Rail(False)` emits nothing and pins its net to `0` (handled by the net-namer in §6.2):

```python
@register_renderer(Rail, format='spice')
def render_rail(r: Rail, ctx: ExporterContext) -> str:
    if r.level is True:
        v = ctx.config.default_supply_voltage  # e.g., 5.0
        return f"V_{ctx.refdes_of(r)} {ctx.net_name(r.ports['out'])} 0 DC {v}"
    return ""  # Rail(False) collapses to net 0; no source needed
```

**Chips** — each chip is an `X` instance pointing at a `.SUBCKT` defined in the model library. The renderer emits one net per *present* pin in datasheet pin-number order; pins the model omits (typically VCC and GND on chips where they're not modelled) are absent from `chip.pins` and so are absent from the emitted line. The `.SUBCKT` definition in the shipped model library must declare exactly the same pin list in the same order — that's the contract between renderer and model:

```python
@register_renderer(SN74HC04, format='spice')
def render_sn74hc04(u: SN74HC04, ctx: ExporterContext) -> str:
    nets = [ctx.net_name(pin.external)
            for pin in sorted(u.pins, key=lambda p: p.id.number)]
    ctx.register_model('SN74HC04')
    return f"{u.refdes} {' '.join(nets)} SN74HC04"
```

The same shape applies to `CD4069`, `LM393`, `CD4043`, `ULN2003A` — one renderer each, each registering its model name.

**Connectors** — registered once at the `Connector` base class per §5.3; MRO dispatch delivers the same `return ""` renderer to every concrete subclass. No per-class stub required.

```python
@register_renderer(Connector, format='spice')
def render_connector_spice(c: Connector, ctx: ExporterContext) -> str:
    return ""
```

**Boards** — emit a `.SUBCKT` definition wrapping the board's components, then an `X` instance from the parent:

```python
@register_renderer(Board, format='spice')
def render_board(b: Board, ctx: ExporterContext) -> str:
    surface_nets = ' '.join(ctx.net_name(p) for _, p in sorted(b.ports.items()))
    body_lines = [f".SUBCKT {b.refdes}_SUBCKT {surface_nets}"]
    body_lines.extend(_render_children(b, ctx))
    body_lines.append(f".ENDS {b.refdes}_SUBCKT")
    instance = f"X{b.refdes} {surface_nets} {b.refdes}_SUBCKT"
    return instance + "\n" + "\n".join(body_lines)
```

`_render_children` is a private helper in the SPICE module that walks `b._factor_nodes`, calls `lookup_renderer` per child, and joins the output.

### 6.4 Library and model management

`framework/export/spice/spice-models.lib` ships with the package and contains:

```spice
.MODEL D_LED D(IS=1E-15 N=2.0)

.SUBCKT SN74HC04 a_1 y_1 a_2 y_2 a_3 y_3 y_4 a_4 y_5 a_5 y_6 a_6
* TI SN74HC04 hex inverter — behavioural placeholder.
* Replace with vendor-supplied model for accurate simulation.
EY1 y_1 0 VALUE = { IF(V(a_1) > 2.5, 0, 5) }
EY2 y_2 0 VALUE = { IF(V(a_2) > 2.5, 0, 5) }
...
.ENDS SN74HC04

.SUBCKT CD4069 ...
.ENDS CD4069

* (analogous .SUBCKT blocks for LM393, CD4043, ULN2003A)
```

The behavioural models are placeholders that exercise the deck structurally — they let the user run `ngspice design.cir` and see signals propagate. Production simulation needs vendor-supplied models; the user can replace by passing `model_library_path='/path/to/vendor.lib'` in `SpiceExportConfig`, or by editing the deck.

`emit_models_inline=True` (config flag, default `False`) inlines the model definitions at the top of the deck instead of referencing the library. Useful for self-contained decks.

### 6.5 The SPICE deck assembly

```python
# framework/export/spice/__init__.py

def export_spice(design: FactorNode, ctx: ExporterContext) -> str:
    if ctx.config.include_header_comment:
        ctx.emit(f"* Exported from circuitry — {datetime.now().isoformat()}")
    name = getattr(design, 'name', None) or type(design).__name__
    ctx.emit(f".TITLE {name}")

    # Walk and render — recursing into Boards via render_board, which
    # emits .SUBCKT blocks; top-level non-Board components emit
    # directly.
    for fn in _walk_top_level(design):
        renderer = lookup_renderer(type(fn), 'spice')
        ctx.emit(renderer(fn, ctx))

    if ctx.config.emit_models_inline:
        ctx.emit(_inline_models(ctx))
    else:
        ctx.emit(f".LIB {ctx.config.model_library_path}")

    ctx.emit(".END")
    return ctx.output()
```

The top-level dispatcher in `framework/export/__init__.py` imports `framework.export.spice` (which registers all renderers via decorators) and calls `export_spice(design, ctx)`.

## 7. CLI

A small CLI front-end in `src/cli/export.py`:

```
$ circuitry export design.circuitry --format spice --output design.cir
$ circuitry export design.circuitry --format spice  # stdout
$ circuitry export --list-formats
spice
```

Built with `argparse` for now (no extra dependency). Pydantic validates the parsed args via `validate_call` on the underlying `export()` function.

## 8. File-by-file change list

New files:

- `src/framework/export/__init__.py` — top-level `export()`, `export_to_string()`, `list_formats()`.
- `src/framework/export/base.py` — `ExporterContext`, `ExportConfig`, renderer registry, `register_renderer`, `lookup_renderer`.
- `src/framework/export/nets.py` — extracted `compute_logical_nets()` and `LogicalNet` dataclass.
- `src/framework/export/walk.py` — `walk_hierarchy()` and `Path` value object.
- `src/framework/export/spice/__init__.py` — SPICE adapter entry point (`export_spice`).
- `src/framework/export/spice/renderers.py` — every SPICE `@register_renderer(...)`.
- `src/framework/export/spice/models.py` — SPICE `.MODEL` / `.LIB` emission helpers.
- `src/framework/export/spice/spice-models.lib` — shipped default SPICE model library.
- `src/cli/__init__.py`, `src/cli/export.py` — CLI front-end.
- `tests/framework/export/test_nets.py` — logical-net walker tests (round-trip with the extracted version vs. `_validate`'s behaviour).
- `tests/framework/export/test_registry.py` — renderer registry tests.
- `tests/framework/export/test_spice_components.py` — per-component SPICE renderer tests (assert each emits the expected text fragment for a simple known design).
- `tests/framework/export/test_spice_water_alarm.py` — end-to-end SPICE export of `WaterAlarm` and `WaterAlarmAssembly`; assert the produced deck parses (optionally pipe to `ngspice -b` if available; otherwise structural regex checks).

Modified files:

- `src/framework/circuit.py` — `Circuit._validate`'s logical-net algorithm refactors to call `framework.export.nets.compute_logical_nets()` rather than duplicating the walker.
- `src/components/passives/resistor.py` — add `@property def ohms(self) -> float: return self._ohms`.
- `src/components/passives/led.py` — add `@property def color(self) -> str: return self._color`. (`lit` already exists.)
- `src/components/passives/rail.py` — add `@property def level(self) -> bool: return self._level`.
- `pyproject.toml` — add an entry point for the CLI (`circuitry = "cli.export:main"`). No new third-party dependency.

Unmodified:

- Every component class. Component classes do not gain export methods — all SPICE logic lives in the adapter. Same for future format adapters.
- The `.circuitry` format module. Export reads the live model; it doesn't need to round-trip through `.circuitry`. (A convenience helper `export_from_file(circuitry_path, format, output_path)` calls `load_circuitry` then `export`.)

## 9. Test plan

`tests/framework/export/test_nets.py`:

1. **`compute_logical_nets` matches `_validate`'s behaviour.** For each existing application (`WaterAlarm`, `WaterAlarmAssembly`), the extracted walker returns the same nets `_validate` was computing internally before the refactor. Compare net membership sets.
2. **Mated connectors collapse into one net.** A two-board assembly with a 2-pin header mate produces one logical net per mated pin pair (i.e. 2 nets, not 4).
3. **Conductors are excluded from the port list.** `LogicalNet.ports` contains the real (non-conductor) ports only — chip cell ports, Rail OUT, LED IN, etc.; Pin externals/internals are not in the list.

`tests/framework/export/test_registry.py`:

4. **Renderer lookup succeeds.** `lookup_renderer(Resistor, 'spice')` returns the registered function.
5. **Unknown format raises with available-formats hint.** `lookup_renderer(Resistor, 'nonexistent')` raises `KeyError` mentioning `'spice'`.
6. **Duplicate registration raises.** Re-registering `(Resistor, 'spice')` raises `ValueError`.
7. **Every component class has a SPICE renderer reachable via MRO.** Walk every registered class in the component registry; assert `lookup_renderer(cls, 'spice')` succeeds for each (either by direct registration or by MRO fallback to an ancestor like `Connector`). Catches missing renderers before they fail at export time.
7b. **MRO dispatch works for connectors.** `lookup_renderer(Header2xNFemale, 'spice')` returns the renderer registered on `Connector`. `lookup_renderer(USBCReceptacle, 'spice')` returns the same one. Registering a `USBCReceptacle`-specific renderer (in a test) overrides the `Connector` default for that class only.

`tests/framework/export/test_spice_components.py`:

8. **Resistor renders to `R<refdes> <n1> <n2> <ohms>`.** Build a one-resistor design (Resistor + Rail + Ground wired); export to SPICE; assert the line `R1 vcc 0 330` (or whatever the chosen value) appears.
9. **LED renders with diode model.** Build LED + Rail + Ground; export; assert `D1 ... D_LED` line plus the `D_LED` model is registered/emitted.
10. **Rail(True) emits a voltage source.** Assert `V_Rail_<n> vcc 0 DC 5` appears.
11. **Rail(False) collapses to net 0 with no source emitted.** Assert no `V_` line corresponds to it.
12. **Chip renders as X instance with ordered pins.** Build SN74HC04 + minimum wiring; export; assert `U1 <12 nets> SN74HC04` with nets in pin-number order.
13. **Connectors emit nothing.** Build a board with a header; assert the export contains no line per connector contact.
14. **Board emits .SUBCKT block.** Build a one-board assembly; export; assert `.SUBCKT A1_SUBCKT ...` and `.ENDS A1_SUBCKT` bracket the board's components, and `X1 ... A1_SUBCKT` invokes it from top level.

`tests/framework/export/test_spice_water_alarm.py`:

15. **`WaterAlarm` exports to a structurally valid deck.** Run `export(WaterAlarm(), 'spice', tmp_path / 'wa.cir')`. Assert: file exists, has a `.TITLE`, an `.END`, every Resistor / LED / Chip line is present, no orphan refdes.
16. **`WaterAlarmAssembly` exports with .SUBCKT hierarchy.** Same as above plus assert two `.SUBCKT` blocks (one per Board) and the matching `X` instances at top level.
17. **Optional: ngspice round-trip.** If `ngspice` is on PATH, run `ngspice -b -o /dev/null <deck>` and assert exit code zero (the deck parses and the analysis runs). Skip cleanly when ngspice isn't installed (`pytest.mark.skipif(not shutil.which('ngspice'))`).

Existing-test impact: `Circuit._validate`'s extracted walker behaves identically to the pre-refactor version, so the board+connector spec's tests for floating nets, multi-driver shorts, and cross-board net detection all continue to pass without changes.

## 10. Acceptance criteria

The work is done when:

1. `python -m pytest` passes; new test count up by at least the 14 tests in §9.
2. `framework.export.export(design, 'spice', path)` produces a `.cir` file for every existing application.
3. Every component class registered in the framework's component registry has a SPICE renderer reachable via MRO (test 7 above) — typically one direct registration per chip/passive plus one shared registration at the `Connector` base.
4. `compute_logical_nets` is the single source of truth for logical-net computation; `Circuit._validate` calls it rather than maintaining a duplicate walker.
5. The CLI works: `circuitry export design.circuitry --format spice --output design.cir`.
6. The shipped `spice-models.lib` is referenced by exported decks by default; `emit_models_inline=True` produces a self-contained deck instead.
7. `list_formats()` returns `['spice']`. Adding a new format adapter directory under `framework/export/` and importing it via `list_formats()` registers it automatically.
8. No setters added; `__slots__` discipline preserved on `LogicalNet`, `ExporterContext`, `Path`, `ExportConfig`.
9. The optional ngspice round-trip test passes when ngspice is installed; skips cleanly otherwise.

## 11. Out of scope (for follow-on work packages)

- **KiCad netlist exporter** (`format='kicad'`). S-expression file with `(components ...)` and `(nets ...)` records. Imports straight into Pcbnew for layout. Per-component renderers analogous to SPICE.
- **EDIF 2 0 0 exporter** (`format='edif'`). IEEE-standard hierarchical interchange. Verbose but the only "real" standard.
- **Yosys JSON exporter** (`format='yosys'`). For the digital subset. Renders to SVG via netlistsvg for browser-readable schematics. Lossy on analog parts (resistors, LEDs).
- **Graphviz / Mermaid exporter** (`format='dot'` or `'mermaid'`). Block-diagram visualisation, not a circuit standard. Good for documentation.
- **Schematic-image (SVG) exporter.** Renders a styled schematic directly. Significant work; depends on placement information that the model doesn't yet carry.
- **Bidirectional KiCad** — round-trip KiCad → `.circuitry` → KiCad. Requires the KiCad exporter plus an importer.
- **Vendor-supplied SPICE models.** The shipped library has behavioural placeholders. Real production simulation wants vendor models (TI, ON Semi, Maxim Integrated). The user supplies the path via `model_library_path` config.
- **Analog circuit simulation in-process.** Even with SPICE export, we don't simulate — we hand off to ngspice / LTspice / vendor tools. A future in-process simulator is a separate undertaking.
- **Mass-registration helper** — `@register_renderer_for_all_subclasses(Connector, format='spice')`. Would eliminate the ~30 trivial connector stubs in the SPICE adapter. Add when it stops being optional.
- **Multi-output adapters.** Some formats emit several files (KiCad project = `.kicad_sch` + `.kicad_pcb` + `.kicad_pro`). The current `export()` API writes one file; multi-file adapters need a directory-output mode.
- **Schema-versioned exports.** Output files don't carry the `.circuitry` source format-version. Decisions about traceability metadata in exports are deferred.
