# backup_power

A 24-V backup-power supply for a 25-W PLC controller — TI Designs TIDUCC7. Three-stage architecture: a TPS2660 eFuse on the input (protection against over-voltage / over-current spikes), an LM5002 boost converter charging a 1200 µF bulk capacitor up to 48 V, and an LM5160 buck regulator that takes over delivering 17 V to the system bus when the primary supply browns out. The bulk cap holds the controller alive for a few seconds while a host system sequences a safe shutdown.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### Two outputs fighting on the bus

```python
# In BackupPower.__init__, perhaps a "consolidation" tries to tie the
# bus output and the bulk-cap voltage onto the same trace — they look
# like the same node in casual reading:
wire(self.supervisor.ports['vout_v'], self.supervisor.ports['bulk_v'])

BackupPower()
# ShortCircuitError: wire() has multiple drivers ('vout_v', 'bulk_v') — short circuit
```

The `BackupSupervisor` cell exposes both signals as `Direction.OUT` because each is independently driven by the system supervisor's state machine: `vout_v` follows the buck regulator's output, `bulk_v` follows the bulk cap's charge trajectory. They're related but not the same — and tying them together forces the supervisor's two state outputs into contention. The bench equivalent is a routing error where the buck's feedback node lands on the bulk cap; the buck's control loop diverges, the bulk cap discharges through the buck's pass element, and the whole supply rings itself to death.

### A floating boost-stage power path

```python
# In BackupPower.__init__, perhaps an attempt to "complete the
# unwired boost stage" by tying the inductor's two terminals and the
# Schottky's terminals together — the schematic shows them all on
# the same node when the LM5002 switch is on:
wire(self.d1.anode, self.d1.cathode, self.l1.t1, self.l1.t2)

BackupPower()
# FloatingNetError: Floating logical net — multiple passive BIDIRs with no driver: 'D1N5817.anode', 'D1N5817.cathode', 'Inductor.t1', 'Inductor.t2'
```

The real-hardware switch node is driven by the LM5002's silicon — a transistor inside the IC switches it to ground 200,000 times a second. In the model, the LM5002 is an opaque BOM-only chip; its switching can't be simulated by a voltage-only graph. The framework deliberately leaves the boost-stage power path unwired so the BOM is correct without falsely asserting a steady-state voltage on a node that doesn't have one. A user who joins these four passives is asserting the wrong topology — and the logical-net walker catches it at `super().__init__()`, naming the offending pins.

## Running it

```bash
python demos/backup_power/backup_power.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`BackupPower.bom.csv`](docs/BackupPower.bom.csv) — parts list
- [`BackupPower.md`](docs/BackupPower.md) — breadboard assembly guide
- [`BackupPower.net`](docs/BackupPower.net) — KiCad netlist
- [`BackupPower.cir`](docs/BackupPower.cir) — SPICE deck
- [`BackupPower.svg`](docs/BackupPower.svg) — rendered schematic
- [`BackupPower.dot`](docs/BackupPower.dot) — Graphviz source for the schematic
- [`BackupPower.mmd`](docs/BackupPower.mmd) — Mermaid flowchart
- [`BackupPower.yosys.json`](docs/BackupPower.yosys.json) — Yosys/netlistsvg JSON
- [`BackupPower.net-report.md`](docs/BackupPower.net-report.md) — every logical net, drivers, readers, domain
- [`BackupPower.domain-report.md`](docs/BackupPower.domain-report.md) — ground domains and isolation boundaries
- [`BackupPower.interface-report.md`](docs/BackupPower.interface-report.md) — public connector pins and their connections

## Going further

- The source: [`backup_power.py`](backup_power.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
