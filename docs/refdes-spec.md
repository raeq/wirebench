# REFDES Instance Attributes — Implementation Spec

## 1. Purpose

Give every physical component instance a **reference designator** ("refdes" — `R1`, `D3`, `U2A`, etc.) so that the model can be exported to standards-compliant formats (SPICE, KiCad netlist, EDIF) and so that humans and downstream tools can refer to specific instances unambiguously.

Per IEEE 315 / ASME Y14.44 a refdes is `<class-prefix><integer>[<section-letter>]`. The **class prefix is a property of the component type** and is hard-coded per class. The **integer** is supplied by the author at construction time. The **section letter** is supplied by a parent chip when wiring a multi-section device.

## 2. Scope

**In scope** — adding the `REFDES_PREFIX` class attribute to every leaf component class, accepting a refdes number (and optional section letter) at construction, exposing a read-only `refdes` property, and enforcing validation.

**Out of scope** — sidecar JSON persistence of refdes assignments (separate work package). Netlist exporters (separate work package). Auto-numbering / annotation (separate work package).

## 3. Constraints carried over from CLAUDE.md

These are not negotiable and the implementation must respect every one of them:

- `__slots__` declared on every component — new instance state goes in `__slots__`.
- No setters. `refdes` is a **read-only property**. The backing fields `_refdes_number` and `_refdes_section` are assigned exactly once in `__init__` and never mutated thereafter.
- Refdes is *metadata*, not a signal. It must not appear in `__call__` and must not influence `evaluate()`.
- No inheritance between component types. The class-attribute prefix is declared on each leaf class directly; do not introduce a base class hierarchy for refdes purposes.

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
| `components.chips.concepts.inverter.Inverter`         | `U` (inherited via section) | See §8.        |
| `components.chips.concepts.comparator.Comparator`     | `U` (inherited via section) | See §8.        |
| `components.chips.concepts.nor_latch.NorLatch`        | `U` (inherited via section) | See §8.        |
| `components.chips.concepts.tristate_buffer.TristateBuffer` | `U` (inherited via section) | See §8.    |
| `components.chips.concepts.darlington_channel.DarlingtonChannel` | `U` (inherited via section) | See §8. |

Classes that **shall not** carry a refdes (no `REFDES_PREFIX`, constructor unchanged):

- `components.passives.rail.Rail` — represents a power net, not a part. Exports map this to a SPICE net name (`Vcc`, `GND`) or a power-flag symbol, not a refdes.
- `framework.ground.Ground` — same reasoning; this is net `0`.
- `framework.circuit.Circuit` and all its subclasses **other than** `framework.chip.Chip` — composites are hierarchy, not parts. `applications.water_alarm.WaterAlarm` is hierarchy and shall not have a refdes. (A `Chip` *is* a part: it gets a refdes.)

## 6. API surface

### 6.1 The class attribute

Each leaf-component class that participates in refdes assignment declares:

```python
REFDES_PREFIX: ClassVar[str] = 'R'   # or 'D', 'U', …
```

`REFDES_PREFIX` is a `ClassVar[str]` so it doesn't consume a `__slots__` entry. The implementation must `assert REFDES_PREFIX in IEEE_315_PREFIXES` at import time (a module-level check inside `framework/refdes.py` that iterates registered classes is acceptable; otherwise enforce per-class in tests).

### 6.2 The instance state

Two new slots, added to every refdes-bearing class:

```python
__slots__ = (..., '_refdes_number', '_refdes_section')
```

- `_refdes_number: int` — positive integer, supplied at construction.
- `_refdes_section: str | None` — single uppercase letter `A`–`Z`, or `None` if the part is not a section of a multi-section device.

Both are assigned exactly once in `__init__` and never reassigned anywhere else in the class.

### 6.3 The constructor

Every refdes-bearing class gains two new keyword-only parameters at the **end** of its existing signature:

```python
def __init__(self, ..., *, refdes_number: int, refdes_section: str | None = None) -> None:
```

`refdes_number` is **mandatory** (no default). Authors must state the number explicitly — silent defaulting would defeat the deterministic-traceability requirement.

`refdes_section` is optional and defaults to `None`. It is supplied only by a parent chip when it constructs its internal cells (§8).

Existing positional parameters keep their positions; the new ones are keyword-only by being placed after `*,`. This minimises churn in call sites for now — a follow-up may make the keyword-only boundary stricter if needed.

### 6.4 The property

```python
@property
def refdes(self) -> str:
    if self._refdes_section is None:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"
    return f"{self.REFDES_PREFIX}{self._refdes_number}{self._refdes_section}"
```

Read-only. No setter. Returns a plain string suitable for direct emission into a netlist.

Two convenience read-only properties for exporters that want the parts separately:

```python
@property
def refdes_number(self) -> int: ...
@property
def refdes_section(self) -> str | None: ...
```

These are optional but recommended; they avoid forcing exporters to parse the composite string.

### 6.5 `__repr__`

Update `__repr__` on each refdes-bearing class to include the refdes, e.g.:

