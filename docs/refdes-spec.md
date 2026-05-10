# REFDES Instance Attributes — Implementation Spec

## 1. Purpose

Give every physical component instance a **reference designator** ("refdes" — `R1`, `D3`, `U2`, etc.) so that the model can be exported to standards-compliant formats (SPICE, KiCad netlist, EDIF) and so that humans and downstream tools can refer to specific instances unambiguously.

Per IEEE 315 / ASME Y14.44 a refdes is `<class-prefix><integer>`. The **class prefix is a property of the component type** and is hard-coded per class. The **integer** is supplied by the author at construction time.

## 2. Scope

**In scope** — adding the `REFDES_PREFIX` class attribute to every leaf chip and passive class, accepting a refdes number at construction, exposing a read-only `refdes` property, and enforcing validation.

**Out of scope** — sidecar JSON persistence of refdes assignments; netlist exporters; auto-numbering / annotation; per-section refdes strings for multi-section devices (`U3A`, `U3B`, …) — exporters can synthesise those from the chip's refdes plus its internal channel index when they need them. The model itself stores only the chip's refdes.

## 3. Constraints carried over from CLAUDE.md

These are not negotiable and the implementation must respect every one of them:

- `__slots__` declared on every component — new instance state goes in `__slots__`.
- No setters. `refdes` is a **read-only property**. The backing field `_refdes_number` is assigned exactly once in `__init__` and never mutated thereafter.
- Refdes is *metadata*, not a signal. It must not appear in `__call__` and must not influence `evaluate()`.
- No inheritance between component types. The class-attribute prefix is declared on each leaf class directly; no base-class hierarchy for refdes purposes.

## 4. The reference-designator standard

IEEE 315 (graphic symbols, prefix letters) is the working reference; ASME Y14.44 (numbering conventions) supersedes IEEE 200. The list below is the full set of prefixes the codebase will recognise. Authors will choose from this list when adding new component classes; for the classes that already exist, the assignment in §5 is fixed.

| Prefix | Class of part                                          |
|--------|--------------------------------------------------------|
| `A`    | Assembly / sub-assembly                                |
| `AT`   | Attenuator                                             |
| `B`    | Motor (rotating machine)                               |
| `BT`   | Battery / cell                                         |
| `C`    | Capacitor                                              |
| `CB`   | Circuit breaker                                        |
| `D`    | Diode (rectifier, Zener, **LED**, photodiode, etc.)    |
| `DS`   | Display / indicator lamp                               |
| `F`    | Fuse                                                   |
| `FL`   | Filter                                                 |
| `G`    | Generator / power supply                               |
| `H`    | Hardware (screws, standoffs)                           |
| `HY`   | Circulator                                             |
| `J`    | Jack (chassis-side / female connector)                 |
| `K`    | Relay / contactor                                      |
| `L`    | Inductor                                               |
| `LS`   | Loudspeaker / buzzer                                   |
| `M`    | Meter                                                  |
| `MK`   | Microphone                                             |
| `P`    | Plug (cable-side / male connector)                     |
| `Q`    | Transistor (BJT, FET, IGBT — discrete)                 |
| `R`    | Resistor                                               |
| `RT`   | Thermistor                                             |
| `RV`   | Varistor / voltage-dependent resistor                  |
| `S`    | Switch (general)                                       |
| `SW`   | Switch (alternate, common in US schematics)            |
| `T`    | Transformer                                            |
| `TC`   | Thermocouple                                           |
| `TP`   | Test point                                             |
| `U`    | Integrated circuit / inseparable assembly              |
| `V`    | Vacuum tube / discharge device (also voltage source)   |
| `VR`   | Variable resistor / potentiometer                      |
| `W`    | Cable / wire harness                                   |
| `X`    | Socket (e.g. IC socket `XU3`)                          |
| `Y`    | Crystal / oscillator                                   |
| `Z`    | Zener (legacy — modern designs use `D`)                |

The implementation shall expose this set as a frozen set of strings in `framework/refdes.py` named `IEEE_315_PREFIXES` so that class-attribute values can be validated against it.

