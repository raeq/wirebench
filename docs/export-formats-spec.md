# Export Formats — Implementation Spec

## 1. Purpose

Extend the export framework with adapters for every netlist / visualisation / BOM format that's ubiquitous in modern electronics workflows. Reuse the framework's existing machinery — the renderer registry, MRO dispatch, `ExporterContext`, `compute_logical_nets`, and the topology / golden-file verification patterns just landed for SPICE — so every new adapter is structurally the same shape as `spice/`.

After this work, `list_formats()` returns at least `['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys']`, and a circuitry design can be handed to KiCad (for layout), Graphviz / Mermaid (for documentation), netlistsvg (for browser-rendered digital schematics), and any fab house (for procurement) — all from the same source.

## 2. Scope

**In scope.** Five new format adapters, each landing as a sub-package under `framework/export/`:

- **KiCad netlist** (`.net`, S-expression, format version "E") — imports into KiCad's Eeschema / Pcbnew for layout.
- **Graphviz DOT** (`.dot`) — renders to SVG / PNG / PDF via the `dot` command; universally available.
- **Mermaid** (`.mmd`) — renders natively in GitHub / GitLab READMEs and via the `mmdc` CLI.
- **Yosys JSON** (`.json`) — consumed by `netlistsvg` for browser-readable digital schematics.
- **BOM CSV** (`.csv`) — bill of materials for procurement; universal.

