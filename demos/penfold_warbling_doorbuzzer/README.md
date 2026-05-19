# penfold_warbling_doorbuzzer

A *warbling* doorbell — two NE555 astables wired in a *modulator +
carrier* configuration so a slow oscillator gates a fast one.  The
result is a chirp-chirp-chirp warble that's far more attention-getting
than a plain steady tone.  Faithful to R. A. Penfold's BP107 Project 16
(pages 86–90, Fig. 42 / 43).

The teaching point: **one oscillator's output drives another's
control input.**  This is *circuit-as-graph-of-subcircuits* at the
within-board level — distinct from the between-board Board mating the
existing isolated_rs232 / fan_cooling demos teach.

## What this design is protected from

### Forgetting to gate U2's RESET

```python
# Wired U1.OUT to U2.CLK instead of U2.RESET — but there is no CLK
# pin on a 555.  Misremembered pin name:
wire(self.u1.OUT, self.u2.CLK)
# UnknownPortError: NE555 has no pin named 'CLK'
```

The 555 doesn't have a CLK pin — the framework refuses the wire-up
at construction because the named port doesn't exist on the chip.
A common misremembering when the design is sketched on paper from
analogy with logic chips; wirebench catches it immediately.

### Two 555s sharing one timing capacitor (a common copy-paste bug)

```python
wire(self.u1.THRES, self.u1.TRIG, self.c1.t1,
     dynamically_driven=True)
# Then later — copy-pasted, forgot to swap c1 → c2:
wire(self.u2.THRES, self.u2.TRIG, self.c1.t1,
     dynamically_driven=True)
# Result: U1 and U2 fight for control of C1's voltage.  Bench
# symptom: neither oscillator runs reliably, output is chaotic.
```

Wirebench can't directly catch *both 555s tied to the same cap* as
a defect (it's a valid wire-up to share a node), but the assembly
guide's net report makes the shared C1 obvious — running the design
through the export and reading the net-report.md shows the cap
appearing on more pins than expected.  Catching this on the export
beats catching it on the bench.

## Running it

```bash
python demos/penfold_warbling_doorbuzzer/penfold_warbling_doorbuzzer.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`WarblingDoorbuzzer.bom.csv`](docs/WarblingDoorbuzzer.bom.csv) — parts list
- [`WarblingDoorbuzzer.md`](docs/WarblingDoorbuzzer.md) — breadboard assembly guide
- [`WarblingDoorbuzzer.breadboard.svg`](docs/WarblingDoorbuzzer.breadboard.svg) — breadboard layout
- [`WarblingDoorbuzzer.net`](docs/WarblingDoorbuzzer.net) — KiCad netlist
- [`WarblingDoorbuzzer.kicad_sch`](docs/WarblingDoorbuzzer.kicad_sch) — KiCad schematic
- [`WarblingDoorbuzzer.cir`](docs/WarblingDoorbuzzer.cir) — SPICE deck
- [`WarblingDoorbuzzer.svg`](docs/WarblingDoorbuzzer.svg) — rendered schematic
- [`WarblingDoorbuzzer.dot`](docs/WarblingDoorbuzzer.dot) — Graphviz source
- [`WarblingDoorbuzzer.mmd`](docs/WarblingDoorbuzzer.mmd) — Mermaid flowchart
- [`WarblingDoorbuzzer.yosys.json`](docs/WarblingDoorbuzzer.yosys.json) — Yosys JSON
- [`WarblingDoorbuzzer.net-report.md`](docs/WarblingDoorbuzzer.net-report.md) — net report
- [`WarblingDoorbuzzer.domain-report.md`](docs/WarblingDoorbuzzer.domain-report.md) — ground domains
- [`WarblingDoorbuzzer.interface-report.md`](docs/WarblingDoorbuzzer.interface-report.md) — public ports

## Going further

- The source: [`penfold_warbling_doorbuzzer.py`](penfold_warbling_doorbuzzer.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  86–90 (text), Fig. 42 (schematic), Fig. 43 (layout).
- The single-555 metronome sibling: [`../penfold_metronome/`](../penfold_metronome/)
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
