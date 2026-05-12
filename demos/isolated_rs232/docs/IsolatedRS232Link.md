# IsolatedRS232Link

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
Multi-board design (top level is a IsolatedRS232Link containing 3 Boards). Multi-board assemblies aren't usefully built on a single breadboard. Export each board's internal circuit separately.
```

## Use a different export

- **PCB layout** — `IsolatedRS232Link.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `IsolatedRS232Link.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `IsolatedRS232Link.svg` (rendered from `IsolatedRS232Link.dot`) and `IsolatedRS232Link.mmd` give the schematic as a graph diagram.
- **Procurement** — `IsolatedRS232Link.bom.csv` is the parts list for the PCB build.
