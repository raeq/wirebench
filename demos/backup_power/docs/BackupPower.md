# BackupPower

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
3 parts can't be assembled on a breadboard:
  - U1 (TPS2660) — Package_SON:WSON-10-1EP_3x3mm_P0.5mm_EP1.6x2.4mm
  - U2 (LM5002) — Package_SO:VSSOP-8_3.0x3.0mm_P0.65mm
  - U3 (LM5160) — Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm

Use `export(<design>, 'kicad', …)` for a PCB netlist, or rework the design with breadboard-friendly part variants (DIP packages, THT passives, 0.1" headers).
```

## Use a different export

- **PCB layout** — `BackupPower.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `BackupPower.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `BackupPower.svg` (rendered from `BackupPower.dot`) and `BackupPower.mmd` give the schematic as a graph diagram.
- **Procurement** — `BackupPower.bom.csv` is the parts list for the PCB build.
