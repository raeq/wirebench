# Learning path

The demos under `demos/` are roughly ordered by complexity. Each lives in its own folder with `<name>.py` (the source) and a `docs/` subfolder containing all six format exports plus a rendered SVG schematic. Read the source, look at the schematic, see what comes out — in any order — but if you're new to the framework, work through them top to bottom.

Each demo is **a buildable circuit**: the BOM lists real parts you can order, the KiCad netlist imports into Pcbnew, and the wire-list in the Python source maps one-for-one to the jumpers on your breadboard.

## Prerequisites

The framework expects you to be comfortable with:

- **Reading and writing Python** at the level of "I can write a class with a few methods."
- **Programming an Arduino** (or equivalent) — enough that microcontroller pin names like `PB5` and references to "the I²C bus" don't bounce you. The `digital_thermometer/` demo onward leans on this.
- **Breadboard basics** — what a power rail is, what GND is, what a current-limit resistor does. The framework won't teach you these from scratch, but it will hand you back the right intuitions as the refusal messages.

If you've never lit an LED with a battery, start with [the project's Hello World example](https://github.com/raeq/wirebench#hello-world) and a real breadboard. Build it. Then come back here.

## The demos in order

| # | Demo                          | What it teaches                                                                       |
|---|-------------------------------|---------------------------------------------------------------------------------------|
| 1 | [`water_alarm/`](../demos/water_alarm/)                  | Composing chips, wiring rails, latching logic. Four chips, two LEDs.        |
| 2 | [`dice/`](../demos/dice/)                                | Classic 555 + 4017 + diode-OR matrix. Recognisable hobbyist staple.         |
| 3 | [`digital_thermometer/`](../demos/digital_thermometer/)  | First MCU project. ATmega328P + DHT11 + 7-seg display. Firmware-as-cell.    |
| 4 | [`doorbell_protector/`](../demos/doorbell_protector/)    | Two-555 monostable with transistor switching and a relay.                   |
| 5 | [`fan_cooling/`](../demos/fan_cooling/)                  | First `Board` demo. TMP302 + MOSFET-switched fan. Connectors that mate.     |
| 6 | [`backup_power/`](../demos/backup_power/)                | TI Designs TIDA-03031. Three-stage power architecture (eFuse + boost + buck). |
| 7 | [`water_alarm_split/`](../demos/water_alarm_split/)      | Same circuit as #1 but split across two boards via `mate()`. HAT pattern.   |
| 8 | [`bldc_motor/`](../demos/bldc_motor/)                    | ATmega328P + DRV8313 + Hall sensors. Three-phase commutation.               |
| 9 | [`isolated_rs232/`](../demos/isolated_rs232/)            | TIDA-01230. Cross-domain isolation — first demo to exercise `GroundDomain`. |
|10 | [`li_ion_fuel_gauge/`](../demos/li_ion_fuel_gauge/)      | TIDA-00594. BQ27546-G1 fuel gauge with sense resistor + thermistor.         |

## What each demo gives you

Every demo folder has the same shape:

```
demos/<name>/
    <name>.py                  # the source — read this first
    docs/
        <Top>.bom.csv          # BOM ready to paste into a parts cart
        <Top>.net              # KiCad netlist for PCB layout
        <Top>.cir              # SPICE deck for simulation
        <Top>.mmd              # Mermaid render for documentation
        <Top>.dot              # Graphviz DOT
        <Top>.yosys.json       # Yosys JSON for netlistsvg
        <Top>.svg              # rendered schematic — open this in a browser
```

For composite assemblies (the `water_alarm_split`, `fan_cooling`, `bldc_motor`, `isolated_rs232`, and `li_ion_fuel_gauge` demos), there's one set of exports per board *plus* one set for the parent assembly — so you can see how the same model exports differently depending on whether you're producing a per-board netlist or an assembly-level overview.

## How to use this path

For each demo:

1. **Open the rendered schematic first.** `docs/<Name>.svg` — see what the circuit looks like before reading any code.
2. **Read the source.** Top-to-bottom; every demo opens with a docstring naming the BOM, the wiring, and what's modelled vs. what's deliberately not.
3. **Run it.** `python demos/<name>/<name>.py` produces a per-input trace through the circuit.
4. **Inspect the exports.** Open `docs/<Name>.bom.csv` in a spreadsheet, `docs/<Name>.cir` in a text editor, `docs/<Name>.net` if you want to try a KiCad import. Convince yourself the framework's output and the schematic agree.
5. **Build it.** Order the parts from the BOM, wire them per the source, and confirm the breadboard behaves as the simulator suggested.

That last step is the point. If the framework's discipline is doing its job, no surprises wait at the bench.

## What this path doesn't cover

- **PCB layout.** Every demo exports to KiCad netlist; turning that into a manufactured board is KiCad's job, and KiCad has its own learning curve. The netlist gives you a starting point; the layout pass needs separate study.
- **Vendor SPICE models for accurate simulation.** The shipped models are structural placeholders that simulate the topology. For quantitative simulation (real propagation delays, real V_F values), replace `framework/export/spice/spice-models.lib` with vendor-supplied models for the specific parts.
- **Firmware development for the MCU demos.** The `digital_thermometer/`, `bldc_motor/`, and similar demos model firmware as a private cell inside the MCU subclass. The cell is whatever logic you decide; the framework doesn't simulate Arduino sketches or compile C++.

For all three: the framework gets you to the start of these tracks. The tracks themselves are separate craft.

## After this path

Once you can build a circuit from one of these demos on a breadboard and confirm the framework's output matches reality:

- Make modifications. Change the timing capacitor in the dice demo. Swap the comparator hysteresis values in the water alarm. Add a third LED to the doorbell protector. The framework will tell you immediately if any change breaks the topology; if it doesn't, the modification is buildable.
- Design your own circuit using the parts already in `src/components/`. The component catalogue is in [`docs/component-library-data.md`](component-library-data.md).
- Add a new component to the library if the part you want doesn't exist yet. The pattern is mechanical — look at any existing class in `src/components/` and follow it.
- Contribute. The design philosophy lives in [`CLAUDE.md`](https://github.com/raeq/wirebench/blob/main/CLAUDE.md); the implementation specs that produced each major framework feature live in [`docs/`](./).
