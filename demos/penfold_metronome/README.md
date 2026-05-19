# penfold_metronome

An NE555 astable driving a small 8 Ω speaker through an AC-coupling
capacitor — the classic *audible beat at adjustable tempo* circuit.
Faithful to R. A. Penfold's BP107 Project 9 (pages 57–60, Fig. 26 / 27).

This demo pairs with [`penfold_one_second_timer`](../penfold_one_second_timer/)
to establish the two classical astable topologies in the wirebench
catalogue: the op-amp relaxation oscillator (P8) and the NE555 RC
astable (P9).  Together they teach that *square wave from a few
passives + one chip* has more than one valid recipe.

## What this design is protected from

### A speaker tied straight to the 555 output (no AC coupling)

```python
wire(self.u1.OUT, self.ls1.t1)
# FloatingNetError or worse: the static check might pass, but the
# bench result is a continuous DC current through the voice coil
# every time the 555's output sits HIGH.  After ten minutes the
# coil is too hot to touch.
```

This is *the* most common 555-astable mistake.  The 555's output
sits at half-supply on average; tying the speaker's coil between
that and GND drives a steady DC current through the coil along
with the AC signal.  The DC component heats the coil and shifts
the cone off-centre.  C3 in series with the speaker (10 µF
electrolytic in the design) blocks the DC component while passing
the audio-band AC.  Wirebench can't catch the DC-heating bug
directly — it's a parameter-class concern — but the assembly-guide
GOTCHAS for `Speaker` flag it as one of the *bench* things the
framework can't enforce but the documentation must.

### A floating timing capacitor

```python
class BrokenMetronome(Circuit):
    def __init__(self) -> None:
        # ... rails / timer declared ...
        self.c1 = Capacitor(100e-9, refdes_number=1)
        wire(self.vr1.t2, self.u1.THRES, self.u1.TRIG, self.c1.t1)
        # Forgot to wire C1.t2 to GND.
        super().__init__()

BrokenMetronome()
# UnconnectedPinError: Pin 'C1.t2' is mandatory but has no connection
```

Both terminals of the timing cap are mandatory (Capacitor refuses
dangling pins).  The framework refuses the design before the
breadboard sees a jumper.

## Running it

```bash
python demos/penfold_metronome/penfold_metronome.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`Metronome.bom.csv`](docs/Metronome.bom.csv) — parts list
- [`Metronome.md`](docs/Metronome.md) — breadboard assembly guide
- [`Metronome.breadboard.svg`](docs/Metronome.breadboard.svg) — breadboard layout SVG
- [`Metronome.net`](docs/Metronome.net) — KiCad netlist
- [`Metronome.kicad_sch`](docs/Metronome.kicad_sch) — KiCad schematic
- [`Metronome.cir`](docs/Metronome.cir) — SPICE deck
- [`Metronome.svg`](docs/Metronome.svg) — rendered schematic
- [`Metronome.dot`](docs/Metronome.dot) — Graphviz source
- [`Metronome.mmd`](docs/Metronome.mmd) — Mermaid flowchart
- [`Metronome.yosys.json`](docs/Metronome.yosys.json) — Yosys JSON
- [`Metronome.net-report.md`](docs/Metronome.net-report.md) — every logical net
- [`Metronome.domain-report.md`](docs/Metronome.domain-report.md) — ground domains
- [`Metronome.interface-report.md`](docs/Metronome.interface-report.md) — public ports

## Going further

- The source: [`penfold_metronome.py`](penfold_metronome.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  57–60 (text), Fig. 26 (schematic), Fig. 27 (layout).
- The op-amp relaxation-oscillator sibling: [`../penfold_one_second_timer/`](../penfold_one_second_timer/)
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