## 5. Prefix assignments for existing classes

These are fixed by the standard and must be encoded as `REFDES_PREFIX` class attributes on the listed classes:

| Class                                          | Prefix | Notes                                                     |
|------------------------------------------------|--------|-----------------------------------------------------------|
| `components.passives.resistor.Resistor`        | `R`    |                                                           |
| `components.passives.led.LED`                  | `D`    | LEDs are diodes; standard prefix is `D`, not `LED`.       |
| `components.chips.lm393.LM393`                 | `U`    |                                                           |
| `components.chips.sn74hc04.SN74HC04`           | `U`    |                                                           |
| `components.chips.cd4069.CD4069`               | `U`    |                                                           |
| `components.chips.cd4043.CD4043`               | `U`    |                                                           |
| `components.chips.uln2003a.ULN2003A`           | `U`    |                                                           |

Classes that **shall not** carry a refdes (no `REFDES_PREFIX`, constructor unchanged):

- `components.passives.rail.Rail` — represents a power net, not a part. Exports map this to a SPICE net name (`Vcc`, `GND`) or a power-flag symbol, not a refdes.
- `framework.ground.Ground` — same reasoning; this is net `0`.
- `framework.circuit.Circuit` and all its subclasses **other than** `framework.chip.Chip` — composites are hierarchy, not parts. `applications.water_alarm.WaterAlarm` is hierarchy and shall not have a refdes. (A `Chip` *is* a part: it gets a refdes.)
- **All cell concept classes** under `components.chips.concepts.` (`NORLatch`, `TriStateBuffer`, `Comparator`, `Inverter`, `DarlingtonChannel`) — cells are private chip implementation, never individually visible on a PCB. The enclosing chip carries the refdes; the cells inside it are nameless from a netlist perspective. If an exporter needs to refer to a specific channel of a chip (e.g. `U3A` for the second comparator of an LM393), it synthesises that string at export time from the chip's refdes plus the internal channel index — without storing it on the cell.

## 6. API surface

### 6.1 The class attribute

Each refdes-bearing class declares:

```python
REFDES_PREFIX: ClassVar[str] = 'R'   # or 'D', 'U', …
```

`REFDES_PREFIX` is a `ClassVar[str]` so it doesn't consume a `__slots__` entry. Validity (that the value is a member of `IEEE_315_PREFIXES`) is enforced at first instance construction by `validate_refdes()`. A class with an invalid prefix that is never instantiated is allowed to exist in the codebase but cannot be used.

### 6.2 The instance state

One new slot, added to every refdes-bearing class:

```python
__slots__ = (..., '_refdes_number')
```

- `_refdes_number: int` — positive integer, supplied at construction.

Assigned exactly once in `__init__` and never reassigned anywhere else in the class.

### 6.3 The constructor

Every refdes-bearing class gains one new keyword-only parameter at the **end** of its existing signature:

```python
def __init__(self, ..., *, refdes_number: int) -> None:
```

`refdes_number` is **mandatory** (no default). Authors must state the number explicitly — silent defaulting would defeat the deterministic-traceability requirement.

Existing positional parameters keep their positions; the new one is keyword-only by being placed after `*,`. This minimises churn in call sites.

### 6.4 The property

```python
@property
def refdes(self) -> str:
    return f"{self.REFDES_PREFIX}{self._refdes_number}"
```

Read-only. No setter. Returns a plain string suitable for direct emission into a netlist.

A convenience read-only property for exporters that want the parts separately:

```python
@property
def refdes_number(self) -> int: ...
```

This is optional but recommended; it avoids forcing exporters to parse the composite string.

### 6.5 `__repr__`

Update `__repr__` on each refdes-bearing class to include the refdes, **appended** to whatever state was previously emitted. The existing keyword (e.g. `ohms=`, `color=`, `lit=`, `out=`, `q=`, `y=`) is kept verbatim — only `refdes='R1'` is appended:

```python
def __repr__(self) -> str:
    return f"Resistor(ohms={self._ohms!r}, refdes={self.refdes!r})"
```

This makes test failures and interactive debugging surface the refdes immediately without changing the existing repr surface.

