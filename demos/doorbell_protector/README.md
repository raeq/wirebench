# doorbell_protector

A two-stage relay protector for a doorbell button: press the button once and a 5-second bell-pulse timer fires the relay, then a 50-second lock-out timer holds the bell off no matter how hard the visitor mashes the switch. Build it inline with an existing doorbell and the bell rings once per minute at most, regardless of pranksters. Two LM555 monostables, a relay, a flyback diode across the coil, and a status LED.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### Two outputs fighting

```python
# In DoorbellProtector.__init__, tie the two timer outputs together
# (perhaps intending to "merge the bell signal" before the relay):
wire(self.ic1.OUT, self.ic2.OUT)

DoorbellProtector()
# ShortCircuitError: wire() has multiple drivers ('OUT', 'OUT') — short circuit
```

IC1's OUT is the bell-pulse signal; IC2's OUT is the lock-out gate. Both are `Direction.OUT` on the NE555 model, and one of them sources HIGH for five seconds while the other sources HIGH for fifty — `wire()` refuses inside the call before construction can finish. The bench equivalent is two CMOS push-pull stages fighting on one trace; the first device to fail sinks the loser's current.

### A floating relay-coil low side

```python
# A well-intentioned "fix": tie the relay's coil_minus, T1's collector,
# and the flyback diode's anode together — they look like they ought to
# share a net.  But nothing on that net is a driver in the model: T1 is
# opaque under graph evaluation, D1 is a passive, and coil_minus is
# BIDIR.  Add to DoorbellProtector.__init__:
wire(self.relay.coil_minus, self.t1.c, self.d1.anode)

DoorbellProtector()
# FloatingNetError: Floating logical net — multiple passive BIDIRs with no driver: 'D1N4007.anode', 'Relay_SPDT.coil_minus', 'BC548.c'
```

The real design deliberately leaves coil_minus, T1's collector, and D1's anode on three separate one-port nets — the physical wires exist, but in the framework's voltage-only graph the transistor is opaque, so there's no driver to propagate through that node. Join them and the framework's logical-net walker visits the new three-port net at `super().__init__()`, finds only passive BIDIRs, and refuses to construct. The bench equivalent is a relay that clicks correctly *until* a back-EMF spike from one of those silent shifts in T1's saturation propagates through the now-shared node and bricks the timer chips.

## Running it

```bash
python demos/doorbell_protector/doorbell_protector.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports:

- [`DoorbellProtector.bom.csv`](docs/DoorbellProtector.bom.csv) — parts list
- [`DoorbellProtector.md`](docs/DoorbellProtector.md) — breadboard assembly guide
- [`DoorbellProtector.net`](docs/DoorbellProtector.net) — KiCad netlist
- [`DoorbellProtector.kicad_sch`](docs/DoorbellProtector.kicad_sch) — KiCad schematic, open in Eeschema 9.x
- [`DoorbellProtector.cir`](docs/DoorbellProtector.cir) — SPICE deck
- [`DoorbellProtector.svg`](docs/DoorbellProtector.svg) — rendered schematic
- [`DoorbellProtector.dot`](docs/DoorbellProtector.dot) — Graphviz source for the schematic
- [`DoorbellProtector.mmd`](docs/DoorbellProtector.mmd) — Mermaid flowchart
- [`DoorbellProtector.yosys.json`](docs/DoorbellProtector.yosys.json) — Yosys/netlistsvg JSON
- [`DoorbellProtector.net-report.md`](docs/DoorbellProtector.net-report.md) — every logical net, drivers, readers, domain
- [`DoorbellProtector.domain-report.md`](docs/DoorbellProtector.domain-report.md) — ground domains and isolation boundaries
- [`DoorbellProtector.interface-report.md`](docs/DoorbellProtector.interface-report.md) — public connector pins and their connections

## Going further

- The source: [`doorbell_protector.py`](doorbell_protector.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
