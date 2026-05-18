# dice

A classic hobbyist electronic dice: an NE555 timer chip clocks a CD4017 decade counter, six counter outputs route through a diode-OR matrix to seven LEDs arranged in the familiar dice-face pattern. Press the button to release the counter from reset; press again to freeze whichever face is showing. No firmware — just analog and CMOS, the same shape as the dice circuits in 1970s electronics magazines.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### Two diode-OR outputs fighting

```python
# A typo wires the two OR matrix outputs to each other, perhaps
# intending to "merge the LED groups":
wire(self.or_a.out, self.or_c.out)
# ShortCircuitError: wire() has multiple drivers ('out', 'out') — short circuit
```

The `DiodeOR` cell exposes its `out` port as `Direction.OUT` — the abstraction has decided that the OR's output is the *driver* on whichever net it joins. Wiring two `out` ports together puts two drivers on one net; `wire()` refuses immediately. On the bench this would show up as the LED-A group and LED-C group lighting *together* for any value of the counter, which is dice with all the dice-ness removed.

### A floating LED anode

```python
# Forget to include led_a.anode in the wire that drives the LED-A net
# (the centre LED for odd rolls):
wire(self.or_a.out,
     self.d1.cathode, self.d2.cathode, self.d3.cathode,
     self.r_a.t1, self.r_a.t2)
# missing: self.led_a.anode
# UnconnectedPinError: Unconnected mandatory port(s): 'LED.anode'
```

LED.anode is `mandatory=True` — leaving it unwired isn't a topological "floating net" (there's no net at all), but a missing connection on a port the framework promised. The framework's surface-port walker catches this at `super().__init__()`, before any of the seven LED faces ever light. The bench equivalent is rolling odd numbers and seeing the dice show six dots — every roll — because the centre LED never participates.

## Running it

```bash
python demos/dice/dice.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`Dice.bom.csv`](docs/Dice.bom.csv) — parts list
- [`Dice.md`](docs/Dice.md) — breadboard assembly guide
- [`Dice.net`](docs/Dice.net) — KiCad netlist
- [`Dice.cir`](docs/Dice.cir) — SPICE deck
- [`Dice.svg`](docs/Dice.svg) — rendered schematic
- [`Dice.dot`](docs/Dice.dot) — Graphviz source for the schematic
- [`Dice.mmd`](docs/Dice.mmd) — Mermaid flowchart
- [`Dice.yosys.json`](docs/Dice.yosys.json) — Yosys/netlistsvg JSON
- [`Dice.net-report.md`](docs/Dice.net-report.md) — every logical net, drivers, readers, domain
- [`Dice.domain-report.md`](docs/Dice.domain-report.md) — ground domains and isolation boundaries
- [`Dice.interface-report.md`](docs/Dice.interface-report.md) — public connector pins and their connections

## Going further

- The source: [`dice.py`](dice.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
