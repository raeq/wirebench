# wirebench

> *Describe real electronic circuits in Python. The framework won't let a design that wouldn't physically work compile — so when your tests are green, the breadboard build matches.*

**KiCad's ERC catches defective wiring after you've drawn the schematic. wirebench prevents you from constructing the wrong design in the first place** — no burnt CMOS outputs from two drivers fighting on one net, no half-evenings tracing a regulator that never had a ground wired, no second order at Mouser because the cable housings don't fit the header you placed. Wire two chip outputs together and `wire()` raises. Leave a regulator's input floating and the `Circuit` subclass refuses to instantiate. Try to mate a male pin header to a JST plug and `mate()` says no. The defects ERC would flag *after* you've drawn the schematic are flagged *before* the Python design even imports cleanly.

If you've programmed an Arduino but felt like wiring the surrounding circuit is a black art — every project a hunt for the magic combination of pull-ups, current-limiting resistors, decoupling caps, and "did I just wire the LED backwards?" — wirebench is where every line of code maps to a physical operation. You write Python that says *"a 330 Ω resistor in series with a red LED between VCC and GND."* The wires in the code are the wires you'll need on the breadboard, and the design either constructs cleanly or it doesn't — there's no middle state where pytest passes but the bench build smokes.

## Who this is for

wirebench is for **hobbyists, makers, and students** doing code-first electronics design: Python programmers building real circuits, students learning electronics through code rather than schematic-editor menus, educators looking for an immediate-feedback teaching tool that refuses defective designs before students reach the bench. If you're at home with `pytest` and you want your hardware design under the same discipline, this is for you.

It's not for ASIC designers, EDA professionals running full Altium/Cadence PCB-layout flows, or anyone who needs continuous-voltage SPICE-grade simulation in Python. wirebench pairs cleanly with KiCad for layout (export to netlist) and ngspice for simulation (export to SPICE) — it does the part those tools don't: catching topology defects at the moment you write the code.

## Hello, world

```python
from wirebench import Resistor, LED, Rail, Circuit, wire, export

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

| Format           | Extension              | What it's for                                                                                  |
|------------------|------------------------|------------------------------------------------------------------------------------------------|
| BOM CSV          | `.bom.csv`             | Paste into a parts cart at Mouser / Digikey / Tayda                                            |
| KiCad netlist    | `.net`                 | Import into KiCad's Pcbnew to lay out a PCB                                                    |
| KiCad schematic  | `.kicad_sch`           | Open in Eeschema 9.x to review the design visually before building                             |
| SPICE deck       | `.cir`                 | Simulate in ngspice or LTspice before building                                                 |
| Mermaid          | `.mmd`                 | Embed in a README to document what you built                                                   |
| Graphviz DOT     | `.dot`                 | Render to SVG / PNG with `dot -Tsvg`                                                           |
| Yosys JSON       | `.yosys.json`          | Render to a browser-friendly schematic via [netlistsvg](https://github.com/nturley/netlistsvg) |
| Assembly Guide   | `.md`                  | Read at the bench — recipe-style breadboard build instructions                                 |
| Breadboard SVG   | `.breadboard.svg`      | Open in a browser — the design as it sits on a standard solderless breadboard                  |
| Net Report       | `.net-report.md`       | Every logical net, what drives it, what reads it, domain assignment                            |
| Domain Report    | `.domain-report.md`    | Every `GroundDomain`, parts in each, where isolation boundaries sit                            |
| Interface Report | `.interface-report.md` | Every `Board`'s public connector pins and what they connect to                                 |

Every demo in `demos/` ships with all twelve exports pre-generated in its `docs/` subfolder — open any `*.kicad_sch` in Eeschema or any `*.svg` to see the rendered schematic, or any `*.md` to read the bench-assembly guide and the three review reports.  The catalogue currently ships **eighteen demos** spanning hello-world LED circuits, vintage-1980s hobbyist designs (the Penfold corpus), and modern microcontroller / power / isolation patterns.

## What it prevents

Three categories of real-world harm wirebench rules out before the design ever reaches a breadboard — each caught in milliseconds, each with the kind of error message that names the offending part and tells you what to fix.

### Burnt outputs

```python
u1 = SN74HC04(refdes_number=1)
wire(u1.y_1, u1.y_2)
# ShortCircuitError: wire() has multiple drivers ('y_1', 'y_2') — short circuit
```

Two CMOS outputs fighting on the same net will burn out one or both. You don't need to know which — wirebench knows, and `wire()` raises before the call returns. The chip never gets the chance to suffer the experiment.

### A wasted parts order

```python
mate(Header2xNMale(...), JSTPHCableHousing(...))
# IncompatibleMateError: Header2xNMale mates with Header2xNFemale, not JSTPHCableHousing
```

Pitch, pin count, and gender all checked at `mate()` time. You don't put through a JST cable order, wait five days, and discover the housings don't fit the header on your board — the wrong combination never gets past the Python.

### Hours of fault-tracing

```python
class CrossedRails(Circuit):
    def __init__(self):
        self.vcc1 = Rail(True)
        self.vcc2 = Rail(True)
        self.r1   = Resistor(330, refdes_number=1)
        wire(self.vcc1.out, self.r1.t1)
        wire(self.vcc2.out, self.r1.t1)   # legal in isolation
        super().__init__()
