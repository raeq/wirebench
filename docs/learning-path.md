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

The *first catches* column names rules from [`the-rules.md`](the-rules.md) that this demo is the first place to surface — i.e. work the demos top-to-bottom and you'll see the framework refuse each rule in a real circuit by the time you reach the demo it's listed against.

| #  | Demo                                                                                                             | What it teaches                                                               | First catches              |
|----|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|----------------------------|
| 1  | [`hello_led/`](https://github.com/raeq/wirebench/tree/main/demos/hello_led/)                                     | The minimal viable circuit — one LED, one resistor, two rails. Reading point. | [Rules 1, 2](the-rules.md) |
| 2  | [`5v_rail_power/`](https://github.com/raeq/wirebench/tree/main/demos/5v_rail_power/)                             | First regulator — LM7805 + Cell + bypass caps. Linear-supply basics.          | —                          |
| 3  | [`penfold_light_switch/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_light_switch/)               | First sensor circuit. LDR + comparator + transistor switch. Penfold BP107 P3. | [Rules 3, 4](the-rules.md) |
| 4  | [`water_alarm/`](https://github.com/raeq/wirebench/tree/main/demos/water_alarm/)                                 | Composing chips, wiring rails, latching logic. Four chips, two LEDs.          | [Rule 9](the-rules.md)     |
| 5  | [`penfold_reaction_game/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_reaction_game/)             | Sequential digital — counter ring + button-stops-clock topology. Penfold P22. | —                          |
| 6  | [`dice/`](https://github.com/raeq/wirebench/tree/main/demos/dice/)                                               | Classic 555 + 4017 + diode-OR matrix. Recognisable hobbyist staple.           | —                          |
| 7  | [`digital_thermometer/`](https://github.com/raeq/wirebench/tree/main/demos/digital_thermometer/)                 | First MCU project. ATmega328P + DHT11 + 7-seg display. Firmware-as-cell.      | —                          |
| 8  | [`penfold_one_second_timer/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_one_second_timer/)       | Op-amp relaxation oscillator with hysteresis. Penfold BP107 P8.               | —                          |
| 9  | [`penfold_metronome/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_metronome/)                     | NE555 astable + speaker — the other classical astable. Penfold BP107 P9.      | —                          |
| 10 | [`penfold_warbling_doorbuzzer/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_warbling_doorbuzzer/) | Oscillator composition — slow gates fast. Penfold BP107 P16.                  | —                          |
| 11 | [`doorbell_protector/`](https://github.com/raeq/wirebench/tree/main/demos/doorbell_protector/)                   | Two-555 monostable with transistor switching and a relay.                     | —                          |
| 12 | [`fan_cooling/`](https://github.com/raeq/wirebench/tree/main/demos/fan_cooling/)                                 | First `Board` demo. TMP302 + MOSFET-switched fan. Connectors that mate.       | [Rule 7](the-rules.md)     |
| 13 | [`backup_power/`](https://github.com/raeq/wirebench/tree/main/demos/backup_power/)                               | TI Designs TIDA-03031. Three-stage power architecture (eFuse + boost + buck). | —                          |
| 14 | [`water_alarm_split/`](https://github.com/raeq/wirebench/tree/main/demos/water_alarm_split/)                     | Same circuit as #3 but split across two boards via `mate()`. HAT pattern.     | [Rule 6](the-rules.md)     |
| 15 | [`bldc_motor/`](https://github.com/raeq/wirebench/tree/main/demos/bldc_motor/)                                   | ATmega328P + DRV8313 + Hall sensors. Three-phase commutation.                 | —                          |
| 16 | [`isolated_rs232/`](https://github.com/raeq/wirebench/tree/main/demos/isolated_rs232/)                           | TIDA-01230. Cross-domain isolation — first demo to exercise `GroundDomain`.   | [Rule 5](the-rules.md)     |
| 17 | [`li_ion_fuel_gauge/`](https://github.com/raeq/wirebench/tree/main/demos/li_ion_fuel_gauge/)                     | TIDA-00594. BQ27546-G1 fuel gauge with sense resistor + thermistor.           | —                          |
| 18 | [`penfold_fuzz_unit/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_fuzz_unit/)                     | Audio domain — op-amp + clipping diodes. Guitar fuzz pedal. Penfold P30.      | —                          |
| 19 | [`penfold_crystal_set/`](https://github.com/raeq/wirebench/tree/main/demos/penfold_crystal_set/)                 | Passive-only RF — no Rail, no battery. Boundary case. Penfold BP107 P27.      | —                          |

Rules 8, 10, 11, and 12 are framework-internal refusals — they fire during refactors and new-design construction rather than in any specific demo's near-miss snippet. The full table of all twelve rules is on [`the-rules.md`](the-rules.md).

Cross-referencing the other way: [`the-rules.md`](the-rules.md) lists, for each rule, the demo where you'll first see it caught — so you can read either page first and find your way back to the other.

## What each demo gives you

Every demo folder follows the same broad shape — one or more Python source files plus a `docs/` subfolder of generated artefacts. The Python file usually matches the folder name (`hello_led.py`, `dice.py`), occasionally not (`5v_rail_power/` uses `five_volt_rail_power.py`). Most demos carry a `README.md` with the *what this design is protected from* sidebar; a small number are source-only.

```text
demos/<name>/
    *.py                            # the source — read this first
    README.md                       # what this design is protected from + recipe (when present)
    docs/
        <Top>.bom.csv               # BOM ready to paste into a parts cart
        <Top>.net                   # KiCad netlist for PCB layout
        <Top>.kicad_sch             # KiCad schematic for Eeschema review
        <Top>.cir                   # SPICE deck for simulation
        <Top>.mmd                   # Mermaid render for documentation
        <Top>.dot                   # Graphviz DOT
        <Top>.yosys.json            # Yosys JSON for netlistsvg
        <Top>.svg                   # rendered schematic — open this in a browser
        <Top>.breadboard.svg        # half-size breadboard layout (single-Board demos)
        <Top>.md                    # recipe-style breadboard assembly guide
        <Top>.net-report.md         # every logical net + drivers + readers + domain
        <Top>.domain-report.md      # GroundDomain memberships and isolation
        <Top>.interface-report.md   # public Board connector pins
```

`<Top>` is the design's top-level class name (e.g. `HelloLED`, `Dice`). A live example of the full set sits in the [hello_led/docs/ folder on GitHub](https://github.com/raeq/wirebench/tree/main/demos/hello_led/docs) — that's the authoritative live index, regenerated whenever an exporter changes, so the listing above can't drift from what actually ships.

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
- Contribute. The source is at [github.com/raeq/wirebench](https://github.com/raeq/wirebench); the design philosophy is the [`design-principles.md`](design-principles.md) page on this site.
