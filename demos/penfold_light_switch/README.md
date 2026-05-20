# penfold_light_switch

A dawn / dusk light-activated switch.  An LDR + fixed-resistor divider
produces a midpoint voltage that tracks ambient light; an LM741
comparator with a potentiometer-set threshold flips its output when
the midpoint crosses the trip point; a BC547 NPN switching transistor
saturates and drives an indicator LED.  Faithful to R. A. Penfold's
BP107 Project 3 (pages 34–37, Fig. 9 / 10).

This is the *sensor → threshold → switched-output* pattern in its
purest analog form.  Wirebench's existing water-alarm demo touches
the same ground but routes through digital logic chips; this one is
the pure-analog ancestor of every motion-sensor, light-sensor, and
photo-relay circuit ever built.

## What this design is protected from

The framework refused these specific mistakes during this design's
development.  Each snippet is a near-miss — paste the broken lines
into your own copy of the design and wirebench raises before the
design can run.

### A floating LDR

```python
class BrokenLightSwitch(Circuit):
    def __init__(self) -> None:
        # ...rails declared...
        self.ldr = Photoresistor(dark_ohms=1_000_000, light_ohms=400,
                                 refdes_number=2)
        # Wired LDR.t2 to the comparator but forgot LDR.t1 to VCC:
        wire(self.ldr.t2, self.u1.IN_POS)
        super().__init__()

BrokenLightSwitch()
# UnconnectedPinError: Pin 'R2.t1' is mandatory but has no connection
```

The LDR's two terminals are mandatory (the framework refuses any
2-lead passive with a dangling terminal — same rule as the Resistor /
Capacitor / Inductor).  Forgetting the supply-side connection means
the LDR sits in series with nothing, the divider midpoint floats, and
the comparator reads garbage.  Wirebench refuses at construction.

### A mismatched comparator input domain

```python
# Wired the LDR midpoint to a Digital-typed rail by mistake:
wire(self.ldr.t2, self.gnd_d.out)
# SignalTypeMismatchError: wire() incompatible signal_types
#     - Photoresistor.t2 (Analog)
#     - Rail.out (Digital)
```

The LDR's terminals are `Analog`; tying one of them to the Digital
twin rail meant for the LED return path crosses the signal-type
boundary.  The framework refuses at the `wire()` call, naming both
ports so the fix (use the Analog rail for the LDR divider, keep the
Digital rail for the LED branch only) is obvious.

## Running it

```bash
python demos/penfold_light_switch/penfold_light_switch.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`LightActivatedSwitch.bom.csv`](docs/LightActivatedSwitch.bom.csv) — parts list
- [`LightActivatedSwitch.md`](docs/LightActivatedSwitch.md) — breadboard assembly guide
- [`LightActivatedSwitch.breadboard.svg`](docs/LightActivatedSwitch.breadboard.svg) — breadboard layout
- [`LightActivatedSwitch.net`](docs/LightActivatedSwitch.net) — KiCad netlist
- [`LightActivatedSwitch.kicad_sch`](docs/LightActivatedSwitch.kicad_sch) — KiCad schematic
- [`LightActivatedSwitch.cir`](docs/LightActivatedSwitch.cir) — SPICE deck
- [`LightActivatedSwitch.svg`](docs/LightActivatedSwitch.svg) — rendered schematic
- [`LightActivatedSwitch.dot`](docs/LightActivatedSwitch.dot) — Graphviz source
- [`LightActivatedSwitch.mmd`](docs/LightActivatedSwitch.mmd) — Mermaid flowchart
- [`LightActivatedSwitch.yosys.json`](docs/LightActivatedSwitch.yosys.json) — Yosys JSON
- [`LightActivatedSwitch.net-report.md`](docs/LightActivatedSwitch.net-report.md) — every logical net
- [`LightActivatedSwitch.domain-report.md`](docs/LightActivatedSwitch.domain-report.md) — ground domains
- [`LightActivatedSwitch.interface-report.md`](docs/LightActivatedSwitch.interface-report.md) — public ports

## Going further

- The source: [`penfold_light_switch.py`](penfold_light_switch.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  34–37 (text), Fig. 9 (schematic), Fig. 10 (layout).
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
