# Board + Connector — Implementation Spec

## 1. Purpose

Add the physical concepts of **printed circuit boards** and **connectors** to the framework. A `Board` is a populated PCB — it has identity (name, revision), it carries components, and it can itself be a part within a stacked assembly. A `Connector` is the class of components whose contacts face outward off the board edge; mating two connectors physically joins two boards into a stacked assembly (the "HAT" pattern — Raspberry Pi shield, Arduino daughterboard, Eurorack module, etc.).

After this work package, the codebase can describe multi-board systems where boards mate via real, named connector parts, and the model preserves the per-board refdes scoping that real silkscreens have.

## 2. Scope

**In scope** — a `Board` class, a `Connector` abstract class, an initial set of concrete connector parts (the Raspberry Pi 40-pin GPIO pair as the canonical HAT case), a `mate()` function, BIDIR-pin support in the existing `Pin` primitive (a small generalisation needed by connectors), and a two-board demo that splits the existing `WaterAlarm` design across a sensor board and a controller board.

**Out of scope** — board mechanical/outline modelling (mounting holes, dimensions, board outline); pin numbering metadata for chips (separate work package — needed for SPICE/KiCad export but orthogonal to boards); cross-domain isolation (mating two boards on different `GroundDomain`s); cross-over / null-modem mating where pin order is permuted; sidecar JSON persistence of refdes; auto-annotation of refdes numbers; netlist exporters; the full library of real connector parts beyond the initial set in §7.

**Prerequisites** — the REFDES Instance Attributes work package (`docs/refdes-spec.md`) must be implemented first. This spec assumes `validate_refdes()`, `IEEE_315_PREFIXES`, `REFDES_PREFIX` class attributes, and the `refdes_number` / `refdes_section` constructor convention all exist.

## 3. Constraints carried over from CLAUDE.md

- Physical fidelity is primary. Every new class corresponds to a real-world physical thing (a board, a connector housing, a contact pin). Operations correspond to physical events (`mate()` = pushing two connectors together).
- `__slots__` declared on every new component class.
- No setters; identity (`name`, `revision`, `refdes`) is read-only after construction.
- Connectors are themselves `FactorNode`s — i.e. they are parts on the board, with refdes, that appear on the BOM. They are not framework primitives.
- Concrete connector subclasses correspond to real part numbers, not to abstract protocol categories. A `Pin2x20MaleHeader` is a real part; a `GenericConnector[40]` is not.
- Naming: physical events (`mate`, `solder`, `wire`), not software verbs (`connect`, `bind`, `attach`).

## 4. Concept overview

A board is a `Circuit` plus four physical things that `Circuit` doesn't model:

1. **Identity** — name and revision (silkscreen text).
2. **A refdes** — the board itself is a part `A1`, `A2` (assembly) when stacked under a parent.
3. **A connector-derived surface** — the board's externally visible `ports` are exactly the external faces of the `Connector` components placed on it. There is no separate "boundary port" abstraction — the surface emerges from the parts.
4. **Per-board refdes namespace** — already correct in the prerequisite refdes spec because `Circuit._validate` is non-recursive. Each `Board` instance contributes its own `An` to the parent's namespace; its internal `R1`, `D1`, `U1` are private to itself.

A connector is a `FactorNode` plus three physical things:

1. **A refdes** — `J1` (chassis-side / female) or `P1` (cable-side / male) per IEEE 315.
2. **A set of contacts** — modelled as `Pin` instances, the same primitive a chip uses for the same reason: each contact bridges board-internal wiring to board-external mating.
3. **A mating partner** — a class-level declaration of which other connector class it physically mates with. `mate()` enforces this at runtime.

The Pin/Cell pattern in `Chip` and the Connector/Component pattern in `Board` are the same shape at different scales — sealed package, named contacts as the surface, private innards.

## 5. Framework changes

### 5.1 BIDIR Pin support