## 7. Validation

A shared helper lives in `framework/refdes.py`:

```python
IEEE_315_PREFIXES: frozenset[str] = frozenset({...})  # full table from §4

def validate_refdes(prefix: str, number: int) -> None:
    if prefix not in IEEE_315_PREFIXES:
        raise ValueError(f"Unknown refdes prefix {prefix!r}; not in IEEE 315.")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError(f"refdes_number must be a positive int; got {number!r}.")
```

Every refdes-bearing `__init__` calls `validate_refdes(self.REFDES_PREFIX, refdes_number)` **before** any other side effects. This keeps the failure mode loud and early.

`Circuit._validate` (in `framework/circuit.py`) gains an additional check: within a single composite, no two refdes-bearing children may have the **same** `(REFDES_PREFIX, refdes_number)` pair. Collisions raise `ValueError("Duplicate refdes: R1 used by Resistor and Resistor")` listing the offending classes.

The check walks `factor_nodes` of the composite. It only inspects nodes with a `REFDES_PREFIX` class attribute — chips and passives. Cells inside chips are skipped because they don't carry a refdes. (`Chip` is itself a `Circuit`, but its own `_validate` will see only its `Pin`s and refdes-less cells, so the duplicate check is automatically a no-op inside a chip.)

## 8. Multi-section devices

Internally, chips like `SN74HC04` (six inverters), `LM393` (two comparators), `ULN2003A` (seven Darlington channels), and `CD4043` (four NOR latches with tri-state buffers) compose multiple cell instances. **None of those cells carry a refdes** — only the chip does.

