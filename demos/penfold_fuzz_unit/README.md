# penfold_fuzz_unit

A guitar-effects *fuzz pedal* — a high-gain inverting op-amp stage
followed by a pair of anti-parallel clipping diodes.  The op-amp's
gain (~470x) lifts the guitar pickup's millivolt signal up past the
±0.7 V conduction threshold of the diodes; the diodes then clip the
output into a square-wave-with-rounded-edges waveform that gives
fuzz its characteristic raspy timbre.  Faithful to R. A. Penfold's
BP107 Project 30 (pages 145–end, Fig. 71 / 72).

The teaching point: **clipping diodes as a signal-processing
primitive.**  The same topology appears in every distortion /
overdrive / soft-clipper pedal ever built; the differences between
them are clipping-diode choice (silicon, germanium, LED), feedback
network shape, and post-clip EQ.  This demo is the minimum viable
fuzz: clean topology, no frills.

## What this design is protected from

### Forgetting the anti-parallel clipping pair

```python
class BrokenFuzz(Circuit):
    def __init__(self) -> None:
        # ... rails / op-amp / input chain declared ...
        self.d1 = D1N4148(refdes_number=1)
        # Only wired D1 (anode → OUT, cathode → GND); D2 missing.
        wire(self.u1.OUT, self.d1.anode)
        wire(self.d1.cathode, self.gnd.out)
        # Compiles, but: the topology now clips only one polarity.
        # Bench symptom: signal sounds like *half-wave-rectified
        # buzz* rather than fuzz — completely wrong sound.
```

Wirebench can't directly catch *only one of a pair* of clipping
diodes (it's a valid topology, just a different effect).  The net
report shows that OUT is wired to only one diode, which a builder
reading the export can flag.  This demo's test explicitly checks
that *exactly two* clipping diodes sit on the OUT net.

### Plugging the input jack tip directly into IN_NEG (no coupling cap)

```python
wire(self.input_jack.ports['tip'], self.u1.IN_NEG)
# The guitar's pickup has a few mV of DC offset on a good day; the
# op-amp's bias network sees this offset as a real input and the
# output saturates instantly.  Bench symptom: dead silence with
# the output rail saturated to +Vcc or GND depending on direction.
```

The framework accepts the wire (it's a valid topological connection),
but the design's *teaching* version always has an input AC-coupling
capacitor.  Reading the schematic export and seeing no cap between
the input jack and the op-amp is the catch — wirebench surfaces
the topology faithfully so the bug shows up in the visualisation
before it shows up on the bench.

## Running it

```bash
python demos/penfold_fuzz_unit/penfold_fuzz_unit.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`FuzzUnit.bom.csv`](docs/FuzzUnit.bom.csv) — parts list
- [`FuzzUnit.md`](docs/FuzzUnit.md) — breadboard assembly guide
- [`FuzzUnit.breadboard.svg`](docs/FuzzUnit.breadboard.svg) — breadboard layout
- [`FuzzUnit.net`](docs/FuzzUnit.net) — KiCad netlist
- [`FuzzUnit.kicad_sch`](docs/FuzzUnit.kicad_sch) — KiCad schematic
- [`FuzzUnit.cir`](docs/FuzzUnit.cir) — SPICE deck
- [`FuzzUnit.svg`](docs/FuzzUnit.svg) — rendered schematic
- [`FuzzUnit.dot`](docs/FuzzUnit.dot) — Graphviz source
- [`FuzzUnit.mmd`](docs/FuzzUnit.mmd) — Mermaid flowchart
- [`FuzzUnit.yosys.json`](docs/FuzzUnit.yosys.json) — Yosys JSON
- [`FuzzUnit.net-report.md`](docs/FuzzUnit.net-report.md) — net report
- [`FuzzUnit.domain-report.md`](docs/FuzzUnit.domain-report.md) — ground domains
- [`FuzzUnit.interface-report.md`](docs/FuzzUnit.interface-report.md) — public ports

## Going further

- The source: [`penfold_fuzz_unit.py`](penfold_fuzz_unit.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  145–end (text), Fig. 71 (schematic), Fig. 72 (layout).
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