```python
def __repr__(self) -> str:
    return f"Resistor(R={self._ohms!r}, refdes={self.refdes!r})"
```

This makes test failures and interactive debugging surface the refdes immediately.

## 7. Validation

A shared helper lives in `framework/refdes.py`:

```python
IEEE_315_PREFIXES: frozenset[str] = frozenset({...})  # full table from §4

def validate_refdes(prefix: str,
                    number: int,
                    section: str | None) -> None:
    if prefix not in IEEE_315_PREFIXES:
        raise ValueError(f"Unknown refdes prefix {prefix!r}; not in IEEE 315.")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise ValueError(f"refdes_number must be a positive int; got {number!r}.")
    if section is not None:
        if not (isinstance(section, str) and len(section) == 1
                and 'A' <= section <= 'Z'):
            raise ValueError(
                f"refdes_section must be a single uppercase A–Z letter or None; "
                f"got {section!r}."
            )
```

Every refdes-bearing `__init__` calls `validate_refdes(self.REFDES_PREFIX, refdes_number, refdes_section)` **before** any other side effects. This keeps the failure mode loud and early.

`Circuit._validate` (in `framework/circuit.py`) gains an additional check: within a single composite, no two refdes-bearing children may have the **same** `(REFDES_PREFIX, refdes_number, refdes_section)` triple. Collisions raise `ValueError("Duplicate refdes: R1 used by Resistor and Resistor")` listing the offending classes. Multi-section devices (§8) are excluded from this check by design — their internal sections share `(prefix, number)` but differ on `section`.

## 8. Multi-section devices

`SN74HC04` is the canonical case: one chip, six `Inverter` sections, refdes `U2A` … `U2F`. The implementation rule:

A `Chip` subclass that contains `N` internal cells of one concept class must:

1. Accept its own `refdes_number` as a keyword-only constructor argument.
2. When constructing each cell, pass `refdes_number=self._refdes_number` and `refdes_section=chr(ord('A') + i)` for `i` in `range(N)`.
3. Pass `refdes_section=None` to itself (the chip-level refdes is `U2`, not `U2A`).

Concrete chip-by-chip section assignments:

| Chip       | Cell class           | Count | Sections          |
|------------|----------------------|-------|-------------------|
| `SN74HC04` | `Inverter`           | 6     | `A`–`F`           |
| `CD4069`   | `Inverter`           | 6     | `A`–`F`           |
| `LM393`    | `Comparator`         | 2     | `A`, `B`          |
| `CD4043`   | `NorLatch` (+ TS buf)| 4     | `A`–`D`           |
| `ULN2003A` | `DarlingtonChannel`  | 7     | `A`–`G`           |

Where a chip composes more than one concept (e.g. `CD4043` mixes a `NorLatch` with a `TristateBuffer` per channel), the section letter is per **channel**, applied to both internal cells of that channel — `U3A` may refer to either the latch or the buffer of channel A, disambiguated by context in the netlist. The `Chip` subclass is responsible for assigning identical section letters to the cells that constitute one logical channel.

The cell classes (`Inverter`, `Comparator`, `NorLatch`, `TristateBuffer`, `DarlingtonChannel`) **require** `refdes_number` and accept the optional `refdes_section`. They may be instantiated standalone in tests with `refdes_section=None`, in which case their refdes is e.g. `U7` rather than `U7A`.

## 9. File-by-file change list

New files:

- `src/framework/refdes.py` — `IEEE_315_PREFIXES`, `validate_refdes()`.

Modified files (add `REFDES_PREFIX` class attribute, extend `__slots__`, add `_refdes_number` / `_refdes_section` and the property, update `__init__`, call `validate_refdes`, update `__repr__`):

- `src/components/passives/resistor.py` — `REFDES_PREFIX = 'R'`.
- `src/components/passives/led.py` — `REFDES_PREFIX = 'D'`.
- `src/components/chips/lm393.py` — `REFDES_PREFIX = 'U'`; thread section letters to comparators.
- `src/components/chips/sn74hc04.py` — `REFDES_PREFIX = 'U'`; thread section letters `A`–`F` to inverters.
- `src/components/chips/cd4069.py` — `REFDES_PREFIX = 'U'`; thread section letters `A`–`F` to inverters.
- `src/components/chips/cd4043.py` — `REFDES_PREFIX = 'U'`; thread section letters `A`–`D` to latch+tristate-buffer pairs.
- `src/components/chips/uln2003a.py` — `REFDES_PREFIX = 'U'`; thread section letters `A`–`G` to Darlington channels.
- `src/components/chips/concepts/inverter.py` — `REFDES_PREFIX = 'U'`; accept `refdes_number`, optional `refdes_section`.
- `src/components/chips/concepts/comparator.py` — same.
- `src/components/chips/concepts/nor_latch.py` — same.
- `src/components/chips/concepts/tristate_buffer.py` — same.
- `src/components/chips/concepts/darlington_channel.py` — same.
- `src/framework/circuit.py` — extend `_validate` with duplicate-refdes detection (skipping section collisions on the same `(prefix, number)`).
- `src/applications/water_alarm.py` — no `REFDES_PREFIX` (it is hierarchy); however, all of its **children** now require explicit `refdes_number=` at construction. Update its `__init__` to supply numbers in source-code order (`Resistor(refdes_number=1)`, `LED(refdes_number=1)`, `SN74HC04(refdes_number=1)`, etc.). The exact assignment is the author's decision per design.

