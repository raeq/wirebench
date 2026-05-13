# PowerSourceBoard

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
The assembly-guide exporter renders single-circuit designs onto a standard 830-pin solderless breadboard. The top-level design is a Board (PowerSourceBoard) — a populated PCB. Use `export(board.circuit, 'assembly_guide', …)` to assemble the board's internal circuit, or use the `kicad` exporter for PCB layout.
```

## Use a different export

- **PCB layout** — `PowerSourceBoard.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `PowerSourceBoard.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `PowerSourceBoard.svg` (rendered from `PowerSourceBoard.dot`) and `PowerSourceBoard.mmd` give the schematic as a graph diagram.
- **Procurement** — `PowerSourceBoard.bom.csv` is the parts list for the PCB build.
