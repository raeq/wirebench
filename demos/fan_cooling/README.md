# fan_cooling

A temperature-triggered cooling-fan module on its own PCB: a TMP302 die-temperature switch sees ambient temperature on its package, drives an SN74AHC1G14 Schmitt inverter that switches a low-side N-channel MOSFET grounding the fan's return leg. Power comes in on a 2-pin female header (`J1`), fans plug into another 2-pin female header (`J2`). The board is a composable `Board` — the top-of-file `CooledSystem` `Circuit` shows the intended composition: a power-source board mated to the fan-cooling board through their connectors.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A wasted parts order — wrong-pin-count power plug

```python
# In CooledSystem.__init__, perhaps the user grabbed an Arduino-style
# 3-pin power header from the parts drawer instead of the 2-pin one
# the FanCoolingBoard expects.  Replace the supply board's plug:
class WrongSupply(PowerSourceBoard):
    def __init__(self, *, refdes_number):
        self.vcc = Rail(True); self.gnd = Rail(False)
        self.plug = Header1xNMale(pin_count=3, pitch_mm=2.54, refdes_number=1)
        wire(self.vcc.ports['out'], self.plug.pins[0].internal)
        wire(self.gnd.ports['out'], self.plug.pins[1].internal)
        super(PowerSourceBoard, self).__init__(
            name='Wrong Supply', revision='A', refdes_number=refdes_number,
        )

supply = WrongSupply(refdes_number=1)
cooler = FanCoolingBoard(refdes_number=2)
mate(supply.connectors[0], cooler.connectors[0])
# PinCountMismatchError: Pin count mismatch: Header1xNMale has 3, Header1xNFemale has 2
```

`mate()` checks pin count before propagating per-pin connections; the board's 2-pin receptacle refuses the 3-pin plug. The bench equivalent is the order arriving from the parts house and the connector not physically going together — except the framework catches it at design time, before the order is placed.

### Two outputs fighting on the fan drive

```python
# Within FanCoolingBoard.__init__, perhaps a debug override that
# "forces the fan on for testing" gets left in:
wire(self.controller.ports['fan_drive'], Rail(True).out)

FanCoolingBoard(refdes_number=1)
# ShortCircuitError: wire() has multiple drivers ('fan_drive', 'out') — short circuit
```

The FanController's `fan_drive` is `Direction.OUT` — it's the only thing on that net allowed to assert a level. Tying it to a Rail's OUT puts two drivers on one node; `wire()` refuses inside the call. The bench equivalent is the controller's silicon trying to pull the FAN- net LOW while the rail clamps it HIGH — the controller's output stage saturates and dies of overcurrent.

## Running it

```bash
python demos/fan_cooling/fan_cooling.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports. The composed `CooledSystem` (supply board + cooling board) gets its own set, and the standalone `FanCoolingBoard` gets a separate set — each board exports as if it were a complete design:

- [`CooledSystem.bom.csv`](docs/CooledSystem.bom.csv), [`CooledSystem.svg`](docs/CooledSystem.svg), [`CooledSystem.md`](docs/CooledSystem.md), [`CooledSystem.net`](docs/CooledSystem.net), [`CooledSystem.cir`](docs/CooledSystem.cir), [`CooledSystem.dot`](docs/CooledSystem.dot), [`CooledSystem.mmd`](docs/CooledSystem.mmd), [`CooledSystem.yosys.json`](docs/CooledSystem.yosys.json), [`CooledSystem.net-report.md`](docs/CooledSystem.net-report.md), [`CooledSystem.domain-report.md`](docs/CooledSystem.domain-report.md), [`CooledSystem.interface-report.md`](docs/CooledSystem.interface-report.md) — the composed assembly
- [`FanCoolingBoard.bom.csv`](docs/FanCoolingBoard.bom.csv), [`FanCoolingBoard.svg`](docs/FanCoolingBoard.svg), [`FanCoolingBoard.md`](docs/FanCoolingBoard.md), [`FanCoolingBoard.net`](docs/FanCoolingBoard.net), [`FanCoolingBoard.cir`](docs/FanCoolingBoard.cir), [`FanCoolingBoard.dot`](docs/FanCoolingBoard.dot), [`FanCoolingBoard.mmd`](docs/FanCoolingBoard.mmd), [`FanCoolingBoard.yosys.json`](docs/FanCoolingBoard.yosys.json), [`FanCoolingBoard.net-report.md`](docs/FanCoolingBoard.net-report.md), [`FanCoolingBoard.domain-report.md`](docs/FanCoolingBoard.domain-report.md), [`FanCoolingBoard.interface-report.md`](docs/FanCoolingBoard.interface-report.md) — the standalone board
- [`PowerSourceBoard.bom.csv`](docs/PowerSourceBoard.bom.csv), [`PowerSourceBoard.svg`](docs/PowerSourceBoard.svg), [`PowerSourceBoard.md`](docs/PowerSourceBoard.md), [`PowerSourceBoard.net`](docs/PowerSourceBoard.net), [`PowerSourceBoard.cir`](docs/PowerSourceBoard.cir), [`PowerSourceBoard.dot`](docs/PowerSourceBoard.dot), [`PowerSourceBoard.mmd`](docs/PowerSourceBoard.mmd), [`PowerSourceBoard.yosys.json`](docs/PowerSourceBoard.yosys.json), [`PowerSourceBoard.net-report.md`](docs/PowerSourceBoard.net-report.md), [`PowerSourceBoard.domain-report.md`](docs/PowerSourceBoard.domain-report.md), [`PowerSourceBoard.interface-report.md`](docs/PowerSourceBoard.interface-report.md) — the example mating supply

## Going further

- The source: [`fan_cooling.py`](fan_cooling.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
