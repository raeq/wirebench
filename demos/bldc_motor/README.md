# bldc_motor

A brushless DC motor controller: an ATmega328P running a Hall-sensor commutator sketch, a TI DRV8313 three-phase gate driver, and a 3-pin motor connector. The `BLDCSystem` composite mates a 24-V supply board to the controller and a `BLDCMotor` cell into the controller's Hall-input and winding receptacles. The MCU reads the three Hall sensors over PC0/PC1/PC2 and asserts the six PWM gates on PD2..PD7 plus the three enables on PB0..PB2 to drive the windings in the right six-step sequence.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A wasted parts order — wrong connector mated

```python
# In BLDCSystem.__init__, perhaps a copy-paste typo mates the motor_plug
# into the Hall-input receptacle instead of the windings receptacle —
# or worse, mates motor_plug to hall_plug directly:
mate(self.motor_plug, self.hall_plug)

BLDCSystem()
# IncompatibleMateError: Header1xNMale mates with Header1xNFemale, not Header1xNMale
```

Both `motor_plug` and `hall_plug` are `Header1xNMale` — male plugs are not mate-partners of other male plugs. `mate()` checks `type(b) is type(a).MATES_WITH` before doing anything else, and refuses the moment the receiving class is wrong. The bench equivalent is a builder confidently pushing the motor's 3-pin plug into the cable that's supposed to go to the Hall sensor — except real connectors usually do go together physically, and the firmware just silently reads garbage from the wrong pins; with wirebench the typo gets caught at design time, before the wrong cable is ordered.

### Two phase outputs fighting

```python
# In BLDCControllerBoard.__init__, perhaps a "parallel two windings to
# get more torque" experiment ties two of the DRV8313's phase outputs
# together:
wire(self.drv.ports['OUT1'], self.drv.ports['OUT2'])

BLDCControllerBoard(refdes_number=1)
# ShortCircuitError: wire() has multiple drivers ('OUT1', 'OUT2') — short circuit
```

The DRV8313's `OUT1`, `OUT2`, `OUT3` are each `Direction.OUT, Analog` — the three independent half-bridges that switch each motor phase between V_M and GND. Tying any two together is precisely the same fault as the silicon's *shoot-through* failure mode (high-side and low-side of the same phase both conducting at once) — except wirebench catches the topology error before it becomes a thermal event. The bench equivalent is a smell of warm silicon, a deafeningly loud failed FET in the DRV's package, and a re-order of the controller IC.

## Running it

```bash
python demos/bldc_motor/bldc_motor.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports. The composed `BLDCSystem` gets its own set, and each board (`BLDCControllerBoard`, `BLDCSupplyBoard`) plus the Arduino sketch chip (`Uno_BLDCCommutator`) export as if they were complete designs in their own right:

- [`BLDCSystem.bom.csv`](docs/BLDCSystem.bom.csv), [`BLDCSystem.svg`](docs/BLDCSystem.svg), [`BLDCSystem.md`](docs/BLDCSystem.md), [`BLDCSystem.net`](docs/BLDCSystem.net), [`BLDCSystem.kicad_sch`](docs/BLDCSystem.kicad_sch), [`BLDCSystem.cir`](docs/BLDCSystem.cir), [`BLDCSystem.dot`](docs/BLDCSystem.dot), [`BLDCSystem.mmd`](docs/BLDCSystem.mmd), [`BLDCSystem.yosys.json`](docs/BLDCSystem.yosys.json), [`BLDCSystem.net-report.md`](docs/BLDCSystem.net-report.md), [`BLDCSystem.domain-report.md`](docs/BLDCSystem.domain-report.md), [`BLDCSystem.interface-report.md`](docs/BLDCSystem.interface-report.md) — composed assembly
- [`BLDCControllerBoard.bom.csv`](docs/BLDCControllerBoard.bom.csv), [`BLDCControllerBoard.svg`](docs/BLDCControllerBoard.svg), [`BLDCControllerBoard.md`](docs/BLDCControllerBoard.md), [`BLDCControllerBoard.net`](docs/BLDCControllerBoard.net), [`BLDCControllerBoard.kicad_sch`](docs/BLDCControllerBoard.kicad_sch), [`BLDCControllerBoard.cir`](docs/BLDCControllerBoard.cir), [`BLDCControllerBoard.dot`](docs/BLDCControllerBoard.dot), [`BLDCControllerBoard.mmd`](docs/BLDCControllerBoard.mmd), [`BLDCControllerBoard.yosys.json`](docs/BLDCControllerBoard.yosys.json), [`BLDCControllerBoard.net-report.md`](docs/BLDCControllerBoard.net-report.md), [`BLDCControllerBoard.domain-report.md`](docs/BLDCControllerBoard.domain-report.md), [`BLDCControllerBoard.interface-report.md`](docs/BLDCControllerBoard.interface-report.md) — controller PCB
- [`BLDCSupplyBoard.bom.csv`](docs/BLDCSupplyBoard.bom.csv), [`BLDCSupplyBoard.svg`](docs/BLDCSupplyBoard.svg), [`BLDCSupplyBoard.md`](docs/BLDCSupplyBoard.md), [`BLDCSupplyBoard.net`](docs/BLDCSupplyBoard.net), [`BLDCSupplyBoard.kicad_sch`](docs/BLDCSupplyBoard.kicad_sch), [`BLDCSupplyBoard.cir`](docs/BLDCSupplyBoard.cir), [`BLDCSupplyBoard.dot`](docs/BLDCSupplyBoard.dot), [`BLDCSupplyBoard.mmd`](docs/BLDCSupplyBoard.mmd), [`BLDCSupplyBoard.yosys.json`](docs/BLDCSupplyBoard.yosys.json), [`BLDCSupplyBoard.net-report.md`](docs/BLDCSupplyBoard.net-report.md), [`BLDCSupplyBoard.domain-report.md`](docs/BLDCSupplyBoard.domain-report.md), [`BLDCSupplyBoard.interface-report.md`](docs/BLDCSupplyBoard.interface-report.md) — supply PCB
- [`Uno_BLDCCommutator.bom.csv`](docs/Uno_BLDCCommutator.bom.csv), [`Uno_BLDCCommutator.svg`](docs/Uno_BLDCCommutator.svg), [`Uno_BLDCCommutator.md`](docs/Uno_BLDCCommutator.md), [`Uno_BLDCCommutator.net`](docs/Uno_BLDCCommutator.net), [`Uno_BLDCCommutator.kicad_sch`](docs/Uno_BLDCCommutator.kicad_sch), [`Uno_BLDCCommutator.cir`](docs/Uno_BLDCCommutator.cir), [`Uno_BLDCCommutator.dot`](docs/Uno_BLDCCommutator.dot), [`Uno_BLDCCommutator.mmd`](docs/Uno_BLDCCommutator.mmd), [`Uno_BLDCCommutator.yosys.json`](docs/Uno_BLDCCommutator.yosys.json), [`Uno_BLDCCommutator.net-report.md`](docs/Uno_BLDCCommutator.net-report.md), [`Uno_BLDCCommutator.domain-report.md`](docs/Uno_BLDCCommutator.domain-report.md), [`Uno_BLDCCommutator.interface-report.md`](docs/Uno_BLDCCommutator.interface-report.md) — MCU sketch subassembly

## Going further

- The source: [`bldc_motor.py`](bldc_motor.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