When an exporter needs to refer to a specific channel of a chip in a netlist (e.g. KiCad's per-section reference `U3A`), it synthesises that string at export time by combining the chip's refdes with the internal channel index. The chip class is responsible for exposing its channel structure to exporters; that is a separate work package and not part of this spec.

For the purposes of *this* spec: a `Chip` instance has one refdes string (`U3`), full stop. Section letters are an export concern, not a model concern.

## 9. File-by-file change list

New files:

- `src/framework/refdes.py` — `IEEE_315_PREFIXES`, `validate_refdes()`.

Modified files (add `REFDES_PREFIX` class attribute, extend `__slots__`, add `_refdes_number` and the `refdes` property, update `__init__`, call `validate_refdes`, update `__repr__`):

- `src/components/passives/resistor.py` — `REFDES_PREFIX = 'R'`.
- `src/components/passives/led.py` — `REFDES_PREFIX = 'D'`.
- `src/components/chips/lm393.py` — `REFDES_PREFIX = 'U'`.
- `src/components/chips/sn74hc04.py` — `REFDES_PREFIX = 'U'`.
- `src/components/chips/cd4069.py` — `REFDES_PREFIX = 'U'`.
- `src/components/chips/cd4043.py` — `REFDES_PREFIX = 'U'`.
- `src/components/chips/uln2003a.py` — `REFDES_PREFIX = 'U'`.
- `src/framework/circuit.py` — extend `_validate` with duplicate-refdes detection over refdes-bearing children only.
- `src/applications/water_alarm.py` — no `REFDES_PREFIX` (it is hierarchy); however, all of its refdes-bearing **children** now require explicit `refdes_number=` at construction. Update its `__init__` to supply numbers in source-code order. The exact assignment is the author's decision per design.

Unmodified:

- `src/components/passives/rail.py` — no refdes.
- `src/framework/ground.py` — no refdes.
- `src/components/chips/concepts/*.py` — cells don't carry refdes; constructors unchanged.
- `src/framework/factor.py`, `port.py`, `pin.py`, `wire.py`, `node.py`, `signals.py`, `units.py` — refdes lives on components, not on framework primitives.
- `src/framework/chip.py` — `Chip` is abstract and does not store refdes itself; each concrete chip subclass declares its own `REFDES_PREFIX = 'U'` and `__slots__` additions. (The alternative — moving `_refdes_number` into `Chip.__slots__` — would push refdes state into the framework layer for one of two component families and leave passives inconsistent. Keep it on the leaf classes.)

## 10. Test plan

Add a new test module `tests/framework/test_refdes.py` with at minimum:

1. **Happy path, leaf passive.** `Resistor(330, refdes_number=1).refdes == 'R1'`.
2. **Happy path, LED prefix is D not LED.** `LED('red', refdes_number=2).refdes == 'D2'`.
3. **Happy path, chip.** `SN74HC04(refdes_number=3).refdes == 'U3'`.
4. **Missing refdes_number rejected.** `Resistor(330)` raises `TypeError` (missing required keyword arg).
5. **Non-positive number rejected.** `Resistor(330, refdes_number=0)` raises `ValueError`; same for `-1`, `1.0`, `True`, `'1'`.
6. **Unknown prefix rejected at instantiation.** A test subclass with `REFDES_PREFIX = 'XX'` triggers a `ValueError` when constructed.
7. **Read-only property.** Setting `r.refdes = 'R9'` raises `AttributeError`.
8. **Cells do not accept refdes_number.** `NORLatch(refdes_number=1)` raises `TypeError` (unexpected keyword arg) — proves cells are nameless at the model level.
9. **Cells have no `REFDES_PREFIX`.** `assert not hasattr(NORLatch, 'REFDES_PREFIX')` for each cell concept class.
10. **Duplicate refdes detected by Circuit._validate.** A composite containing two `Resistor(refdes_number=1)` instances raises `ValueError` on construction, citing both classes.
11. **Different prefixes with same number do not collide.** `R1` and `D1` and `U1` co-exist in one composite without issue.
12. **`__repr__` includes refdes.** `'R1'` appears in `repr(Resistor(330, refdes_number=1))`, and the existing keyword (`ohms=`) is preserved.

Existing tests will need updating to pass `refdes_number=` to every constructed refdes-bearing component. The migration is mechanical: walk every `Resistor(...)`, `LED(...)`, `SN74HC04(...)`, `CD4043(...)`, etc., in `tests/` and in `src/applications/` and append the keyword. Choose numbers in source-code order; each test fixture's numbering is local to that test. Cell concept tests (`tests/components/test_inverter.py`, `test_nor_latch.py`, etc.) are not affected.

## 11. Acceptance criteria

The work is done when:

1. `python -m pytest` passes with the new and existing tests.
2. Every refdes-bearing class (chips + passives) has a `REFDES_PREFIX` class attribute that appears in `IEEE_315_PREFIXES`.
3. Every refdes-bearing class declares `_refdes_number` in `__slots__`, accepts it in `__init__`, and exposes the `refdes` read-only property.
4. `validate_refdes` is called from every refdes-bearing `__init__` before any other side effects.
5. `Circuit._validate` detects duplicate `(prefix, number)` pairs within a single composite, walking only refdes-bearing children.
6. Cells (concepts) carry no refdes — no `REFDES_PREFIX` class attribute, no `refdes_number` constructor arg, no `refdes` property.
7. `WaterAlarm` and all its tests construct without errors and produce a coherent set of refdes (no duplicates, all numbered).
8. No setters, no public mutators, no convenience methods bypass the existing signal-path discipline.
9. No new positional parameters introduced — `refdes_number` is keyword-only.

## 12. Out of scope (for follow-up work packages)

- **Sidecar JSON persistence.** Stable refdes assignments across renames/reorderings, stored alongside the design.
- **Auto-annotation.** A traversal that fills in missing `refdes_number`s in deterministic order. The current spec requires explicit author-supplied numbers.
- **Netlist exporters.** SPICE, KiCad, EDIF emitters that consume `refdes` are separate work packages. Per-section reference strings (`U3A`, `U3B`, …) for multi-section devices are synthesised at export time by combining the chip's refdes with the channel index — the model does not store them.
- **Renumbering / collision repair.** No tool to renumber after the fact; collisions are user-fixed.
- **Pin number metadata.** SPICE/KiCad need pin *numbers* (1, 2, 3 …) on chip pins; today the codebase only has pin *names* (`a_1`, `y_2`, …). That mapping is a separate concern.