Every adapter ships with **robust verification**: per-component renderer tests, end-to-end exports for `WaterAlarm` and `WaterAlarmAssembly`, topology cross-reference tests (where applicable), golden files in `tests/golden/<format>/`, format-syntactic validation (parse with a real parser library where one exists), and optional external-tool round-trip (skip cleanly when the tool isn't installed).

**Out of scope.** EDIF 2 0 0 / IEEE 1647 (verbose, declining usage, less ubiquitous than the five above — separate work package if a real need surfaces); Verilog / VHDL gate-level netlists (RTL-oriented; doesn't map naturally from physical-circuit modelling); PCB-layout artefacts (Gerber, drill files — require placement information); SVG schematic rendering directly from circuitry (without going through netlistsvg); Altium-specific formats (proprietary, marginal in OSS workflows).

**Prerequisites.** All previous specs implemented and verified: refdes, pin-id, board+connector, `.circuitry` format, pydantic adoption, export framework + SPICE. This spec assumes `compute_logical_nets`, `lookup_renderer` with MRO dispatch, `ExporterContext`, `register_renderer`, the SPICE adapter's structure under `framework/export/spice/`, and the topology / golden-file test patterns from the previous round.

## 3. Constraints carried over from CLAUDE.md and prior specs

- Physical fidelity is primary. Each format describes physical things — parts with refdes, contacts with pin numbers, wires forming nets — in its native syntax. Adapters do not invent abstractions that don't correspond to a physical fact, even when the target format would let them.
- `__slots__` discipline preserved on every new dataclass / value object.
- No setters; no public mutators. Exporters read from the model; they never write back.
- Pydantic v2 for per-format configuration models (`KiCadExportConfig`, `DotExportConfig`, etc.), each subclassing the existing `ExportConfig` per the export-framework spec.
- Registry-mediated dispatch only. New renderers register via `@register_renderer(component_class, format='<name>')`; MRO walk handles inheritance (e.g., one `Connector`-level entry per format covers the whole connector library).
- The verification bar from the previous round stands: **no softening of tests allowed**. Where a test fails because a renderer is missing or wrong, the fix is to add or correct the renderer — never to lower the assertion bar.

## 4. Format adapters — overview

Each adapter is a sub-package mirroring `framework/export/spice/`:

```
framework/export/<format>/
    __init__.py            # entry point: export_<format>(design, ctx) -> str
    renderers.py           # @register_renderer(...) for every component class
    <format-specific helpers>
```

Common shape per adapter:

- `__init__.py` imports `renderers`, which executes the decorators at import time.
- `renderers.py` registers one entry per refdes-bearing class plus one entry at `Connector` base (inherited by every concrete connector via MRO).
- The adapter's top-level emitter walks the design via `compute_logical_nets` and `walk_hierarchy`, calls `lookup_renderer(type(component), '<format>')` per component, accumulates the result via `ExporterContext.emit`.
- A per-adapter `<Format>ExportConfig(ExportConfig)` model carries format-specific options.

## 5. The five format adapters

### 5.1 KiCad netlist (`framework/export/kicad/`)

S-expression-based netlist format, version "E" (KiCad 7+ compatible). Imported by Eeschema and Pcbnew for layout.

**KiCad `.net` files are flat.** Every component lives at the top level of `(components ...)`; hierarchy is expressed per-component via `(sheetpath ...)` rather than via nested `(sheet)` blocks. Cross-board refdes collisions are resolved by qualifying with the parent board's refdes — KiCad expects globally unique refdes within a netlist.

**File shape:**

```
(export (version "E")
  (design
    (source "WaterAlarmAssembly")
    (tool "circuitry 0.x"))
  (components
    (comp (ref "A1_U1")
      (value "ULN2003A")
      (footprint "Package_DIP:DIP-16_W7.62mm")
      (libsource (lib "Driver_LED") (part "ULN2003A") (description "Darlington array"))
      (sheetpath (names "/A1/") (tstamps "/<hash-of-A1>/")))
    (comp (ref "A1_J1")
      (value "Header2xN_40")
      (footprint "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical")
      (sheetpath (names "/A1/") (tstamps "/<hash-of-A1>/")))
    (comp (ref "A2_U1") (value "SN74HC04") ...
      (sheetpath (names "/A2/") (tstamps "/<hash-of-A2>/")))
    ...)
  (nets
    (net (code "1") (name "vcc")
      (node (ref "A2_U2") (pin "16") (pintype "power_in")))
    (net (code "2") (name "GND")
      (node (ref "A2_U1") (pin "7") (pintype "power_in")))
    (net (code "3") (name "Net-(A1_U1-Pad1)")
      (node (ref "A1_U1") (pin "1") (pintype "input"))
      (node (ref "A1_J1") (pin "3") (pintype "passive")))
    ...))
```

**Per-component renderers** (registered in `kicad/renderers.py`) — each emits a flat `(comp ...)` record with `(sheetpath ...)` carrying the hierarchical path:

- `Resistor` → `(comp (ref "<qualified_refdes>") (value "<ohms>") (footprint "<FOOTPRINT>") (sheetpath ...))`
- `LED` → same shape, value is the colour.
- `Rail`, `GroundDomain` → emit nothing as a component. Rail-induced net names are handled by the net-namer (§6.6).
- Each chip → `(comp (ref "<qualified_refdes>") (value "<chip class name>") (footprint "<DIP-N or SOIC-N>") (sheetpath ...))`
- `Connector` (registered at base, inherited via MRO) → analogous `(comp ...)` record. `value` is the concrete connector class name; `footprint` comes from the class's `FOOTPRINT` property (parameterised connectors compute it from `pin_count` and `pitch_mm` — see §6).
- `Board` → emits *no record of its own*. It only contributes a `sheetpath` segment that each of its children prepends to their own path. The board's refdes (`A1`, `A2`) becomes the path segment.

**Refdes qualification.** When the design contains multiple boards (any `Board`-rooted hierarchy), every component's emitted refdes is prefixed with each ancestor board's refdes, joined by `_`. So sensor-board `U1` becomes `A1_U1`; controller-board `U1` becomes `A2_U1`. This guarantees global uniqueness in the flat netlist while preserving the per-board silkscreen identity (recoverable by splitting on `_`). Standalone `Circuit` designs (no `Board` ancestor) skip qualification.

**`tstamps` generation.** KiCad expects timestamp identifiers per sheet path. We synthesise deterministic ones: SHA-1 of `f"{board.name}|{board.revision}|{board.refdes}"`, truncated to 8 hex chars, formatted as `/<hash>/`. Determinism is mandatory — golden-file tests depend on byte stability.

**Pin types** (`pintype` field):

| Source                                 | KiCad pintype     |
|----------------------------------------|-------------------|
| Chip pin with `Direction.IN`           | `"input"`         |
| Chip pin with `Direction.OUT`          | `"output"`        |
| Chip pin with `Direction.BIDIR`        | `"bidirectional"` |
| Connector contact (any direction)      | `"passive"`       |
| Resistor / LED terminal                | `"passive"`       |
| Rail OUT (power)                       | `"power_out"`     |

The adapter uses a per-component-class mapping (or falls back to `"passive"`) and reads the pin direction from `Pin.role` (chips/connectors) or from `Port.direction` (passives).

**Pin numbers.** Every `(node ...)` carries a `(pin "<n>")` field. The number comes from `pin_number_of(component, port_name)` (see §6.5) — `pin.id.number` for chips/connectors, `PIN_NUMBERS[port_name]` for passives.

**Footprints.** See §6 — class attribute for fixed-geometry parts, `@property` for parameterised families. When the resolved footprint is `None`, the `(footprint ...)` field is omitted; KiCad imports the part as unplaced.

**Net naming.** Provided by the adapter-supplied net-namer (§6.6). For KiCad: `Rail(True)` → `"vcc"`; `Rail(False)` → `"GND"`; other nets → `"Net-(<lowest_qualified_refdes>-Pad<lowest_pin_number>)"`.

**Hierarchical reconstruction in KiCad.** When the user imports the `.net` file into KiCad, the per-component `sheetpath` lets KiCad reconstruct the board structure. Each unique sheet path becomes a sheet symbol; components with `sheetpath` `/A1/` end up inside the sheet labelled `A1`. The hierarchy is round-trippable in the sense that re-export from KiCad would produce the same sheet structure.

### 5.2 Graphviz DOT (`framework/export/dot/`)

Block-diagram visualisation. Bipartite circuit graph: components are box-nodes, nets are circle-nodes, edges connect components to nets.

**File shape:**

```
digraph "WaterAlarm" {
  rankdir=LR;
  node [shape=box, fontname="monospace"];

  // Components
  R1 [label="R1\n330Ω"];
  D1 [label="D1\nred LED"];
  U1 [label="U1\nSN74HC04"];

  // Nets (as small circles)
  node [shape=circle, label="", width=0.15, fixedsize=true];
  net_vcc; net_gnd; net_1; net_2;

  // Bipartite edges (component -- net)
  R1 -- net_1;
  R1 -- net_vcc;
  U1 -- net_1 [taillabel="3"];
  ...
}
```

**Per-component renderers**: each emits a node declaration with a multi-line label (refdes + value or model). Edges are emitted at the net-walker level, not per-component, by iterating each `LogicalNet`'s ports.

**Hierarchy.** Boards become DOT `subgraph cluster_<refdes>` blocks. The cluster gets a label with the board's name+revision.

**Connector handling.** Connectors are conductors (IS_CONDUCTOR=True) — they're already collapsed at the logical-net level. Emit nothing per connector.

**Net naming.** `vcc` / `gnd` / `net_<n>` — short, readable.

### 5.3 Mermaid (`framework/export/mermaid/`)

Browser-renderable flowchart syntax. Simpler than DOT; renders natively in GitHub, GitLab, and Notion.

**File shape:**

```
%%{init: {"theme": "neutral"}}%%
flowchart LR
    R1["R1<br/>330Ω"]
    D1["D1<br/>red LED"]
    U1["U1<br/>SN74HC04"]
    net_1(("net_1"))
    R1 --- net_1
    U1 --- net_1
    R1 --- net_vcc
    ...

    subgraph A2["A2: Controller Board"]
        ...
    end
```

**Per-component renderers**: same shape as DOT — each component is a node with a multi-line label using `<br/>` separator. Nets are double-circle nodes (`(( ))`). Edges use `---` (undirected).

**Hierarchy.** Boards become `subgraph` blocks with labels.

**Connectors.** Same as DOT — collapsed via IS_CONDUCTOR.

### 5.4 Yosys JSON (`framework/export/yosys/`)

Yosys synthesis tool's JSON format. Consumed by `netlistsvg` to render browser-friendly digital schematics.

**Best fit:** digital subset of designs (chips, cell concepts). Analog parts (resistors, LEDs) emit as opaque "blackbox" cells; rails become wire driven by a synthetic `$_const0_` / `$_const1_` cell.

**File shape:**

```json
{
  "creator": "circuitry 0.x",
  "modules": {
    "WaterAlarm": {
      "ports": {
        "low_probe":  {"direction": "input",  "bits": [2]},
        "high_probe": {"direction": "input",  "bits": [3]},
        "state":      {"direction": "output", "bits": [7]}
      },
      "cells": {
        "U1": {
          "type": "SN74HC04",
          "hide_name": 0,
          "parameters": {},
          "port_directions": {"a_1": "input", "y_1": "output", ...},
          "connections": {"a_1": [4], "y_1": [5], ...}
        },
        "U2": {"type": "CD4043", ...},
        "R1": {"type": "Resistor", ...},
        "D1": {"type": "LED", ...}
      },
      "netnames": {
        "vcc": {"hide_name": 0, "bits": [1], "attributes": {}},
        "net_1": {"hide_name": 0, "bits": [4], "attributes": {}},
        ...
      }
    }
  }
}
```

**Per-component renderers** produce dict fragments inserted into the `cells` map. The adapter assembles the full JSON via stdlib `json.dumps` with `indent=2, sort_keys=True` so output is deterministic.

**Net IDs.** Yosys nets are integers ("bits"). Each logical net gets a unique int starting at 2 (Yosys reserves 0 and 1 for constants).

**Hierarchy.** Each Board becomes its own module; the assembly is a top-level module instantiating each board as a cell.

### 5.5 BOM CSV (`framework/export/bom/`)

Bill of materials — tabular list of every refdes-bearing component, suitable for procurement and assembly. Universal CSV format.

**File shape:**

```csv
Refdes,Value,Footprint,Quantity,Manufacturer Part Number,Description
D1,red LED,LED_SMD:LED_0805,1,,Light-emitting diode
D2,green LED,LED_SMD:LED_0805,1,,Light-emitting diode
R1,330,Resistor_SMD:R_0603_1608Metric,1,,Resistor
U1,SN74HC04,Package_DIP:DIP-14_W7.62mm,1,SN74HC04N,Hex inverter
U2,CD4043,Package_DIP:DIP-16_W7.62mm,1,CD4043BE,Quad NOR R/S latch
```

**Per-component renderers** produce one CSV row each. The adapter sorts rows by refdes (R*, D*, U*, J*, A*) for human readability.

**Quantity column** — always `1` in this work package. A future enhancement could group identical parts (same value + footprint) into one row with a higher quantity, but for traceability "one row per refdes" is the cleaner default.

**Connectors and Rails.** Connectors do appear on the BOM (they're real parts). Rails and conductors do not. The adapter walks refdes-bearing components only.

**Hierarchy.** Boards appear as their own BOM line (`A1, Sensor Board Rev A, ...`); their internal components are also listed, with an extra column `Parent` referencing the board's refdes (`A1`, `A2`, blank for top-level).

## 6. Footprint metadata

KiCad netlist, BOM, and (optionally) Yosys benefit from footprint information. Each component class exposes a `FOOTPRINT` attribute in one of two forms depending on whether the part's geometry is fixed or parameterised:

**Fixed-geometry parts — `FOOTPRINT` is a `ClassVar[str | None]`:**

```python
class Resistor(FactorNode):
    REFDES_PREFIX = 'R'
    FOOTPRINT: ClassVar[str | None] = "Resistor_SMD:R_0603_1608Metric"

class SN74HC04(Chip):
    FOOTPRINT: ClassVar[str | None] = "Package_DIP:DIP-14_W7.62mm"

class USBCReceptacle(Connector):
    FOOTPRINT: ClassVar[str | None] = \
        "Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal"
```

**Parameterised families — `FOOTPRINT` is a `@property` that synthesises from instance state:**

```python
class Header2xNMale(Connector):
    @property
    def FOOTPRINT(self) -> str:
        return (
            f"Connector_PinHeader_{self.pitch_mm}mm:"
            f"PinHeader_2x{self.pin_count // 2}_P{self.pitch_mm}mm_Vertical"
        )

class JSTPHBoardSide(Connector):
    @property
    def FOOTPRINT(self) -> str:
        return f"Connector_JST:JST_PH_B{self.pin_count}B-PH-K_1x{self.pin_count:02d}_P2.00mm_Vertical"
```

Adapters read `comp.FOOTPRINT` uniformly — Python's attribute lookup transparently calls the property when present and reads the class attribute otherwise. The adapter doesn't need to care which kind it is.

**Default footprints** for the day-1 library:

| Class                                  | Form           | FOOTPRINT (or property expression)                                     |
|----------------------------------------|----------------|-------------------------------------------------------------------------|
| `Resistor`                             | ClassVar       | `"Resistor_SMD:R_0603_1608Metric"`                                      |
| `LED`                                  | ClassVar       | `"LED_SMD:LED_0805"`                                                    |
| `Rail`                                 | ClassVar       | `None` (Rail isn't a placeable part)                                    |
| `SN74HC04`                             | ClassVar       | `"Package_DIP:DIP-14_W7.62mm"`                                          |
| `CD4069`                               | ClassVar       | `"Package_DIP:DIP-14_W7.62mm"`                                          |
| `LM393`                                | ClassVar       | `"Package_DIP:DIP-8_W7.62mm"`                                           |
| `CD4043`                               | ClassVar       | `"Package_DIP:DIP-16_W7.62mm"`                                          |
| `ULN2003A`                             | ClassVar       | `"Package_DIP:DIP-16_W7.62mm"`                                          |
| `Header1xNMale` / `Header1xNFemale`    | @property      | `PinHeader_1x{n}_P{pitch}mm_Vertical` synthesis                         |
| `Header2xNMale` / `Header2xNFemale`    | @property      | `PinHeader_2x{n/2}_P{pitch}mm_Vertical` synthesis                       |
| `IDC2xNMale` / `IDC2xNSocket`          | @property      | `IDC-Header_2x{n/2}_P{pitch}mm_Vertical` synthesis                      |
| `USBAReceptacle` / `USBAPlug`          | ClassVar       | `"Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal"` / cable-side    |
| `USBBReceptacle` / `USBBPlug`          | ClassVar       | `"Connector_USB:USB_B_Wuerth_61400826021_Horizontal"` / cable-side      |
| `USBMicroBReceptacle` / Plug           | ClassVar       | `"Connector_USB:USB_Micro-B_GCT_USB3076-30-A_Horizontal"` / cable-side  |
| `USBCReceptacle` / `USBCPlug`          | ClassVar       | `"Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal"` / cable-side |
| `RJ45Jack` / `RJ45Plug`                | ClassVar       | `"Connector_RJ:RJ45_Wuerth_7499010121A_Horizontal"` / cable-side        |
| `HDMITypeAReceptacle` / Plug           | ClassVar       | `"Connector_Video:HDMI_A_Amphenol_10029449-001RLF_Horizontal"`          |
| `Audio3p5mmTRSJack` / Plug             | ClassVar       | `"Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles"`|
| `Audio3p5mmTRRSJack` / Plug            | ClassVar       | analogous TRRS footprint                                                |
| `BarrelJack5p5x2p1` / Plug             | ClassVar       | `"Connector_BarrelJack:BarrelJack_Horizontal"` / cable-side             |
| `BarrelJack5p5x2p5` / Plug             | ClassVar       | analogous 2.5mm variant                                                 |
| `JSTPHBoardSide` / `JSTPHCableHousing` | @property      | `JST_PH_B{n}B-PH-K_1x{n:02d}_P2.00mm_Vertical` synthesis                |
| `JSTXHBoardSide` / `JSTXHCableHousing` | @property      | `JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical` synthesis                |
| `JSTSHBoardSide` / `JSTSHCableHousing` | @property      | `JST_SH_BM{n}B-SRSS-TB_1x{n:02d}-1MP_P1.00mm_Horizontal` synthesis      |
| `JSTGHBoardSide` / `JSTGHCableHousing` | @property      | `JST_GH_BM{n}B-GHS-TBT_1x{n:02d}-1MP_P1.25mm_Vertical` synthesis        |
| `ScrewTerminalBlock`                   | @property      | `TerminalBlock:TerminalBlock_Phoenix_MPT-{pitch}mm_1x{n}_P{pitch}mm_Horizontal` synthesis |
| `MicroSDCardSlot`                      | ClassVar       | `"Connector_Card:microSD_HC_Hirose_DM3D-SF"`                            |
| `MicroSDCard`                          | ClassVar       | `None` (the card isn't a placeable part on the parent board)            |
| `SDCardSlot`                           | ClassVar       | `"Connector_Card:SD_TE_2041021"`                                        |
| `SDCard`                               | ClassVar       | `None` (same reasoning)                                                 |

Footprint strings follow KiCad library naming. The implementer should cross-check each against the KiCad 7+ default library before committing; the table above is the *intent*. Where a stock KiCad footprint doesn't exist for an exact match (some JST sizes), fall back to the closest generic name and document the substitution in the `kicad/` module.

**Per-instance overrides remain deferred** — the constructor-`footprint=` argument is out of scope for this work package. Users who need a non-default footprint subclass the component (a one-line subclass with a different `FOOTPRINT` ClassVar suffices) or wait for the override extension.

## 6.5 Pin numbers on passive terminals

KiCad and Yosys netlists require a pin number per node reference. Chips and connectors already carry pin numbers via `Pin.id.number` (per the pin-id spec); passives don't because their terminals are raw `Port`s, not `Pin` wrappers. The pin-id spec's deferral — *"defer until an exporter actually needs it"* — is lifted by this work package.

**Add `PIN_NUMBERS: ClassVar[dict[str, int]]` to each passive component class:**

```python
class Resistor(FactorNode):
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'t1': 1, 't2': 2}

class LED(FactorNode):
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'anode': 1, 'cathode': 2}

class Rail(FactorNode):
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'out': 1}
```

These mirror the SMD silkscreen convention (anode-side / cathode-side, terminal 1 / terminal 2) — physical fact about each part, not software fabrication.

**The framework provides a uniform helper** in `framework/export/base.py` so adapters don't have to special-case passives vs. chips:

```python
def pin_number_of(component: FactorNode, port_name: str) -> int | None:
    """The datasheet pin number for `port_name` on `component`, regardless
    of whether the component models its terminals as `Pin` instances
    (chips, connectors) or as raw `Port`s with `PIN_NUMBERS` metadata
    (passives). Returns None if the component declares no number for the
    requested port — adapters decide whether that's an error or a
    silently-omitted field."""
    for pin in getattr(component, 'pins', ()):
        if pin.id.name == port_name:
            return pin.id.number
    return getattr(type(component), 'PIN_NUMBERS', {}).get(port_name)
```

Adapters call `pin_number_of(comp, 'anode')` etc. and emit the result. For KiCad and Yosys (which require numbers), `None` is an export-time error mentioning the offending component class and port. For SPICE, DOT, Mermaid, BOM (which don't reference pin numbers in their output), the helper is unused.

## 6.6 Adapter-supplied net namers

Net naming conventions differ across formats: SPICE uses `0` for ground, KiCad uses `GND`, Yosys uses integer bit IDs, DOT/Mermaid use readable strings. The current `ExporterContext._assign_net_names` hardcodes SPICE's conventions; this work package refactors that into a per-adapter strategy.

**The contract.** Each adapter declares a function with the signature:

```python
def name_<format>_net(net: LogicalNet, ctx: ExporterContext) -> str:
    """Return the format-specific name for a logical net."""
```

and registers it alongside its renderers:

```python
# in framework/export/<format>/__init__.py
from framework.export.base import register_net_namer

def name_kicad_net(net: LogicalNet, ctx: ExporterContext) -> str:
    if any(isinstance(o, Rail) and o.level is False for o, _ in net.ports):
        return 'GND'
    if any(isinstance(o, Rail) and o.level is True for o, _ in net.ports):
        return 'vcc'
    # Synthesise: Net-(<lowest_qualified_refdes>-Pad<lowest_pin_number>)
    real_ports = [(o, p) for o, p in net.ports if not o.IS_CONDUCTOR]
    o, p = sorted(real_ports, key=lambda op: (ctx.refdes_of(op[0]),
                                              pin_number_of(op[0], p.name) or 0))[0]
    return f"Net-({ctx.refdes_of(o)}-Pad{pin_number_of(o, p.name)})"

register_net_namer('kicad', name_kicad_net)
```

**The framework-level refactor.** `ExporterContext.__init__` looks up the namer for `self._format` via `framework.export.base.lookup_net_namer(format)` and stores it. `ctx.net_name(port)` calls it per net. The existing SPICE-hardcoded logic moves out of `base.py` and into `spice/__init__.py` as `name_spice_net()`, registered the same way as new adapters.

**Yosys's integer bit IDs.** Yosys nets are integers (e.g. `"bits": [2]`). The namer returns the integer as a string (`"2"`, `"3"`, …) starting at `"2"` (Yosys reserves `0` and `1` for constants). The Yosys adapter converts to int at JSON-emission time. Keeping the namer's return type uniformly `str` keeps the framework simple.

**Determinism.** Namers must produce identical output for identical inputs, including order-independence across `LogicalNet.ports`. The framework's `compute_logical_nets` already returns ports in deterministic order; namers must not introduce non-determinism (no timestamps, no RNG, no dict iteration on unsorted keys).

## 6.7 Header determinism

The SPICE adapter's `include_header_comment=True` default currently embeds `datetime.now().isoformat()`, which breaks byte-determinism and therefore golden-file tests. Every adapter in this work package, *and* the SPICE adapter as a fix-in-passing, observes this rule:

- `include_header_comment` defaults to `False`. Golden-file tests run with the default and get byte-stable output.
- When `True`, the header carries deterministic content only — a `circuitry` version string, the design's name, and (optionally) a content-hash fingerprint. No wall-clock timestamps, no environment-dependent fields.
- The KiCad `(date "...")` field is omitted from the netlist by default. When the user explicitly sets `KiCadExportConfig.include_date=True`, the date is set from the design's `revision` field (which is stable) or from `CIRCUITRY_EXPORT_DATE` env var (test-controllable).

This is the same shape SPICE should have had from day one; the work package quietly fixes it across all adapters.

## 7. CLI extensions

The existing `circuitry export` command gains the new format names automatically (it reads from `list_formats()`). Test:

```bash
$ circuitry export --list-formats
bom
dot
kicad
mermaid
spice
yosys

$ circuitry export design.circuitry --format kicad --output design.net
$ circuitry export design.circuitry --format dot | dot -Tsvg > design.svg
$ circuitry export design.circuitry --format mermaid > design.mmd
$ circuitry export design.circuitry --format yosys | netlistsvg > design.svg
$ circuitry export design.circuitry --format bom --output bom.csv
```

No new CLI arguments required — format detection is purely string-based against the registry.

## 8. File-by-file change list

**New files** (per adapter; replicate the pattern for each of the five formats):

- `src/framework/export/<format>/__init__.py` — entry point and top-level emitter.
- `src/framework/export/<format>/renderers.py` — `@register_renderer(...)` for every component class (one direct entry per chip/passive plus one shared at `Connector` for connectors via MRO).
- `src/framework/export/<format>/config.py` — `<Format>ExportConfig(ExportConfig)`.

**Modified files:**

- `src/components/passives/resistor.py`, `led.py`, `rail.py` — add `FOOTPRINT` class attribute (Rail's is `None`) **and `PIN_NUMBERS` class attribute** per §6.5 (Resistor: `{'t1':1, 't2':2}`; LED: `{'anode':1, 'cathode':2}`; Rail: `{'out':1}`).
- `src/components/chips/*.py` — add `FOOTPRINT` class attribute per chip.
- `src/components/connectors/*.py` — add `FOOTPRINT` per concrete connector class. Fixed-geometry connectors use the `ClassVar` form; parameterised families (`Header*`, `IDC*`, `JST*`, `ScrewTerminalBlock`) use the `@property` form per §6.
- `src/framework/factor.py` — declare `FOOTPRINT: ClassVar[str | None] = None` and `PIN_NUMBERS: ClassVar[dict[str, int]] = {}` on `FactorNode` so subclasses can override and the attribute lookup is always safe.
- `src/framework/export/base.py` — **refactor `ExporterContext._assign_net_names`** out into per-adapter `name_<format>_net` functions per §6.6. Add `register_net_namer(format: str, namer: Callable)` and `lookup_net_namer(format: str) -> Callable`. Add the `pin_number_of(component, port_name)` helper per §6.5. `ExporterContext.__init__` now calls `lookup_net_namer(format)` rather than hardcoding SPICE's conventions.
- `src/framework/export/spice/__init__.py` — define `name_spice_net()` carrying the existing SPICE-specific logic (Rail(False) → `0`, Rail(True) → `vcc`, others → `net_<n>`) and call `register_net_namer('spice', name_spice_net)`. This is a refactor with no behavioural change for SPICE consumers.
- `src/framework/export/spice/__init__.py`, again — change `include_header_comment` default to `False` per §6.7; when `True`, emit deterministic content only (no `datetime.now()`).

**New test files** (per adapter — replicate the structure):

- `tests/framework/export/<format>/test_<format>_components.py` — per-component renderer tests.
- `tests/framework/export/<format>/test_<format>_topology.py` — topology cross-reference test (per the pattern landed for SPICE).
- `tests/framework/export/<format>/test_<format>_golden.py` — golden-file test.
- `tests/framework/export/<format>/test_<format>_external_tool.py` — optional external-tool round-trip; skips cleanly if the tool isn't on PATH.
- `tests/golden/<format>/water_alarm.<ext>`, `tests/golden/<format>/water_alarm_assembly.<ext>` — checked-in golden outputs.

**Unmodified files** — the framework layer (`base.py`, `nets.py`, `walk.py`, top-level `__init__.py`) gains nothing. New adapters are pure additions.

## 9. Verification — the robust strand

Each adapter ships with five mandatory test categories. The bar is the same one that's now in force for SPICE: **per-component tests assert real content; topology cross-reference catches scrambled connectivity; golden files catch silent formatting drift; no test may be softened to accommodate a half-implemented renderer**.

### 9.1 Per-component renderer tests

For each component class touched by the adapter, write a focused test asserting the produced fragment matches the expected output. Test fixtures use minimal designs (one component + a Rail or Ground wired) so the assertion is exact.

Example shape (KiCad):

```python
def test_kicad_resistor_renders_as_comp_record() -> None:
    design = ... # one Resistor wired to vcc / gnd
    deck = export_to_string(design, 'kicad')
    assert '(comp (ref "R1")' in deck
    assert '(value "330")' in deck
    assert '(footprint "Resistor_SMD:R_0603_1608Metric")' in deck
```

Target count per adapter: at least 10 tests covering passives, chips (a sample of two), connectors, Boards, Assemblies, and edge cases (chip pin order, refdes-less Rail, mated connectors collapsing).

### 9.2 Topology cross-reference

Same pattern as SPICE's `test_spice_topology.py`. Build the model, compute the expected `{(refdes, port_name): net_name}` mapping by walking ports and asking `ExporterContext.net_name`, then parse the deck and reconstruct the same mapping from the exported text. Assert equality.

For each format, the parser is format-specific and short (regex-based, ~40-60 lines). Catches the load-bearing class of bug: a renderer that emits the right *number* of nets but in the wrong *order* (e.g., a chip's pins scrambled) — which a per-component test that only counts tokens will miss.

KiCad, BOM, and Yosys all carry per-port connectivity information and benefit directly from this test. DOT and Mermaid are visualisation-only — for those, the topology test asserts that every original (refdes, port, net) triple appears *somewhere* in the rendered output (since DOT/Mermaid edges aren't ordered), which is a weaker but still useful check.

**The pin-order regression check.** As proven for SPICE: temporarily break the chip pin-sort key, confirm the topology test fails clearly. Document the result in the test PR.

### 9.3 Golden files

For each adapter, golden files at `tests/golden/<format>/water_alarm.<ext>` and `tests/golden/<format>/water_alarm_assembly.<ext>`. The test exports each application and asserts byte-equality. Updating a golden requires the `UPDATE_GOLDEN=1` environment variable, ensuring updates show up as a deliberate file change in PR diffs.

`tests/golden/<format>/README.md` documents the convention per adapter.

### 9.4 Format-syntactic validation

For each format, use a real parser to validate the output is syntactically correct beyond regex matching:

| Format         | Parser                                          |
|----------------|-------------------------------------------------|
| KiCad netlist  | A minimal S-expression parser (~30 lines) or `sexpdata` if it's already a dep |
| Graphviz DOT   | `dot -Txdot` (round-trips DOT through Graphviz's parser; skip if not installed) |
| Mermaid        | `mmdc -i <file> -o /dev/null` (skip if not installed) |
| Yosys JSON     | `json.loads` (always available); also validate against the Yosys JSON schema if a Python lib exists |
| BOM CSV        | `csv.DictReader` (always available); assert expected column headers |

For formats where a real parser isn't available in stdlib, the syntactic test is the optional external-tool round-trip — and it skips cleanly when the tool isn't installed.

### 9.5 Optional external-tool round-trip

One test per adapter that runs the target tool against the exported file when the tool is on PATH; skips with `pytest.mark.skipif(not shutil.which('<tool>'))` otherwise:

| Format         | Tool             | Test                                                           |
|----------------|------------------|----------------------------------------------------------------|
| KiCad netlist  | `kicad-cli`      | Future: `kicad-cli sch import-netlist` — currently no CLI gate, skip placeholder. |
| Graphviz DOT   | `dot`            | `dot -Tsvg -o /dev/null <file>` exit code 0.                  |
| Mermaid        | `mmdc`           | `mmdc -i <file> -o /tmp/out.svg` exit code 0.                 |
| Yosys JSON     | `netlistsvg`     | `netlistsvg <file> -o /tmp/out.svg` exit code 0.              |
| BOM CSV        | (none needed)    | Just parse with `csv.DictReader` and check shape.             |

### 9.6 The no-softening rule

Every adapter's test suite must include the rule (in the test module docstring): *"If a test fails because a renderer is missing or incorrect, the fix is to add or correct the renderer — not to lower the assertion bar. No `pytest.skip`, `xfail`, 'current behaviour', 'TODO: tighten', or relaxed regex unless there's a specific in-spec deferral with a tracked follow-on."*

The verification round at the end of this work package explicitly grep-checks for those phrases in `tests/framework/export/*/` and rejects any new occurrences relative to the baseline.

## 10. Test plan summary

Per adapter (×5 formats):

- ~10 per-component renderer tests.
- 2 topology cross-reference tests (one per application).
- 2 golden-file tests (one per application).
- 1 format-syntactic validation test.
- 1 optional external-tool test (skipped cleanly when tool absent).

Total per adapter: ~16 tests.
Total new tests across all five adapters: **~80**.

Baseline at start of work package: 314 (post-SPICE) + 4 (from topology / golden follow-on after SPICE) = 318. Target after this work package: **at least 398**.

## 11. Acceptance criteria

The work package is done when:

1. `python -m pytest` passes; test count up by at least 80 over the pre-work baseline.
2. `list_formats()` returns at least `['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys']`.
3. Every component class in the component registry has a renderer reachable via MRO for **every** format (i.e., `lookup_renderer(cls, fmt)` succeeds for every (class, fmt) pair). The per-format "smoke" test from spec §9.4 of the export-framework spec — extended to all formats — is the load-bearing check.
4. `export(WaterAlarm(), fmt, path)` and `export(WaterAlarmAssembly(), fmt, path)` produce well-formed output for every format `fmt`.
5. Golden files exist at `tests/golden/<format>/water_alarm.<ext>` and `tests/golden/<format>/water_alarm_assembly.<ext>` for each of the five formats and match byte-for-byte on a clean run.
6. Topology cross-reference passes for every format that carries per-port connectivity (KiCad, Yosys, BOM — strict; DOT, Mermaid — weaker "every triple appears" form).
7. For every format, a temporarily-broken pin-order in any chip's `_render_chip_*` produces a clear topology-test failure naming the affected pins. Verified during implementation; restored before merge.
8. No `pytest.skip`, `xfail`, "current behaviour", "TODO: tighten", or relaxed-regex justifications introduced relative to the pre-work baseline. The no-softening rule from §9.6 is grep-verified.
9. Optional external-tool tests (`dot`, `mmdc`, `netlistsvg`) pass on a machine with those tools installed; skip cleanly otherwise. Document the manual verification result in the PR description if external tools were used.
10. `FOOTPRINT` is set on every refdes-bearing component class — `ClassVar[str | None]` for fixed-geometry parts, `@property` returning `str` for parameterised families (per §6). `None` is preserved for `Rail` and `FactorNode`.
11. `PIN_NUMBERS: ClassVar[dict[str, int]]` is set on `Resistor`, `LED`, `Rail` per §6.5. The `pin_number_of(component, port_name)` helper in `framework/export/base.py` returns the correct number for chips (via `Pin.id.number`), connectors (same path), and passives (via `PIN_NUMBERS`).
12. Net naming is per-adapter via `register_net_namer(...)` / `lookup_net_namer(...)` per §6.6. `ExporterContext` is no longer SPICE-coupled. The SPICE adapter's net namer is registered alongside the new adapters' namers; behavioural output for SPICE is unchanged.
13. Header determinism per §6.7: `include_header_comment` defaults to `False` across all adapters; SPICE-as-it-stands is fixed in passing. Golden-file tests produce byte-stable output by default.
14. `__slots__` discipline preserved; no setters introduced; physical-fidelity discipline intact (no software-meta attributes; only data that corresponds to real part properties).
15. The CLI accepts every new format name without modification; `circuitry export --list-formats` lists them newline-separated, alphabetised.
16. KiCad output is flat (not nested `(sheet)` blocks) per §5.1. Cross-board refdes collisions are resolved by prefixing with each ancestor board's refdes (`A1_U1`, `A2_U1`). Per-component `sheetpath` and `tstamps` carry the hierarchy; `tstamps` are deterministic (SHA-1 of `name|revision|refdes`, 8 hex chars).

## 12. Out of scope (for follow-on work packages)

- **EDIF 2 0 0 / IEEE 1647 adapter.** Useful for Cadence / Mentor / Altium interop; not currently ubiquitous enough to land in this work package. Add when a real consumer needs it.
- **Verilog / VHDL gate-level netlist.** RTL-oriented; doesn't map cleanly from physical-circuit modelling.
- **Altium-native, OrCAD, Eagle, DXF formats.** Proprietary or marginal in OSS workflows.
- **PCB layout artefacts.** Gerber, drill files, pick-and-place CSV — all require placement information that the model doesn't yet carry.
- **Per-instance footprint overrides.** Class-level default only in this work package; per-instance override deferred.
- **Quantity-aware BOM rollup.** "10× R1-R10 same part" deferred — one row per refdes for traceability.
- **Power-flag / hierarchical-label emission in KiCad.** Day-1 emits flat nets; KiCad will still import correctly but hierarchical labels for cross-sheet signals are a follow-on.
- **Yosys JSON deep digital semantics.** Things like edge-triggered flip-flops, async resets, parameterised cells — needs RTL-level information the current model doesn't carry.
- **Schematic placement / auto-layout for DOT and Mermaid.** Current output relies on the renderer tool's default layout engine; tuning ranksep / nodesep for circuit-shaped diagrams is a polish pass.
- **Round-tripping (importing back from each format).** Each adapter is one-way: design → format. Reading a KiCad netlist and reconstructing a `.circuitry` design is a separate, significantly harder problem.