# ShortCircuitError: Short circuit on logical net — multiple drivers: 'Rail.out', 'Rail.out'
```

Each `wire()` call is fine in isolation — the contention only emerges when the framework walks the combined logical net at `super().__init__()`. This is the same algorithm KiCad's ERC runs, except KiCad waits for you to click *Run ERC* and wirebench waits no longer than `__init__` returning. Without that walk, you'd find the conflict the slow way: build the design, watch the supplies fight, scope every node looking for the one that doesn't sit where it should.

---

The same logic prevents other classes of harm hobbyists don't always know to look for: forbidden runtime states (S=1, R=1 on an SR latch) that would lock a latch into undefined behaviour, ground-domain crossings without an isolator that would defeat the point of having isolation, chips with declared output pins that nothing internal drives — every quiet failure mode where the circuit looks right and doesn't work. Every error message names the offending part by refdes and pin number, so you know what to fix before you reach for a soldering iron.

When `pytest` is green, the topology is sound.

## A real design

`demos/water_alarm/` is the simplest end-to-end example — four chips, two LEDs, a pair of probes mounted in a tank. The source is `water_alarm.py`; open `docs/WaterAlarm.svg` for the rendered schematic, or `docs/WaterAlarm.bom.csv` for the parts list. The same folder shape applies to every demo. See [`docs/learning-path.md`](docs/learning-path.md) for the suggested order to work through them.

## What it doesn't do

- **Solve Ohm's law.** Logic-level only. For continuous-voltage simulation, export to SPICE and let ngspice handle it.
- **Catch parameter mistakes.** The framework prevents defective *topology* — shorts, floating nets, mismatched connectors, forbidden states, cross-domain wiring — but it won't save you from a 330 Ω current limiter sized for a high-current LED, a 25 V capacitor on a 30 V rail, or a regulator dissipating 4 W with no heatsink. Use SPICE, arithmetic, or the per-component `GOTCHAS` strings for those.
- **Simulate firmware.** Model firmware as a private cell inside a chip subclass (see `demos/digital_thermometer/`); the cell is your code.
- **Lay out a PCB.** KiCad netlist export gets you to the start of layout; KiCad does the rest.

See [`docs/design-principles.md`](docs/design-principles.md) for why the framework is shaped the way it is.

## Documentation

The docs are published at **<https://raeq.github.io/wirebench/>** — searchable, with the learning path, prevention benchmark, design principles, and component catalogue cross-linked.

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
- [`docs/design-principles.md`](docs/design-principles.md) — why the framework prevents what it prevents.
- [`docs/component-library-data.md`](docs/component-library-data.md) — hand-curated catalogue with datasheet links, pin maps, and footprints; [`docs/parts.md`](docs/parts.md) — auto-generated index of all 150 modelled components, searchable on the doc site.
- [`docs/`](docs/) — implementation specs for every major work package.
- [`CLAUDE.md`](CLAUDE.md) — design philosophy in full, for contributors.

## Licensing

Released under the [PolyForm Noncommercial License 1.0.0](LICENSE) — free for non-commercial use, including personal study, hobby projects, academic research, and use by educational, charitable, or public institutions.

**Commercial use requires a separate paid license.** Contact the project maintainer for terms.