The existing `Pin` raises `NotImplementedError` for `Direction.BIDIR`. Connector contacts are physically bidirectional (a contact is just a wire — direction is determined by what's wired to it), so this limitation must be lifted.

Generalise `Pin.__init__` to accept `Direction.BIDIR`:

- External face: `Direction.BIDIR`, mandatory, declared `signal_type`.
- Internal face: `Direction.BIDIR`, mandatory False, same `signal_type`.

Generalise `Pin.evaluate`:

```python
def evaluate(self) -> None:
    if self._role is Direction.IN:
        self._internal.drive(self._external.value)
    elif self._role is Direction.OUT:
        self._external.drive(self._internal.value)
    else:  # BIDIR
        ext, intl = self._external.value, self._internal.value
        if ext is None and intl is None:
            return
        if ext is not None and intl is None:
            self._internal.drive(ext)
        elif intl is not None and ext is None:
            self._external.drive(intl)
        elif ext != intl:
            raise ValueError(
                f"BIDIR pin '{self._external.name}' contention: "
                f"external={ext!r}, internal={intl!r}"
            )
        # else both equal — no-op
```

Update `Pin.__repr__` to render `'bidir'` for BIDIR pins.

### 5.2 `declare_mating_pair()` helper

A two-line helper to set the symmetric `MATES_WITH` ClassVars on two connector classes after both are defined, avoiding forward-reference awkwardness:

```python
# in framework/connector.py (or framework/mate.py)
def declare_mating_pair(a: type['Connector'], b: type['Connector']) -> None:
    """Mark two Connector subclasses as physical mates of each other."""
    a.MATES_WITH = b
    b.MATES_WITH = a
```

## 6. The `Connector` base class

New file `src/framework/connector.py`. `Connector` extends `FactorNode` directly (not `Circuit` — a connector has no internal wiring graph; it is a housing of `Pin`s).

```python
from typing import ClassVar
from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.pin import Pin
from framework.port import Direction
from framework.refdes import validate_refdes


class Connector(FactorNode):
    """A physical connector — a housing with a fixed set of named contacts.

    Each contact is a `Pin`, with an external face that mates with the
    partner connector and an internal face wired to the rest of the board.

    Concrete subclasses correspond to real-world parts and declare their
    pin count, pitch, gender, contact pinout, and physical mating partner.
    """

    __slots__ = ('_pins', '_refdes_number', '_refdes_section')

    REFDES_PREFIX:  ClassVar[str]                  # 'J' (female) or 'P' (male)
    GENDER:         ClassVar[str]                  # 'female' | 'male'
    PIN_COUNT:      ClassVar[int]
    PITCH_MM:       ClassVar[float]
    MATES_WITH:     ClassVar[type['Connector']]    # set via declare_mating_pair
    PINOUT:         ClassVar[tuple[tuple[str, Direction, type], ...]]
    # Each PINOUT entry: (contact_name, direction, signal_type).
    # Use Direction.BIDIR for general-purpose contacts (typical for headers);
    # use Direction.IN/OUT only when the connector physically constrains
    # signal direction (e.g. a fixed-function audio jack).

    def __init__(
        self,
        *,
        domain: GroundDomain = ELECTRICAL,
        refdes_number: int,
        refdes_section: str | None = None,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number, refdes_section)
        self._refdes_number  = refdes_number
        self._refdes_section = refdes_section
        self._pins = tuple(
            Pin(name, direction, domain, mandatory=False, signal_type=sigtype)
            for name, direction, sigtype in self.PINOUT
        )

    @property
    def pins(self) -> tuple[Pin, ...]:
        return self._pins

    @property
    def external_ports(self) -> dict:
        """Pin externals only — what the partner connector mates to,
        and what the board exposes on its surface."""
        return {pin.external.name: pin.external for pin in self._pins}

    @property
    def ports(self) -> dict:
        """Both faces of every pin — needed by Circuit._validate and
        Circuit._topological_sort inside the enclosing board."""
        out = {}
        for pin in self._pins:
            out.update(pin.ports)
        return out

    @property
    def refdes(self) -> str:
        if self._refdes_section is None:
            return f"{self.REFDES_PREFIX}{self._refdes_number}"
        return f"{self.REFDES_PREFIX}{self._refdes_number}{self._refdes_section}"

    @property
    def refdes_number(self) -> int:    return self._refdes_number

    @property
    def refdes_section(self) -> str | None: return self._refdes_section

    def evaluate(self) -> None:
        for pin in self._pins:
            pin.evaluate()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(refdes={self.refdes!r})"
```

Notes for the implementer:

- `Connector` is abstract by convention only (no `@abstractmethod`); the missing `ClassVar`s on the base will make any direct instantiation error out at attribute access. That's good enough — declaring `__init_subclass__` to enforce ClassVar presence is optional.
- The `refdes_section` parameter exists for symmetry with other refdes-bearing parts but is rarely needed for connectors. (No real connector that I'm aware of is sectioned the way a hex-inverter chip is. The parameter is there in case a future part needs it.)

## 7. Initial concrete connector classes

New file `src/components/connectors/__init__.py`. New file per part. The initial library is intentionally minimal — exactly what's needed to demonstrate the HAT pattern in the demo (§12) plus its mating partner. Future parts are added file-by-file in follow-up work.

### 7.1 The 2×20 0.1" pitch header pair (Raspberry Pi GPIO)

`src/components/connectors/pin2x20.py`:

```python
from typing import ClassVar
from framework.connector import Connector, declare_mating_pair
from framework.port import Direction
from framework.signals import Analog


def _gpio_pinout() -> tuple:
    # 40 pins, generic BIDIR, Analog signal type so they accept either
    # logic levels or rail voltages without enforcement at the pin.
    return tuple((f'p{i}', Direction.BIDIR, Analog) for i in range(1, 41))


class Pin2x20MaleHeader(Connector):
    """2×20 0.1\" (2.54 mm) pitch male pin header.
    The header soldered to a Raspberry Pi (J8 on RPi schematics)."""

    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'
    PIN_COUNT     = 40
    PITCH_MM      = 2.54
    PINOUT        = _gpio_pinout()


class Pin2x20FemaleHeader(Connector):
    """2×20 0.1\" (2.54 mm) pitch female socket header.
    The header soldered to a HAT / shield, mating with the SBC's male header."""

    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'
    PIN_COUNT     = 40
    PITCH_MM      = 2.54
    PINOUT        = _gpio_pinout()


declare_mating_pair(Pin2x20MaleHeader, Pin2x20FemaleHeader)
```

### 7.2 Naming and packaging convention

Each connector part lives in its own module under `src/components/connectors/`. Module name = lowercase part identifier (`pin2x20.py`, `jst_xh_4.py`, `usb_c_receptacle.py`). Class name = part identifier in PascalCase. Mating pairs live in the same module and call `declare_mating_pair()` at module bottom.

Per CLAUDE.md, naming follows hardware terminology — `Pin2x20MaleHeader`, not `Connector40Pin`. Pitch is encoded in the class doc, not in the class name (the `2x20` already implies 0.1" pitch in industry usage; for non-standard pitches add a suffix like `Pin2x10_2mm`).

## 8. The `Board` class

New file `src/framework/board.py`. `Board` extends `Circuit`.

```python
from typing import ClassVar
from framework.circuit import Circuit
from framework.connector import Connector
from framework.factor import FactorNode
from framework.refdes import validate_refdes


class Board(Circuit):
    """A printed circuit board: a populated PCB with name, revision,
    and a refdes (it is itself a part within a parent assembly).

    The board's external surface is the set of external pin faces of every
    `Connector` component on it. Surface port names are qualified by the
    connector's refdes — e.g. 'J1.p3' — to guarantee uniqueness when a
    board carries more than one connector.

    Refdes scoping is correct for free: `Circuit._validate` (per the refdes
    spec) is non-recursive, so each Board contributes only its own refdes
    'A1' / 'A2' to the parent assembly's namespace, while its internal
    R1/D1/U1 are private to itself.
    """

    REFDES_PREFIX: ClassVar[str] = 'A'
    __slots__ = (
        '_name', '_revision', '_connectors',
        '_refdes_number', '_refdes_section',
    )

    def __init__(
        self,
        *,
        name: str,
        revision: str,
        components: list[FactorNode],
        refdes_number: int,
        refdes_section: str | None = None,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number, refdes_section)
        if not isinstance(name, str) or not name:
            raise ValueError("Board name must be a non-empty string")
        if not isinstance(revision, str) or not revision:
            raise ValueError("Board revision must be a non-empty string")

        self._name           = name
        self._revision       = revision
        self._refdes_number  = refdes_number
        self._refdes_section = refdes_section
        self._connectors     = tuple(c for c in components if isinstance(c, Connector))

        # Surface = external faces of every connector, qualified by refdes.
        ports = {}
        for connector in self._connectors:
            for pin_name, port in connector.external_ports.items():
                qualified = f"{connector.refdes}.{pin_name}"
                if qualified in ports:
                    raise ValueError(
                        f"Duplicate surface port '{qualified}' — "
                        f"two connectors share refdes {connector.refdes}?"
                    )
                ports[qualified] = port

        super().__init__(factor_nodes=list(components), ports=ports)

    @property
    def name(self) -> str:           return self._name
    @property
    def revision(self) -> str:       return self._revision
    @property
    def connectors(self) -> tuple:   return self._connectors
    @property
    def refdes(self) -> str:
        if self._refdes_section is None:
            return f"{self.REFDES_PREFIX}{self._refdes_number}"
        return f"{self.REFDES_PREFIX}{self._refdes_number}{self._refdes_section}"
    @property
    def refdes_number(self) -> int:           return self._refdes_number
    @property
    def refdes_section(self) -> str | None:   return self._refdes_section

    def __repr__(self) -> str:
        return (
            f"Board(name={self._name!r}, revision={self._revision!r}, "
            f"refdes={self.refdes!r})"
        )
```

`Board` is concrete: callers may instantiate it directly (`Board(name="Sensor Board", revision="A", components=[...], refdes_number=1)`) for ad-hoc designs, or subclass it to give a particular design a Python identity (recommended for production code). Subclasses follow the existing `WaterAlarm`-style pattern: their `__init__` constructs all parts, wires them, then calls `super().__init__(...)`.

Boards do **not** need a `__call__` — they evaluate via `Circuit.evaluate()` and signals reach them through wired surface ports. A subclass may add `__call__` if the board is also useful as a standalone testable unit (driving probes directly), but it's not required by the framework.

## 9. The `mate()` function

New file `src/framework/mate.py`:

```python
from framework.connector import Connector
from framework.wire import wire


def mate(a: Connector, b: Connector) -> None:
    """Physically mate two connectors: wire each external pin of `a` to the
    same-position external pin of `b`.

    Mating is positional — pin i of `a` joins pin i of `b`, matching the
    physical reality where pin numbers stamped on the housings line up when
    the parts are pushed together.

    Raises:
        TypeError  — if `b` is not type(a).MATES_WITH (the parts are not
                     physical mates of each other).
        ValueError — pin count mismatch, ground domain mismatch, signal-type
                     mismatch, or any wire()-level error per pin pair.
    """
    if type(b) is not type(a).MATES_WITH:
        raise TypeError(
            f"{type(a).__name__} mates with {type(a).MATES_WITH.__name__}, "
            f"not {type(b).__name__}"
        )
    if len(a.pins) != len(b.pins):
        raise ValueError(
            f"Pin count mismatch: {type(a).__name__} has {len(a.pins)} pins, "
            f"{type(b).__name__} has {len(b.pins)}"
        )
    for pa, pb in zip(a.pins, b.pins):
        wire(pa.external, pb.external)
```

Notes:

- `mate()` only wires the external pin faces of the two connectors. The internal faces remain wired to whatever each board's `__init__` connected them to. Once mated, the resulting graph spans both boards and `Circuit.evaluate()` on either board will (subject to topological order) propagate signals across the seam.
- `mate()` does not need to track which boards the connectors belong to. A connector knows its own pins; that's enough.
- A connector may be mated only once. If any external face is already on a node, `wire()` will refuse to merge two distinct existing nodes (per `wire()`'s current behaviour) — surfacing a clear error message. No additional check needed in `mate()`.
- Stacked-board evaluation: when board `A1` and board `A2` are mated and then composed under a parent `Circuit`, the parent's `factor_nodes=[A1, A2]` and topological sort orders them by data dependency through the connector seam. No additional framework support is needed; this falls out of the existing topological sort.

## 10. Refdes scope (no spec changes)

The prerequisite refdes spec adds duplicate-refdes detection to `Circuit._validate` operating on the *direct* `factor_nodes` of the composite (not recursing into child composites). This is the correct scope for boards:

- A child `Board` contributes its own refdes (e.g. `A1`) to the parent assembly's namespace, where it must be unique among other refdes-bearing children.
- The board's *internal* `R1`, `D1`, `J1` are checked only inside the board's own `_validate` invocation.
- Two separate `Board` instances may both contain `R1` — exactly the silkscreen behaviour of real PCBs, and exactly what is required for the HAT pattern.

No edits to `framework/circuit.py` beyond what the refdes spec already requires.

## 11. File-by-file change list

New files:

- `src/framework/connector.py` — `Connector` base class, `declare_mating_pair()`.
- `src/framework/board.py` — `Board(Circuit)` class.
- `src/framework/mate.py` — `mate()` function.
- `src/components/connectors/__init__.py` — empty (or re-exports for convenience).
- `src/components/connectors/pin2x20.py` — `Pin2x20MaleHeader`, `Pin2x20FemaleHeader`, mating-pair declaration.

Modified files:

- `src/framework/pin.py` — generalise `__init__` and `evaluate` to support `Direction.BIDIR` (§5.1).
- `src/applications/water_alarm_split/__init__.py` — new demo (§12). Or place under `src/applications/` as a peer module of `water_alarm.py`. Do not modify the existing `water_alarm.py`.

Unmodified:

- `src/framework/circuit.py` — refdes-scoping behaviour is already correct.
- `src/framework/chip.py`, `factor.py`, `ground.py`, `node.py`, `port.py`, `signals.py`, `units.py`, `wire.py` — untouched.
- All existing chip and passive component files — untouched.
- `src/applications/water_alarm.py` — untouched (kept as the canonical single-circuit example for backward comparison).

## 12. Demo: WaterAlarm split across two boards

A new application `src/applications/water_alarm_split/` demonstrates Board + Connector + mate() end-to-end by re-implementing `WaterAlarm` as two physical boards mated through a 6-pin connector.

**`SensorBoard`** carries the input-conditioning electronics:

- `ULN2003A` (refdes `U1` on the sensor board)
- `Pin2x20FemaleHeader` (refdes `J1`) — only 6 of the 40 pins are used; the rest are unconnected.
  - `J1.p1` ← VCC supply (board input)
  - `J1.p2` ← GND
  - `J1.p3` ← low_probe sensor input (wired to `U1.in_1`)
  - `J1.p4` ← high_probe sensor input (wired to `U1.in_2`)
  - `J1.p5` → low_probe conditioned output (wired from `U1.out_1`)
  - `J1.p6` → high_probe conditioned output (wired from `U1.out_2`)

**`ControllerBoard`** carries the latch and indicators:

- `SN74HC04` (refdes `U1` — note: shares `U1` with the sensor board's `U1`; this is correct, refdes is per-board)
- `CD4043` (refdes `U2`)
- `LED('red')` (refdes `D1`)
- `LED('green')` (refdes `D2`)
- `Rail(False)` (refdes-less; existing class, retains its existing pattern)
- `Rail(True)` (refdes-less)
- `Pin2x20MaleHeader` (refdes `P1`) — same 6 pins of interest as the sensor board, plus internal wiring through the SN74HC04 to the CD4043 latch and out to the LEDs.

**`WaterAlarmAssembly`** is a `Circuit` (not a `Board` — it's a stacked assembly, not a PCB) that holds:

- `SensorBoard(refdes_number=1)` → `A1`
- `ControllerBoard(refdes_number=2)` → `A2`
- A single `mate(sensor.connectors[0], controller.connectors[0])` call

and exposes the surface ports of `A1` for sensor drive (`A1.J1.p3`, `A1.J1.p4`) and observes the controller's LED state via component handles.

The demo is the test surface for the work package: it must produce identical end-to-end behaviour to the existing single-circuit `WaterAlarm` for the same probe-input sequences.

## 13. Test plan

New test module `tests/framework/test_board.py`:

1. **Empty board.** `Board(name='X', revision='A', components=[], refdes_number=1).refdes == 'A1'`. Surface ports dict is empty.
2. **Board with a connector exposes its externals.** Construct a board with one `Pin2x20FemaleHeader(refdes_number=1)`. Assert `'J1.p1'` … `'J1.p40'` are in the board's `ports`.
3. **Multiple connectors on one board, no port name collision.** Construct a board with two female headers (`refdes_number=1`, `refdes_number=2`). Assert ports include both `'J1.p1'` and `'J2.p1'`.
4. **Two connectors with the same refdes is rejected.** Construct a board with two female headers both `refdes_number=1`. Refdes-spec's `Circuit._validate` raises duplicate-refdes; verify the exception message names both.
5. **Board has refdes prefix `A`.** `Board(...).REFDES_PREFIX == 'A'`. `Board(refdes_number=3).refdes == 'A3'`.
6. **Board name and revision are required strings.** Empty / non-string values raise `ValueError`.
7. **Board name and revision are read-only.** No setter exists; assignment raises `AttributeError` on a property.

New test module `tests/framework/test_connector.py`:

8. **`Connector` is abstract by convention.** Direct instantiation of `Connector(refdes_number=1)` fails (missing `REFDES_PREFIX` / `PINOUT` ClassVars).
9. **A concrete connector exposes its pins.** `Pin2x20FemaleHeader(refdes_number=1).pins` is length 40; each is a `Pin`.
10. **External vs. all ports.** `external_ports` length == 40; `ports` length == 80 (external + internal per pin).
11. **Refdes prefix is `J` for female, `P` for male.** Per the IEEE 315 convention.
12. **BIDIR pin support.** `Pin('x', Direction.BIDIR, ELECTRICAL, signal_type=Digital)` constructs without error. Drive external → internal sees the value; drive internal → external sees the value; drive both with same value → no-op; drive both with different values → `ValueError("contention")`.

New test module `tests/framework/test_mate.py`:

13. **Successful mate.** `mate(female, male)` wires every external pin pair. After mating, driving `female.pins[0].external` results in `male.pins[0].external` reading the same value (after `evaluate()`).
14. **Mismatched mate raises.** `mate(female, female)` raises `TypeError` mentioning `MATES_WITH`.
15. **Ground domain mismatch raises.** Construct two female headers in different domains, attempt to mate (after a `male` is built in the other domain). Raises `ValueError`.
16. **A connector cannot be mated twice.** `mate(a, b); mate(a, c)` — second call raises (per `wire()`'s "would merge two existing nodes" guard).
17. **`declare_mating_pair` symmetry.** After declaration, `A.MATES_WITH is B and B.MATES_WITH is A`.

New test module `tests/applications/test_water_alarm_split.py`:

18. **End-to-end equivalence.** For the same sequence of `(low_probe, high_probe)` inputs, the split assembly's red/green LED states and the latch `q_1` value match the single-circuit `WaterAlarm`. Run a representative truth-table-ish exercise: `(0,0) → idle`, `(1,0) → set alarm`, `(1,1) → clear alarm`, `(0,1)` (impossible physically — high probe wet, low dry — verify the model behaves consistently, even if the result is implementation-defined).
19. **Refdes scoping is correct in the assembly.** `assembly.refdes_in_use` (informal: walk and collect) shows `A1`, `A2`; descending into `A1` shows `U1`, `J1`; descending into `A2` shows `U1` (correct collision-free across boards), `U2`, `D1`, `D2`, `P1`.
20. **Unmated assembly evaluation.** Construct sensor + controller boards but skip the `mate()` call. Driving the sensor's probe ports leaves the controller's LEDs in their power-on state (`None` for `LED.lit`) — i.e. the seam is open. This exercises the BIDIR-pin "neither side driven" path.

Existing-test impact: none. The work package adds capability; existing components and `WaterAlarm` are untouched.

## 14. Acceptance criteria

The work is done when:

1. `python -m pytest` passes including all new tests.
2. The two-board `WaterAlarm` demo produces output equivalent to the single-circuit `WaterAlarm` for matched probe inputs.
3. `Pin` accepts `Direction.BIDIR` and the contention rule is enforced.
4. `Board`, `Connector`, `Pin2x20MaleHeader`, `Pin2x20FemaleHeader`, and `mate()` exist and behave per §6, §7, §8, §9.
5. No setters added to any component class; all new identity/refdes accessors are read-only properties.
6. Every new class declares `__slots__`.
7. `mate()` uses positional pin correspondence and raises clearly when types or pin counts disagree.
8. The existing `water_alarm.py` and all other existing files except `framework/pin.py` are unmodified.

## 15. Out of scope (for follow-up work packages)

- **Mechanical / outline modelling.** Mounting holes, board outline, dimensions, keep-out zones. None of this is electrical and the soldering-iron principle excludes it from the current model.
- **Pin numbers on chip pins.** SPICE/KiCad export needs pin *numbers* (1, 2, 3, …) on chip and connector pins; today only pin *names* are modelled. Connector pins use `p1`–`p40` which doubles as a number, but chips don't yet — separate work.
- **Cross-domain mating.** Modelling boards on different `GroundDomain`s (e.g. mains-isolated vs. battery-referenced) and the optical / capacitive isolation barriers between them.
- **Cross-over / null-modem connectors.** Mating where pin order is permuted (cross-over Ethernet, null-modem serial). Implementable as a separate `mate_crossover()` function or as a connector subclass override; either is plausible.
- **Wider connector library.** JST-XH series, USB-A/B/C, RJ-45, IDC ribbon, screw terminals, board-edge connectors. Add part-by-part as designs require.
- **Multi-board enclosures and bus backplanes.** Boards mating into a shared backplane (Eurorack, VME, PCI). The framework supports this without changes — a backplane is just a `Board` with many connectors of the same type — but the demonstration is a separate work package.
- **Sidecar JSON persistence**, **netlist exporters** (SPICE, KiCad, EDIF), **auto-annotation of refdes numbers** — all separately tracked, all unaffected by this spec.
