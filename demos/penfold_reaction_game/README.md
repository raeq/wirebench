# penfold_reaction_game

Push-button reaction-time game.  An NE555 astable clocks a CD4017
decade counter at a few hundred hertz; ten indicator LEDs hang off the
counter's ten outputs.  While S1 is pressed the counter sweeps too
fast for the eye to resolve; release S1 and the LED illuminated at
that instant becomes the readout.  Faithful to R. A. Penfold's
BP107 Project 22 (pages 110–113, Fig. 56 / 57).

## What this design is protected from

The framework refused these specific mistakes during this design's
development.  Each snippet is a near-miss — paste the broken lines
into your own copy of the design and wirebench raises before the
design can run.

### A floating LED current-limit resistor

```python
class BrokenReactionGame(Circuit):
    def __init__(self) -> None:
        # ... rails, timer, counter declared ...
        self.led = LED('red', refdes_number=1)
        self.r   = Resistor(470, refdes_number=1)

        wire(self.counter.Q0, self.led.anode)
        wire(self.led.cathode, self.r.t1)
        # Forgot the wire from R.t2 back to GND.
        super().__init__()

BrokenReactionGame()
# UnconnectedPinError: Pin 'R1.t2' is mandatory but has no connection
```

Both terminals of a resistor are mandatory in wirebench — a dangling
limit resistor is a real bench bug where the LED appears wired but
draws no current and never lights.  The framework refuses the design
at `super().__init__()` instead of letting the demo produce a silent
"why isn't D5 lighting?" failure on the bench.

### Mismatched signal types on the CE pin

```python
# Drove the CE input with an Analog rail directly:
wire(self.vcc_a.out, self.counter.CE)
# SignalTypeMismatchError: wire() incompatible signal_types
#     - Rail.out (Analog)
#     - CD4017.CE (Digital)
```

CD4017's CE is declared `Digital`; the Analog twin-rail used for the
chip's VDD/VSS is not interchangeable with a logic-level tie-off.
The framework refuses the wire at construction time, naming both
ports so the fix (use the Digital `vcc` rail, or wire CE via a
conductor) is obvious before the breadboard sees a jumper.

## Running it

```bash
python demos/penfold_reaction_game/penfold_reaction_game.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`ReactionGame.bom.csv`](docs/ReactionGame.bom.csv) — parts list
- [`ReactionGame.md`](docs/ReactionGame.md) — breadboard assembly guide
- [`ReactionGame.breadboard.svg`](docs/ReactionGame.breadboard.svg) — breadboard layout SVG
- [`ReactionGame.net`](docs/ReactionGame.net) — KiCad netlist
- [`ReactionGame.kicad_sch`](docs/ReactionGame.kicad_sch) — KiCad schematic, open in Eeschema 9.x
- [`ReactionGame.cir`](docs/ReactionGame.cir) — SPICE deck
- [`ReactionGame.svg`](docs/ReactionGame.svg) — rendered schematic
- [`ReactionGame.dot`](docs/ReactionGame.dot) — Graphviz source
- [`ReactionGame.mmd`](docs/ReactionGame.mmd) — Mermaid flowchart
- [`ReactionGame.yosys.json`](docs/ReactionGame.yosys.json) — Yosys/netlistsvg JSON
- [`ReactionGame.net-report.md`](docs/ReactionGame.net-report.md) — every logical net, drivers, readers
- [`ReactionGame.domain-report.md`](docs/ReactionGame.domain-report.md) — ground domains and isolation
- [`ReactionGame.interface-report.md`](docs/ReactionGame.interface-report.md) — public ports and their connections

## Going further

- The source: [`penfold_reaction_game.py`](penfold_reaction_game.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  110–113 (text), Fig. 56 (schematic), Fig. 57 (layout).
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
