# li_ion_fuel_gauge

A single-cell Li-Ion battery pack with an on-board BQ27546-G1 fuel gauge: the cell, a 10 mΩ sense resistor for current measurement, an NTC thermistor for temperature, three I²C/HDQ pull-ups, and a 4-pin female header that exposes SDA, SCL, HDQ, and GND to a host system. The fuel gauge talks to a host over I²C or HDQ to report state-of-charge, voltage, temperature, and accumulated coulombs. Reproduces the topology of TIDA-00594.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A shorted cell

```python
# In BatteryPackBoard.__init__, perhaps a typo joins the cell's
# positive and negative terminals as if they were a single "pack
# ground" reference:
wire(self.bt1.ports['pos'], self.bt1.ports['neg'])

BatteryPackBoard(refdes_number=1)
# ShortCircuitError: wire() has multiple drivers ('pos', 'neg') — short circuit
```

Both `pos` and `neg` on the `Cell` are `Direction.OUT` — the cell is a driver, and the framework expects each terminal to land on its own net. Joining them is a direct short across the cell. The bench equivalent is the most spectacular failure mode in this BOM: a Li-Ion cell driven into hundreds-of-milliamps short produces gas, heat, and sometimes flame; the cell vents through whatever path the housing allows.

### A signal-type mismatch on the chip-enable pin

```python
# A natural-looking "improvement": pull the chip's CE pin HIGH by
# tying it to PACK+, which the design comments out as deliberately
# not done.  Replace the PACK+ net with:
wire(
    self.bt1.ports['pos'],
    self.u1.ports['BAT'],
    self.u1.ports['REGIN'],
    self.u1.ports['CE'],      # added: tie CE HIGH "for clarity"
    self.c_bat.ports['t1'],
    self.c_regin.ports['t1'],
)

BatteryPackBoard(refdes_number=1)
# SignalTypeMismatchError: Signal type mismatch in wire(): 'pos': Analog, 'BAT': Analog, 'CE': Digital, ...
```

The cell's terminals and the chip's `BAT` / `REGIN` pins are all `Analog` — they're carrying a continuous battery voltage. The chip's `CE` pin is `Digital` — it's expecting a logic-level signal from a protection IC or a microcontroller. The framework refuses to mix the two types on one net, because at the bench an analog rail at 4.2 V isn't a "logic HIGH" — it's a voltage that may or may not satisfy the chip's V_IH threshold across temperature, and silently corrupting that distinction makes for the kind of "works at room temp, fails in a hot car" failure that haunts power-management boards.

## Running it

```bash
python demos/li_ion_fuel_gauge/li_ion_fuel_gauge.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`BatteryPackBoard.bom.csv`](docs/BatteryPackBoard.bom.csv) — parts list
- [`BatteryPackBoard.md`](docs/BatteryPackBoard.md) — breadboard assembly guide
- [`BatteryPackBoard.net`](docs/BatteryPackBoard.net) — KiCad netlist
- [`BatteryPackBoard.cir`](docs/BatteryPackBoard.cir) — SPICE deck
- [`BatteryPackBoard.svg`](docs/BatteryPackBoard.svg) — rendered schematic
- [`BatteryPackBoard.dot`](docs/BatteryPackBoard.dot) — Graphviz source for the schematic
- [`BatteryPackBoard.mmd`](docs/BatteryPackBoard.mmd) — Mermaid flowchart
- [`BatteryPackBoard.yosys.json`](docs/BatteryPackBoard.yosys.json) — Yosys/netlistsvg JSON
- [`BatteryPackBoard.net-report.md`](docs/BatteryPackBoard.net-report.md) — every logical net, drivers, readers, domain
- [`BatteryPackBoard.domain-report.md`](docs/BatteryPackBoard.domain-report.md) — ground domains and isolation boundaries
- [`BatteryPackBoard.interface-report.md`](docs/BatteryPackBoard.interface-report.md) — public connector pins and their connections

## Going further

- The source: [`li_ion_fuel_gauge.py`](li_ion_fuel_gauge.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
