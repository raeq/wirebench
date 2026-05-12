# BLDCSystem

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
Multi-board design (top level is a BLDCSystem containing 2 Boards). Multi-board assemblies aren't usefully built on a single breadboard. Export each board's internal circuit separately.
```

## Use a different export

- **PCB layout** — `BLDCSystem.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `BLDCSystem.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `BLDCSystem.svg` (rendered from `BLDCSystem.dot`) and `BLDCSystem.mmd` give the schematic as a graph diagram.
- **Procurement** — `BLDCSystem.bom.csv` is the parts list for the PCB build.
