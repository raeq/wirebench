# circuitbench

> *Describe real electronic circuits in Python. The framework refuses to compile designs that wouldn't physically work — so when your tests are green, the breadboard build matches.*

If you've programmed an Arduino but felt like wiring the surrounding circuit is a black art — every project a hunt for the magic combination of pull-ups, current-limiting resistors, decoupling caps, and "did I just wire the LED backwards?" — circuitbench is a Python framework where every line of code maps to a physical operation.

You write Python that says *"a 330 Ω resistor in series with a red LED between VCC and GND."* You get out a BOM you can paste into a parts cart, a KiCad netlist you can import for PCB layout, a SPICE deck for simulation, a rendered schematic for documentation, and the confidence that every wire in the code is a wire you'll need on the breadboard — no more, no less.

## Hello, world

```python
from circuitry import Resistor, LED, Rail, Circuit, wire, export

class HelloLED(Circuit):
    def __init__(self) -> None:
        self.vcc = Rail(True)                       # 5 V supply rail
        self.gnd = Rail(False)                      # 0 V ground
        self.r1  = Resistor(330, refdes_number=1)   # R1: 330 Ω current limiter
        self.d1  = LED('red', refdes_number=1)      # D1: red LED

        wire(self.vcc.out, self.r1.t1)              # VCC → R1 pin 1
        wire(self.r1.t2,   self.d1.anode)           #         R1 pin 2 → LED anode
        wire(self.d1.cathode, self.gnd.out)         #                    LED cathode → GND

        super().__init__()

design = HelloLED()
export(design, 'bom',     'hello.bom.csv')
export(design, 'kicad',   'hello.net')
export(design, 'spice',   'hello.cir')
export(design, 'mermaid', 'hello.mmd')
```

This is a buildable circuit. The wire-list in the Python file maps one-for-one to the jumpers on your breadboard. Drop the BOM into Mouser or Digikey, order two parts, and you have everything you need.

Components are stored as `self.<name>` attributes so the framework can auto-collect them — `super().__init__()` walks `self.__dict__` and picks up every `Resistor`, `LED`, `Chip`, and `Rail` you've placed. The two-stage pattern (declare parts → wire them → finalise with `super().__init__()`) reads like a bench-style buildout: take parts off the shelf, wire them together, close the assembly.

**What comes out:**

| Format        | Extension      | What it's for                                                                |
|---------------|----------------|------------------------------------------------------------------------------|
| BOM CSV       | `.bom.csv`     | Paste into a parts cart at Mouser / Digikey / Tayda                          |
| KiCad netlist | `.net`         | Import into KiCad's Pcbnew to lay out a PCB                                  |
| SPICE deck    | `.cir`         | Simulate in ngspice or LTspice before building                               |
| Mermaid       | `.mmd`         | Embed in a README to document what you built                                 |
| Graphviz DOT  | `.dot`         | Render to SVG / PNG with `dot -Tsvg`                                         |
| Yosys JSON    | `.yosys.json`  | Render to a browser-friendly schematic via [netlistsvg](https://github.com/nturley/netlistsvg) |
| Assembly Guide| `.md`          | Read at the bench — recipe-style breadboard build instructions               |

Every demo in `demos/` ships with all seven exports pre-generated in its `docs/` subfolder — open any `*.svg` to see the rendered schematic, or any `*.md` to read the bench-assembly guide.

## When the code refuses

The most useful thing the framework does is refuse to build designs that wouldn't work. Examples it catches at construction, before you've spent an evening at the bench:

```python
# Wiring two chip outputs together — short circuit
u1 = SN74HC04(refdes_number=1)
wire(u1.y_1, u1.y_2)
# ValueError: wire() has multiple drivers ('y_1', 'y_2') — short circuit

# Mating connectors that don't physically pair
mate(Pin2x20MaleHeader(...), JSTPHCableHousing(...))
# TypeError: Pin2x20MaleHeader mates with Pin2x20FemaleHeader, not JSTPHCableHousing
```

You don't need to know that two CMOS outputs fighting will burn out one or both. The framework knows. When `pytest` is green, the topology is sound.

## A real design

`demos/water_alarm/` is the simplest end-to-end example — four chips, two LEDs, a pair of probes mounted in a tank. The source is `water_alarm.py`; open `docs/WaterAlarm.svg` for the rendered schematic, or `docs/WaterAlarm.bom.csv` for the parts list. The same folder shape applies to every demo. See [`docs/learning-path.md`](docs/learning-path.md) for the suggested order to work through them.

## What it doesn't do

- **Solve Ohm's law.** Logic-level only. For continuous-voltage simulation, export to SPICE and let ngspice handle it.
- **Simulate firmware.** Model firmware as a private cell inside a chip subclass (see `demos/digital_thermometer/`); the cell is your code.
- **Lay out a PCB.** KiCad netlist export gets you to the start of layout; KiCad does the rest.

See [`docs/design-principles.md`](docs/design-principles.md) for why the framework is shaped the way it is.

## Install

Requires Python 3.10+:

```bash
uv venv && uv pip install -e ".[dev]"
# or
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

Full coverage of the framework, components, every export format with byte-deterministic golden files, end-to-end round-trips, and property-based stress on the load-bearing logic.

## Going further

- [`demos/`](demos/) — every demo is a complete study artifact (source + all six exports + rendered schematic).
- [`docs/learning-path.md`](docs/learning-path.md) — suggested order for working through the demos.
- [`docs/design-principles.md`](docs/design-principles.md) — why the framework refuses what it refuses.
- [`docs/component-library-data.md`](docs/component-library-data.md) — catalogue of all 122 modelled components with datasheet links, pin maps, and footprints.
- [`docs/`](docs/) — implementation specs for every major work package.
- [`CLAUDE.md`](CLAUDE.md) — design philosophy in full, for contributors.

## Licensing

Released under the [PolyForm Noncommercial License 1.0.0](LICENSE) — free for non-commercial use, including personal study, hobby projects, academic research, and use by educational, charitable, or public institutions.

**Commercial use requires a separate paid license.** Contact the project maintainer for terms.
