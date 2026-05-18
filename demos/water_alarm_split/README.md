# water_alarm_split

The same hysteresis-driven water-level alarm as `water_alarm/`, but split across two physical PCBs that mate through a 40-pin Raspberry-Pi-style GPIO header pair. The `SensorBoard` carries the ULN2003A and exposes conditioned probe outputs over the header; the `ControllerBoard` carries the SR latch, the inverter chips, the LEDs, and the rails, and consumes the conditioned signals over the matching header. The `WaterAlarmAssembly` `Circuit` `mate()`s the two boards together — this is the canonical HAT pattern for wirebench, and the demo where the connector-mating physics gets stressed.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A wasted parts order — wrong HAT pin count

```python
# In WaterAlarmAssembly.__init__, perhaps a user re-purposes a smaller
# 2x8 (16-pin) HAT carrier they had lying around for the controller
# board.  In ControllerBoard.__init__, replace the 40-pin header with:
self.connector = Header2xNMale(pin_count=16, pitch_mm=2.54, refdes_number=1)

WaterAlarmAssembly()
# PinCountMismatchError: Pin count mismatch: Header2xNFemale has 40, Header2xNMale has 16
```

`mate()` checks pin count before propagating per-pin connections. The bench equivalent is the order arriving and the 16-pin male physically not reaching the matching positions on the 40-pin female — except the framework catches it at design time, when the BOM still has time to be corrected before the parts ship.

### A wasted parts order — wrong connector family

```python
# In ControllerBoard.__init__, perhaps a user grabs a JST PH cable
# housing from the parts drawer thinking it'll fit the HAT slot:
from components.connectors.jst_ph import JSTPHCableHousing
self.connector = JSTPHCableHousing(pin_count=4, refdes_number=1)

WaterAlarmAssembly()
# IncompatibleMateError: Header2xNFemale mates with Header2xNMale, not JSTPHCableHousing
```

`mate()` checks the connector family — every connector class registers exactly one mating partner via `declare_mating_pair()`, and any other family is refused. The bench equivalent is the JST cable physically not going into the 0.1"-pitch HAT slot at all — but the framework refuses to model the design that way, which means the BOM never lists the wrong part.

## Running it

```bash
python demos/water_alarm_split/water_alarm_split.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports. The composed `WaterAlarmAssembly` gets a set, and each board (`SensorBoard`, `ControllerBoard`) gets its own per-board set — the framework treats each board as if it were a complete design, so per-board exports go to the EE shop that fabricates each board separately:

- [`ControllerBoard.bom.csv`](docs/ControllerBoard.bom.csv), [`ControllerBoard.svg`](docs/ControllerBoard.svg), [`ControllerBoard.md`](docs/ControllerBoard.md), [`ControllerBoard.net`](docs/ControllerBoard.net), [`ControllerBoard.kicad_sch`](docs/ControllerBoard.kicad_sch), [`ControllerBoard.cir`](docs/ControllerBoard.cir), [`ControllerBoard.dot`](docs/ControllerBoard.dot), [`ControllerBoard.mmd`](docs/ControllerBoard.mmd), [`ControllerBoard.yosys.json`](docs/ControllerBoard.yosys.json), [`ControllerBoard.net-report.md`](docs/ControllerBoard.net-report.md), [`ControllerBoard.domain-report.md`](docs/ControllerBoard.domain-report.md), [`ControllerBoard.interface-report.md`](docs/ControllerBoard.interface-report.md) — controller PCB
- [`SensorBoard.bom.csv`](docs/SensorBoard.bom.csv), [`SensorBoard.svg`](docs/SensorBoard.svg), [`SensorBoard.md`](docs/SensorBoard.md), [`SensorBoard.net`](docs/SensorBoard.net), [`SensorBoard.kicad_sch`](docs/SensorBoard.kicad_sch), [`SensorBoard.cir`](docs/SensorBoard.cir), [`SensorBoard.dot`](docs/SensorBoard.dot), [`SensorBoard.mmd`](docs/SensorBoard.mmd), [`SensorBoard.yosys.json`](docs/SensorBoard.yosys.json), [`SensorBoard.net-report.md`](docs/SensorBoard.net-report.md), [`SensorBoard.domain-report.md`](docs/SensorBoard.domain-report.md), [`SensorBoard.interface-report.md`](docs/SensorBoard.interface-report.md) — sensor PCB
- [`WaterAlarmAssembly.bom.csv`](docs/WaterAlarmAssembly.bom.csv), [`WaterAlarmAssembly.svg`](docs/WaterAlarmAssembly.svg), [`WaterAlarmAssembly.md`](docs/WaterAlarmAssembly.md), [`WaterAlarmAssembly.net`](docs/WaterAlarmAssembly.net), [`WaterAlarmAssembly.kicad_sch`](docs/WaterAlarmAssembly.kicad_sch), [`WaterAlarmAssembly.cir`](docs/WaterAlarmAssembly.cir), [`WaterAlarmAssembly.dot`](docs/WaterAlarmAssembly.dot), [`WaterAlarmAssembly.mmd`](docs/WaterAlarmAssembly.mmd), [`WaterAlarmAssembly.yosys.json`](docs/WaterAlarmAssembly.yosys.json), [`WaterAlarmAssembly.net-report.md`](docs/WaterAlarmAssembly.net-report.md), [`WaterAlarmAssembly.domain-report.md`](docs/WaterAlarmAssembly.domain-report.md), [`WaterAlarmAssembly.interface-report.md`](docs/WaterAlarmAssembly.interface-report.md) — combined assembly

## Going further

- The source: [`water_alarm_split.py`](water_alarm_split.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
