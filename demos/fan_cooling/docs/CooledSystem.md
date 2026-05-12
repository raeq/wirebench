# CooledSystem

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
Multi-board design (top level is a CooledSystem containing 2 Boards). Multi-board assemblies aren't usefully built on a single breadboard. Export each board's internal circuit separately.
```

## Use a different export

- **PCB layout** — `CooledSystem.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `CooledSystem.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `CooledSystem.svg` (rendered from `CooledSystem.dot`) and `CooledSystem.mmd` give the schematic as a graph diagram.
- **Procurement** — `CooledSystem.bom.csv` is the parts list for the PCB build.
