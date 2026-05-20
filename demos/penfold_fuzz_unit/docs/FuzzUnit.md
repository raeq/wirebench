# FuzzUnit

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
2 parts can't be assembled on a breadboard:
  - J1 (Audio3p5mmTRSJack) — Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles
  - J2 (Audio3p5mmTRSJack) — Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles

Use `export(<design>, 'kicad', …)` for a PCB netlist, or rework the design with breadboard-friendly part variants (DIP packages, THT passives, 0.1" headers).
```

## Use a different export

- **PCB layout** — `FuzzUnit.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `FuzzUnit.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `FuzzUnit.svg` (rendered from `FuzzUnit.dot`) and `FuzzUnit.mmd` give the schematic as a graph diagram.
- **Procurement** — `FuzzUnit.bom.csv` is the parts list for the PCB build.
