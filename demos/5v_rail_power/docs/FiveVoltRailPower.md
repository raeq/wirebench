# FiveVoltRailPower

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
Chips have unwired supply pins — the assembled circuit won't power up. Wire each pin below to its rail in the design source:
  - U1 pin 2 (GND) [ground] — wire to the − rail
```

## Use a different export

- **PCB layout** — `FiveVoltRailPower.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `FiveVoltRailPower.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `FiveVoltRailPower.svg` (rendered from `FiveVoltRailPower.dot`) and `FiveVoltRailPower.mmd` give the schematic as a graph diagram.
- **Procurement** — `FiveVoltRailPower.bom.csv` is the parts list for the PCB build.
