# water_alarm

A bench-style hysteresis alarm for a tank: two probes mounted at the low and high water marks, an open-collector sensor IC, a CMOS SR latch, and two indicator LEDs. Drop the probes into the tank; when the water reaches the low probe, the red LED latches on. When it reaches the high probe, the latch resets and the green LED takes over. Empty the tank past the low probe and the alarm re-arms — that's the hysteresis that keeps the LEDs from flickering as the water level wobbles.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A locked-up latch

```python
# In WaterAlarm.__init__, replace the inverter route from high probe
# to reset with a direct wire. Original two-wire route (replaced):
#   wire(self.sensor.out_2, self.sn74hc04.a_1, self.r_pu2.ports['t1'])
#   wire(self.sn74hc04.y_1, self.cd4043.r_1)
wire(self.sensor.out_2, self.cd4043.r_1, self.r_pu2.ports['t1'])

# Now evaluating the design with both probes dry:
d = WaterAlarm()
d(low_probe=0.0, high_probe=0.0)
# ForbiddenStateError: Invalid: S and R both active
```

The high-probe route deliberately runs through an inverter so the latch's Reset only asserts when the water *is* above the high mark (sensor LOW → inverted to HIGH on R). Skip the inverter and the bench reality is that both Set and Reset assert simultaneously whenever both probes are dry — exactly the forbidden NOR-latch state. The framework catches it at `evaluate()` because the `NORLatch` cell inside the CD4043 raises the moment its S and R inputs both drive HIGH. On the bench you'd see a latch in an undefined state — the LED behaviour would depend on which gate's propagation delay won the race.

### Two outputs fighting

```python
wire(self.cd4043.q_1, self.cd4069.y_1)
# ShortCircuitError: wire() has multiple drivers ('q_1', 'y_1') — short circuit
```

A typo joins the latch's Q output to the CMOS inverter's Y output — two CMOS output stages now drive the same net. One asserts HIGH, the other LOW; the silicon resolves it by whichever device sources or sinks more current, which is the same thing as "the chip that smokes first." `wire()` refuses inside the call itself, so the rest of the construction never runs. The bench equivalent is the smell of warm IC.

## Running it

```bash
python demos/water_alarm/water_alarm.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`WaterAlarm.bom.csv`](docs/WaterAlarm.bom.csv) — parts list
- [`WaterAlarm.md`](docs/WaterAlarm.md) — breadboard assembly guide
- [`WaterAlarm.net`](docs/WaterAlarm.net) — KiCad netlist
- [`WaterAlarm.cir`](docs/WaterAlarm.cir) — SPICE deck
- [`WaterAlarm.svg`](docs/WaterAlarm.svg) — rendered schematic
- [`WaterAlarm.dot`](docs/WaterAlarm.dot) — Graphviz source for the schematic
- [`WaterAlarm.mmd`](docs/WaterAlarm.mmd) — Mermaid flowchart
- [`WaterAlarm.yosys.json`](docs/WaterAlarm.yosys.json) — Yosys/netlistsvg JSON
- [`WaterAlarm.net-report.md`](docs/WaterAlarm.net-report.md) — every logical net, drivers, readers, domain
- [`WaterAlarm.domain-report.md`](docs/WaterAlarm.domain-report.md) — ground domains and isolation boundaries
- [`WaterAlarm.interface-report.md`](docs/WaterAlarm.interface-report.md) — public connector pins and their connections

## Going further

- The source: [`water_alarm.py`](water_alarm.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
