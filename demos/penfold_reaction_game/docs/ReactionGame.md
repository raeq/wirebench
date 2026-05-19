# ReactionGame

This design cannot be assembled on a standard 830-pin solderless breadboard.  The assembly-guide exporter refused with:

```
Chips have floating reset pins — the line is undefined at steady state and the chip will behave unpredictably. Wire each pin below either to a driver or through a pull-up resistor to the + rail in the design source:
  - U2 pin 15 (RST) [reset] — wire to a driver or pull-up to + rail
```

## Use a different export

- **PCB layout** — `ReactionGame.net` is a KiCad netlist; import into Pcbnew to lay out a board.
- **Simulation** — `ReactionGame.cir` is a SPICE deck; run it in ngspice or LTspice before committing to silicon.
- **Documentation** — `ReactionGame.svg` (rendered from `ReactionGame.dot`) and `ReactionGame.mmd` give the schematic as a graph diagram.
- **Procurement** — `ReactionGame.bom.csv` is the parts list for the PCB build.
