# penfold_crystal_set

A passive-only MW (medium-wave) crystal radio.  The whole receiver
runs on the tens of microwatts of RF energy the antenna picks up
from the local broadcast band — there is **no battery and no power
rail anywhere in the design**.  Faithful to R. A. Penfold's BP107
Project 27 (pages 131–134, Fig. 62 / 63).

The teaching point: **passive-only topology with environment-fed
energy.**  This demo is the framework's *boundary-case probe*: can
a Circuit construct without any declared `Rail`?  The answer is
yes — the wirebench catalogue's new `Antenna` and `Earth` classes
make environment-fed topology expressible without forcing a fake
power-supply Rail into the BOM.

The targeted topology test (`test_zero_rails`) asserts the canonical
*passive-only* property: zero `Rail` instances in the circuit.  If
the framework's expression surface were too narrow to admit such a
design, this test would fail and the failure itself would document
the gap (matching the Phase-2.7 *dynamically_driven* shape from the
P8 one-second-timer).  It doesn't fail — the framework reaches that
far.

## What this design is protected from

### Forgetting the antenna or the earth

```python
class BrokenCrystalSet(Circuit):
    def __init__(self) -> None:
        # ... LC tank, diode, earpiece declared ...
        # Forgot to declare an Antenna or Earth.
        wire(self.l1.t1, self.vc1.t1, self.d1.anode)
        wire(self.l1.t2, self.vc1.t2)   # nowhere for the return
        super().__init__()

BrokenCrystalSet()
# FloatingNetError: Floating logical net — multiple passive BIDIRs
#                  with no driver: 'FerriteAerial.t1', 'D_OA90.anode',
#                  'VariableCapacitor.t1'
```

The crystal set needs *both* an Antenna (signal source) and an
Earth (return path).  Either one missing means the LC tank has no
defined potential to resonate against; wirebench refuses to
construct the design because the resulting nets are floating BIDIR
clusters with no driver.  The framework can't *know* the missing
component is specifically an antenna or earth, but the error names
the floating net so the fix is obvious.

### Picking a silicon diode instead of germanium

```python
# Substituted a 1N4148 for the OA90 — looks the same physically:
self.d1 = D1N4148(refdes_number=1)   # silicon V_F ~0.7 V
# Bench symptom: silence.  The microvolts of antenna signal can't
# forward-bias a silicon junction; the diode never conducts.
```

Wirebench accepts the substitution (both classes have the same port
shape and a 1N4148 is electrically valid as a diode).  The catch is
in the parts catalogue: the OA90's `V_F = 0.2` and the 1N4148's
`V_F = 0.7` are class metadata; running the design through the
parts CLI surfaces the difference, and the assembly-guide
explicitly notes germanium-not-silicon as a P27 requirement.  This
is one of the *not-mechanical-but-electrical* mistakes wirebench
flags through documentation rather than through hard validation.

## Running it

```bash
python demos/penfold_crystal_set/penfold_crystal_set.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated
exports:

- [`CrystalSet.bom.csv`](docs/CrystalSet.bom.csv) — parts list
- [`CrystalSet.md`](docs/CrystalSet.md) — breadboard assembly guide
- [`CrystalSet.breadboard.svg`](docs/CrystalSet.breadboard.svg) — breadboard layout
- [`CrystalSet.net`](docs/CrystalSet.net) — KiCad netlist
- [`CrystalSet.kicad_sch`](docs/CrystalSet.kicad_sch) — KiCad schematic
- [`CrystalSet.cir`](docs/CrystalSet.cir) — SPICE deck
- [`CrystalSet.svg`](docs/CrystalSet.svg) — rendered schematic
- [`CrystalSet.dot`](docs/CrystalSet.dot) — Graphviz source
- [`CrystalSet.mmd`](docs/CrystalSet.mmd) — Mermaid flowchart
- [`CrystalSet.yosys.json`](docs/CrystalSet.yosys.json) — Yosys JSON
- [`CrystalSet.net-report.md`](docs/CrystalSet.net-report.md) — every logical net
- [`CrystalSet.domain-report.md`](docs/CrystalSet.domain-report.md) — ground domains
- [`CrystalSet.interface-report.md`](docs/CrystalSet.interface-report.md) — public ports

## Going further

- The source: [`penfold_crystal_set.py`](penfold_crystal_set.py)
- The book: R. A. Penfold, *30 Solderless Breadboard Projects, Book 1*,
  Bernard Babani Publishing, October 1982 (ISBN 0 85934 082 1) — pages
  131–134 (text), Fig. 62 (schematic), Fig. 63 (layout).
- The full ordered list of all demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
