# 5v_rail_power

A regulated 5 V breadboard supply from a stack of three CR2032 coin cells: 9 V from the stack → reverse-polarity Schottky → LM7805 linear regulator → output cap → 5.1 V Zener crowbar → power-good green LED. Install a jumper across SW1 to close the switch; if the LED lights, the supply is up. If it stays dark, one link in the chain is broken — that's the whole verification surface, and it's the safest fail mode for a hobby supply.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench refuses to construct it.

### A floating regulator input

```python
# In FiveVoltRailPower.__init__, drop the SeriesRectifier cell so the
# diode is a "pure passive" with no driver propagating across it:
self.d1 = D1N5817(refdes_number=1)
# (deleted: self.d1_rectifier = SeriesRectifier(v_f=0.3))

wire(self.sw1.pins[1].internal, self.d1.anode)
wire(self.d1.cathode, self.c1.t1, self.u1.INPUT)
# FloatingNetError: Floating logical net — multiple passive BIDIRs with no driver: 'Capacitor.t1', 'D1N5817.cathode'
```

Without the `SeriesRectifier` cell, D1's two terminals are still BIDIR but nothing drives across the diode in the simulation model. The regulator-input net now contains only the diode cathode and the cap terminal — two passive BIDIRs with no OUT/BIDIR driver upstream. The framework's logical-net walker visits the net at `super().__init__()`, finds it floating, and names the offending pins. On the bench this is the silent failure where you've soldered everything correctly but the regulator's input never sees a voltage — D3 stays dark, and you spend an hour with a multimeter chasing where the voltage stopped propagating.

### A shorted battery

```python
wire(self.bt1.pos, self.bt1.neg)
# ShortCircuitError: wire() has multiple drivers ('pos', 'neg') — short circuit
```

A typo wires the battery's `pos` and `neg` terminals together — both are `Direction.OUT` (a battery is a driver), so wiring them is a hundreds-of-milliamps short across nine volts of lithium chemistry. `wire()` raises before the call returns. The bench equivalent is a paperclip welded to the cell stack; *of all the catches in this codebase, this is the one whose failure mode actually starts a fire.*

## Running it

```bash
python demos/5v_rail_power/five_volt_rail_power.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`FiveVoltRailPower.bom.csv`](docs/FiveVoltRailPower.bom.csv) — parts list
- [`FiveVoltRailPower.md`](docs/FiveVoltRailPower.md) — breadboard assembly guide
- [`FiveVoltRailPower.net`](docs/FiveVoltRailPower.net) — KiCad netlist
- [`FiveVoltRailPower.cir`](docs/FiveVoltRailPower.cir) — SPICE deck
- [`FiveVoltRailPower.svg`](docs/FiveVoltRailPower.svg) — rendered schematic
- [`FiveVoltRailPower.dot`](docs/FiveVoltRailPower.dot) — Graphviz source for the schematic
- [`FiveVoltRailPower.mmd`](docs/FiveVoltRailPower.mmd) — Mermaid flowchart
- [`FiveVoltRailPower.yosys.json`](docs/FiveVoltRailPower.yosys.json) — Yosys/netlistsvg JSON

## Going further

- The source: [`five_volt_rail_power.py`](five_volt_rail_power.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