Unmodified:

- `src/components/passives/rail.py` — no refdes.
- `src/framework/ground.py` — no refdes.
- `src/framework/factor.py`, `port.py`, `pin.py`, `wire.py`, `node.py`, `signals.py`, `units.py` — refdes lives on components, not on framework primitives.
- `src/framework/chip.py` — `Chip` is abstract and does not store refdes itself; each concrete chip subclass declares its own `REFDES_PREFIX = 'U'` and `__slots__` additions. (The alternative — moving `_refdes_number`/`_refdes_section` into `Chip.__slots__` — would push refdes state into the framework layer for one of two component families and leave passives inconsistent. Keep it on the leaf classes.)

## 10. Test plan

Add a new test module `tests/framework/test_refdes.py` with at minimum:

1. **Happy path, leaf component.** `Resistor(330, refdes_number=1).refdes == 'R1'`.
2. **Happy path, LED prefix is D not LED.** `LED('red', refdes_number=2).refdes == 'D2'`.
3. **Missing refdes_number rejected.** `Resistor(330)` raises `TypeError` (missing required keyword arg).
4. **Non-positive number rejected.** `Resistor(330, refdes_number=0)` raises `ValueError`; same for `-1`, `1.0`, `True`, `'1'`.
5. **Bad section rejected.** `Inverter(refdes_number=1, refdes_section='aa')` and `'a'` and `'1'` and `''` all raise `ValueError`. `None` is accepted.
6. **Unknown prefix at class definition rejected.** A test subclass with `REFDES_PREFIX = 'XX'` triggers a `ValueError` when `validate_refdes` runs on construction.
7. **Read-only property.** Setting `r.refdes = 'R9'` raises `AttributeError`; same for `r._refdes_number = 9` against `__slots__` immutability rules (assignment is allowed by Python on slot fields — the test asserts the *property* is read-only and documents the convention that backing fields are written once).
8. **Multi-section device assigns sections.** Construct `SN74HC04(refdes_number=3)`. Assert that `chip.refdes == 'U3'`, `chip._gates[0].refdes == 'U3A'`, …, `chip._gates[5].refdes == 'U3F'`.
9. **Duplicate refdes detected by Circuit._validate.** A composite containing two `Resistor(refdes_number=1)` instances raises `ValueError` on construction, citing both classes.
10. **Sections on the same chip don't collide.** `U3A` and `U3B` inside one `SN74HC04` do *not* trigger the duplicate check.
11. **Standalone cell with no section.** `Inverter(refdes_number=7).refdes == 'U7'` (no trailing letter).
12. **`__repr__` includes refdes.** `'R1'` appears in `repr(Resistor(330, refdes_number=1))`.

Existing tests will need updating to pass `refdes_number=` to every constructed component. The migration is mechanical: walk every `Resistor(...)`, `LED(...)`, `SN74HC04(...)`, etc., in `tests/` and in `src/applications/` and append the keyword. Choose numbers in source-code order; each test fixture's numbering is local to that test.

## 11. Acceptance criteria

The work is done when:

1. `python -m pytest` passes with the new and existing tests.
2. Every refdes-bearing class has a `REFDES_PREFIX` class attribute that appears in `IEEE_315_PREFIXES`.
3. Every refdes-bearing class declares `_refdes_number` and `_refdes_section` in `__slots__`, accepts them in `__init__`, and exposes the `refdes` read-only property.
4. `validate_refdes` is called from every refdes-bearing `__init__` before any side effects.
5. `Circuit._validate` detects duplicate `(prefix, number, section)` triples within a single composite.
6. `WaterAlarm` and all its tests construct without errors and produce a coherent set of refdes (no duplicates, all numbered).
7. No setters, no public mutators, no convenience methods bypass the existing signal-path discipline.
8. No new positional parameters introduced — `refdes_number` and `refdes_section` are keyword-only.

## 12. Out of scope (for follow-up work packages)

- **Sidecar JSON persistence.** Stable refdes assignments across renames/reorderings, stored alongside the design.
- **Auto-annotation.** A traversal that fills in missing refdes_numbers in deterministic order. The current spec requires explicit author-supplied numbers.
- **Netlist exporters.** SPICE, KiCad, EDIF emitters that consume `refdes` are separate work packages.
- **Renumbering / collision repair.** No tool to renumber after the fact; collisions are user-fixed.
- **Pin number metadata.** SPICE/KiCad need pin *numbers* (1, 2, 3 …) on chip pins; today the codebase only has pin *names* (`a_1`, `y_2`, …). That mapping is a separate concern.
