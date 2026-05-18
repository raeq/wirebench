# hello_led

The smallest buildable wirebench design: a red LED in series with a 330 Ω current-limit resistor, between a 5 V rail and ground. Build it on a breadboard, apply power, the LED lights. The three `wire()` calls in the Python file map one-for-one to the three jumpers you place on the board.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench refuses to construct it.

### A floating resistor

```python
class BrokenHelloLED(Circuit):
    def __init__(self) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.r1  = Resistor(330, refdes_number=1)
        self.d1  = LED('red', refdes_number=1)

        wire(self.r1.t1, self.r1.t2)         # joined R1's two legs to each other
        wire(self.vcc.out, self.d1.anode)    # then ran the LED straight across the rails
        wire(self.gnd.out, self.d1.cathode)
        super().__init__()
# FloatingNetError: Floating logical net — multiple passive BIDIRs with no driver: 'Resistor.t1', 'Resistor.t2'
```

A typo wires R1's two terminals to each other; the LED gets its own straight path across the rails. R1's net now contains only two passive BIDIR ports — nothing on it is driving anything. The framework's logical-net walker visits the resistor at `super().__init__()`, sees both terminals sitting on a net with no OUT/BIDIR source, and names the offending pins. The bench equivalent is a working LED *and* the wrong amount of current through it — exactly the silent miswire that makes "but the LED still lit up" testing useless.

### A shorted supply

```python
wire(self.vcc.out, self.gnd.out)
# ShortCircuitError: wire() has multiple drivers ('out', 'out') — short circuit
```

`Rail(True)` and `Rail(False)` are both drivers; wiring them together is a 5 V to ground short. The framework refuses inside `wire()` itself — the call raises before returning, so the rest of the circuit's construction never runs. The bench equivalent is the smell of overheating bench-supply wiring; the framework catches it before you build it.

## Running it

```bash
python demos/hello_led/hello_led.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`HelloLED.bom.csv`](docs/HelloLED.bom.csv) — parts list (one resistor, one LED)
- [`HelloLED.md`](docs/HelloLED.md) — breadboard assembly guide
- [`HelloLED.net`](docs/HelloLED.net) — KiCad netlist
- [`HelloLED.cir`](docs/HelloLED.cir) — SPICE deck
- [`HelloLED.svg`](docs/HelloLED.svg) — rendered schematic
- [`HelloLED.dot`](docs/HelloLED.dot) — Graphviz source for the schematic
- [`HelloLED.mmd`](docs/HelloLED.mmd) — Mermaid flowchart
- [`HelloLED.yosys.json`](docs/HelloLED.yosys.json) — Yosys/netlistsvg JSON

## Going further

- The source: [`hello_led.py`](hello_led.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
