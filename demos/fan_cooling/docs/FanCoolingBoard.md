# FanCoolingBoard

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
The assembly-guide exporter renders single-circuit designs onto a standard 830-pin solderless breadboard. The top-level design is a Board (FanCoolingBoard) — a populated PCB. Use `export(board.circuit, 'assembly_guide', …)` to assemble the board's internal circuit, or use the `kicad` exporter for PCB layout.
```

## Use a different export

- **PCB layout** — `FanCoolingBoard.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `FanCoolingBoard.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `FanCoolingBoard.svg` (rendered from `FanCoolingBoard.dot`) and `FanCoolingBoard.mmd` give the schematic as a graph diagram.
- **Procurement** — `FanCoolingBoard.bom.csv` is the parts list for the PCB build.
