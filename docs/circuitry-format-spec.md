# `.circuitry` Format and Pydantic Adoption — Implementation Spec

## 1. Purpose

Give the framework a canonical, lossless, human-readable file format — extension `.circuitry` — for saving and loading complete designs (an `Assembly`, a `Board`, or a standalone `Circuit`). The format is the foundation for every downstream consumer: SPICE / KiCad / EDIF netlist exporters, schematic visualisers, future PCB layout tools. Each of those reads a `.circuitry` file rather than walking the in-memory model.

This work package also brings **pydantic v2** into the project. Pydantic is the schema engine for the format and the validation engine for every component class's argument-bearing methods. The earlier "stdlib for now, pydantic when it earns its keep" decision is reversed: it has earned its keep, and the project adopts it broadly.

## 2. Scope

**In scope** — the `.circuitry` JSON format (top-level structure, component records, wiring, mate operations, surface ports, format versioning); pydantic v2 as the schema engine; a component registry mapping class names to classes; reader and writer APIs (`load_circuitry(path)`, `save_circuitry(root, path)`); migrating `PinId` to `pydantic.dataclasses.dataclass`; adding `@validate_call` to every component class's `__init__` and to argument-bearing methods across the framework (`wire`, `mate`, `validate_refdes`, `Pin.other_face`, etc.); converting hand-rolled validation to pydantic field constraints where the mapping is direct; round-tripping every existing application end-to-end.

**Out of scope** — netlist exporters (SPICE, KiCad, EDIF, Yosys JSON) — they read `.circuitry` files in follow-on work packages; migrations between major format versions; multi-file projects where one `.circuitry` references another; binary or compressed format variants; schema publication to a public registry; pydantic adoption inside `Port`, `Node`, `Wire`, or other low-level primitives that aren't user-constructed (their state is managed by `wire()` and `Circuit._validate`, not by direct user calls).

**Prerequisites** — refdes spec, board+connector spec, and pin-id spec all implemented. This spec assumes `PinId`, `IS_CONDUCTOR`, the logical-net `_validate`, the full connector library, and every refdes-bearing class are in place.

## 3. Constraints carried over from CLAUDE.md

- Physical fidelity is primary. The `.circuitry` file describes physical things: parts with refdes, pins with numbers and names, conductors joining contacts. The schema's job is to record those facts; pydantic is just the validation/serialisation engine and is not allowed to introduce software fictions into the data model.
- `__slots__` everywhere. Components are not converted to `pydantic.BaseModel` (which would change their `__slots__` semantics and conflict with the existing architecture). Pydantic enters via two narrower mechanisms — `@validate_call` for method validation, and `BaseModel` subclasses for the serialisation schema records.
- No setters. Component state is constructed once and read thereafter. Round-trip is "save current state → load identical fresh instance," not "save → mutate → load."
- Component name resolution is registry-mediated, never via `importlib.import_module()` or `eval`. The registry IS the security boundary against pickle-style RCE.

## 4. Why pydantic now (and why not earlier)

The earlier deferral was correct on its terms: `PinId` is two fields constructed in code, validated in code, consumed in code. Pydantic's machinery had nothing to do there.

This work package is different on three axes:

1. **External-data boundary.** The `.circuitry` file is text that crosses the boundary between disk and process. It's deserialised from untrusted bytes. Validation against a schema is the right tool — what pydantic was built for.
2. **Schema versioning.** The format will evolve. Major-version bumps need explicit migration paths; minor versions need additive compatibility. Pydantic models are the natural place to encode that.
3. **Validation breadth.** Every component class accepts user-supplied constructor arguments (refdes numbers, ohms values, colours, pin counts, pitches). Today each `__init__` either validates by hand or doesn't validate at all. `@validate_call` with `Annotated` field constraints gives uniform, declarative validation across the codebase with one decorator per method.

Pydantic v2 is the target. v1 is deprecated, the v2 Rust core is fast enough that runtime overhead is acceptable for the call frequencies in this codebase, and `@validate_call` plus `pydantic.dataclasses.dataclass` are v2-native APIs.

## 5. The pydantic adoption

### 5.1 Three pydantic shapes, three use cases

The work package uses pydantic in three distinct shapes; each fits a different need.

| Shape                                  | Where it's used                                                                                                                                                                            |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `@pydantic.validate_call`              | Decorator on every component class's `__init__`, on argument-bearing framework methods (`wire`, `mate`, `validate_refdes`, `Pin.other_face`), and on the reader/writer entry points. Validates arguments against type hints + `Annotated` constraints at call time. No structural changes to the class. |
| `@pydantic.dataclasses.dataclass`      | `PinId` and any future small immutable value-object data classes. Drop-in replacement for stdlib `dataclass`; validation runs on construction.                                              |
| `pydantic.BaseModel` subclasses        | The `.circuitry` schema records (`ComponentRecord`, `BoardRecord`, `AssemblyRecord`, `WireRecord`, `MateRecord`, `SurfacePortRecord`, `CircuitryFile`). Used only for the file format — not for components themselves. |

Components are *not* converted to `BaseModel`. They keep their `__slots__`, their `evaluate()` and `__call__` methods, their hand-built `_ports` dicts, everything. Pydantic touches them only via the `@validate_call` decorator on argument-bearing methods.

### 5.2 `PinId` migration

The current stdlib dataclass:

```python
@dataclass(frozen=True, slots=True)
class PinId:
    number: int
    name: str
    def __post_init__(self) -> None: ...
```

becomes:

```python
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Annotated

@dataclass(frozen=True, slots=True, config={"arbitrary_types_allowed": False})
class PinId:
    number: Annotated[int, Field(gt=0)]
    name: Annotated[str, Field(min_length=1)]
```

The hand-rolled `__post_init__` checks are replaced by the field constraints. Behaviour is identical from the caller's perspective: `PinId(1, 'VBUS')` works; `PinId(0, 'X')`, `PinId(-1, 'X')`, `PinId(1, '')` all raise `ValidationError` (a pydantic exception type, picklable, with structured error info).

The pin-id spec's test suite (test 4 — number must be positive int; test 5 — name must be non-empty string) continues to pass; the error *types* change from `TypeError` / `ValueError` to `pydantic.ValidationError`. Test assertions are updated accordingly.

### 5.3 `@validate_call` across the framework

Every argument-bearing method gets the decorator:

```python
from pydantic import validate_call, Field, PositiveInt, PositiveFloat
from typing import Annotated

class Resistor(FactorNode):
    __slots__ = ('_ohms', '_ports', '_refdes_number')
    REFDES_PREFIX = 'R'

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        ohms: Annotated[float, Field(gt=0)] | Ohms,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: PositiveInt,
    ) -> None:
        self._ohms = float(ohms)
        self._refdes_number = refdes_number
        self._ports = {...}

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, current: float | Amps) -> Volts:
        return Volts(float(current) * self._ohms)
```

The `arbitrary_types_allowed=True` config flag is necessary because `GroundDomain`, `Ohms`, `Amps`, `Volts`, `Port`, `Pin`, `Connector`, `FactorNode`, `Circuit`, `Board`, etc. are project types that pydantic doesn't know how to introspect by default. The flag tells pydantic to accept them as-is on `isinstance` checks.

`@validate_call` lands on:

- Every component class's `__init__` and `__call__`: every chip, every passive, every connector, every cell concept, `Circuit`, `Board`, `Chip` if its `__init__` is non-trivial.
- Every framework free function: `wire(*ports)`, `mate(a, b)`, `validate_refdes(prefix, number)`, `declare_mating_pair(a, b)`.
- `Pin.other_face(port)` and any other argument-bearing method on framework primitives.
- The reader and writer entry points: `load_circuitry(path)`, `save_circuitry(root, path)`.

It does **not** land on:

- Property getters (no arguments).
- `evaluate(self)` (no arguments — its work is graph traversal, not parameter handling).
- Private methods (`_validate`, `_topological_sort`, `_build_pinout`, `_logical_net`) — these are called from within the class's own machinery with already-validated arguments. Validating twice is waste.
- Hot-path methods inside the evaluator. If profiling reveals `@validate_call` on `__call__` is in a measurable hot path, the decorator is removed and a per-class comment notes the deliberate exemption.

### 5.4 Existing hand-rolled validation

Three call-sites already validate by hand: `validate_refdes()` (the refdes-spec helper), `wire()` (driver count, domain match, signal-type compatibility), and `Pin.evaluate` (BIDIR contention).

`validate_refdes` becomes a slim wrapper that just calls into pydantic-validated `PositiveInt` / `Literal[*IEEE_315_PREFIXES]` constraints, or its responsibilities migrate into per-component field annotations (`refdes_number: PositiveInt` is already pydantic-native; `REFDES_PREFIX: Literal[*tuple(IEEE_315_PREFIXES)]` covers the prefix). Either way the hand-rolled body shrinks.

`wire()` is harder — its rules are about *relationships among arguments* (no more than one OUT, all ports share a domain, all share a signal type) rather than per-argument types. Pydantic field constraints don't express cross-field invariants well. Keep `wire()`'s body as hand-rolled validation; add `@validate_call` so the *signature* (each argument is a `Port`) is pydantic-checked, and keep the relationship checks in the body. A `model_validator(mode='after')` could express the cross-field rules if `wire()` were a `BaseModel`, but converting it to one isn't worth the contortion.

`Pin.evaluate`'s contention check is genuine runtime logic, not validation. It stays as-is.

### 5.5 Validation error handling

`pydantic.ValidationError` replaces hand-raised `ValueError` / `TypeError` for most argument-validation cases. The error type is a hierarchy under `pydantic`; tests that previously asserted `ValueError` are updated to assert `pydantic.ValidationError`.

Where a specific exception type is part of the public API (none currently — but the future SPICE exporter might want to raise `circuitry.export.SpiceExportError`), the framework can catch `ValidationError` at the boundary and re-raise as a domain-specific type. Not needed for this work package.

## 6. The `.circuitry` format — overview

A `.circuitry` file is JSON. The top-level structure:

```json
{
  "format_version": "1.0.0",
  "name": "Water Alarm Assembly",
  "root": {
    "type": "Assembly",
    ...
  }
}
```

- `format_version` — semver string. Loaders reject unknown major versions with a clear error.
- `name` — optional, human-readable design name. Not used for reconstruction; saved for the human reader.
- `root` — one of: `AssemblyRecord`, `BoardRecord`, `CircuitRecord`. The single hierarchy root of the design.

The root determines what's at the top: an `Assembly` (a `Circuit` containing `Board`s and `mate()` operations), a `Board` (a `Circuit` with connectors that hasn't been stacked yet), or a standalone `Circuit` like the original `WaterAlarm`.

### 6.1 Component records

Each component class has a corresponding pydantic record class. Records share three fields: `type` (discriminator literal), `refdes` (if the component has one), and component-specific configuration.

```python
class ResistorRecord(BaseModel):
    type: Literal["Resistor"] = "Resistor"
    refdes: Annotated[str, Field(pattern=r'^R\d+$')]
    ohms: PositiveFloat

class LEDRecord(BaseModel):
    type: Literal["LED"] = "LED"
    refdes: Annotated[str, Field(pattern=r'^D\d+$')]
    color: Annotated[str, Field(min_length=1)]

class RailRecord(BaseModel):
    type: Literal["Rail"] = "Rail"
    # No refdes — Rail is a net abstraction
    id: Annotated[str, Field(pattern=r'^Rail_\d+$')]  # synthesised local id
    level: bool

class GroundRecord(BaseModel):
    type: Literal["Ground"] = "Ground"
    id: Annotated[str, Field(pattern=r'^Ground_\d+$')]

class SN74HC04Record(BaseModel):
    type: Literal["SN74HC04"] = "SN74HC04"
    refdes: Annotated[str, Field(pattern=r'^U\d+$')]

# ... one record per chip, passive, and connector class
```

All component records are union'd through a discriminator on the `type` field:

```python
ComponentRecord = Annotated[
    Union[ResistorRecord, LEDRecord, RailRecord, GroundRecord,
          SN74HC04Record, CD4069Record, LM393Record, CD4043Record, ULN2003ARecord,
          Header1xNMaleRecord, Header1xNFemaleRecord,
          Header2xNMaleRecord, Header2xNFemaleRecord,
          IDC2xNMaleRecord, IDC2xNSocketRecord,
          USBAReceptacleRecord, USBAPlugRecord,
          USBBReceptacleRecord, USBBPlugRecord,
          USBMicroBReceptacleRecord, USBMicroBPlugRecord,
          USBCReceptacleRecord, USBCPlugRecord,
          RJ45JackRecord, RJ45PlugRecord,
          HDMITypeAReceptacleRecord, HDMITypeAPlugRecord,
          Audio3p5mmTRSJackRecord, Audio3p5mmTRSPlugRecord,
          Audio3p5mmTRRSJackRecord, Audio3p5mmTRRSPlugRecord,
          BarrelJack5p5x2p1Record, BarrelPlug5p5x2p1Record,
          BarrelJack5p5x2p5Record, BarrelPlug5p5x2p5Record,
          JSTPHBoardSideRecord, JSTPHCableHousingRecord,
          JSTXHBoardSideRecord, JSTXHCableHousingRecord,
          JSTSHBoardSideRecord, JSTSHCableHousingRecord,
          JSTGHBoardSideRecord, JSTGHCableHousingRecord,
          ScrewTerminalBlockRecord,
          MicroSDCardSlotRecord, MicroSDCardRecord,
          SDCardSlotRecord, SDCardRecord],
    Discriminator("type"),
]
```

Parameterised connectors carry `pin_count` and `pitch_mm` fields. Boards carry `name` and `revision` fields. The pin-id spec means each component already knows its pin numbering from its class definition; the file doesn't need to re-encode pin IDs (loading reconstructs them from the class).

### 6.2 Board records

`BoardRecord` is structurally a flat container: the board's identity, its child components, and the wires between them.

```python
class WireRecord(BaseModel):
    ports: list[Annotated[str, Field(min_length=1)]] = Field(min_length=2)
    # Each entry is a port reference like "U1.out_1" or "J1.p3_external"
    # All entries are joined into one Node by the loader.

class BoardRecord(BaseModel):
    type: Literal["Board"] = "Board"
    refdes: Annotated[str, Field(pattern=r'^A\d+$')]
    name: Annotated[str, Field(min_length=1)]
    revision: Annotated[str, Field(min_length=1)]
    components: list[ComponentRecord]
    wires: list[WireRecord]
```

The `Board` subclass identity (`SensorBoard`, `ControllerBoard`, etc.) is not preserved by the round-trip — the loader reconstructs a plain `Board` with the same components and wires. If subclass identity matters (e.g., the subclass has additional methods), the user can either retain the subclass in code and not round-trip it through `.circuitry`, or follow up with a "preserve subclass via registry" extension (out of scope here).

### 6.3 Circuit records

`CircuitRecord` is like `BoardRecord` but without name/revision/refdes — it's just a flat Circuit composite without board identity. Used for things like `WaterAlarm` that were `Circuit` subclasses before the board work landed.

```python
class CircuitRecord(BaseModel):
    type: Literal["Circuit"] = "Circuit"
    components: list[ComponentRecord]
    wires: list[WireRecord]
    surface_ports: dict[str, str] = Field(default_factory=dict)
    # Maps surface port name → internal port reference, e.g.
    # {"low_probe": "U1.in_1"}.
```

### 6.4 Assembly records

An assembly is a top-level composite that holds boards and the mate operations joining them.

```python
class MateRecord(BaseModel):
    a: Annotated[str, Field(pattern=r'^[AJP]\d+(\.[JP]\d+)?$')]
    b: Annotated[str, Field(pattern=r'^[AJP]\d+(\.[JP]\d+)?$')]
    # References to connectors by their hierarchical refdes:
    # "A1.J1" means board A1's connector J1.

class SurfacePortRecord(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    target: Annotated[str, Field(min_length=1)]
    # Hierarchical port reference, e.g. "A2.P1.p3_external" or "A2.U2.q_1".

class AssemblyRecord(BaseModel):
    type: Literal["Assembly"] = "Assembly"
    boards: list[BoardRecord]
    mates: list[MateRecord]
    surface_ports: list[SurfacePortRecord] = Field(default_factory=list)
```

### 6.5 The file envelope

```python
class CircuitryFile(BaseModel):
    format_version: Annotated[str, Field(pattern=r'^\d+\.\d+\.\d+$')]
    name: str | None = None
    root: AssemblyRecord | BoardRecord | CircuitRecord = Field(discriminator='type')

    model_config = {"extra": "forbid"}  # reject unknown top-level keys
```

`extra="forbid"` ensures forward-compatibility safety: an older loader hitting a future-format file with new top-level fields fails loudly rather than silently dropping data. New minor-version fields are added with explicit defaults; old loaders just don't see them in the model, so they're not preserved across save (acceptable for minor-version compatibility).

## 7. Port reference syntax

Throughout the format, ports are referenced by dotted hierarchical paths:

- Inside a Board: `"U1.out_1"`, `"J1.p3_external"`, `"D1.anode"`. The first segment is the local refdes (or synthesised id for refdes-less parts like `Rail_0`); subsequent segments name the port.
- Inside an Assembly: `"A1.U1.out_1"` for a port on a chip inside a board; `"A1.J1"` for a connector itself when referenced by `mate()`; `"A2.P1.p3_external"` for the external face of pin p3 on the controller board's connector P1.
- Pin external vs. internal faces use the suffixes `_external` and `_inner` (matching the existing `Pin._inner` naming convention).

Port references are validated against the live in-memory model on load; an unknown reference raises a `pydantic.ValidationError` with the full path that failed to resolve.

## 8. The component registry

```python
# framework/registry.py
from typing import Callable, TypeVar
from framework.factor import FactorNode

T = TypeVar('T', bound=FactorNode)

_REGISTRY: dict[str, type[FactorNode]] = {}


def register(name: str) -> Callable[[type[T]], type[T]]:
    """Class decorator: register a FactorNode subclass under a string name
    for the .circuitry deserialiser to look up. Names must be unique
    across the codebase. Use the bare class name by convention."""
    def decorator(cls: type[T]) -> type[T]:
        if name in _REGISTRY:
            raise ValueError(
                f"Component name {name!r} already registered to "
                f"{_REGISTRY[name].__module__}.{_REGISTRY[name].__qualname__}"
            )
        _REGISTRY[name] = cls
        return cls
    return decorator


def lookup(name: str) -> type[FactorNode]:
    """Look up a component class by registered name. Used by the .circuitry
    loader. Raises KeyError with a clear message if the name is unknown."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown component type {name!r}; not in the registry. "
            f"Known types: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]
```

Every component class decorates itself:

```python
from framework.registry import register

@register("Resistor")
class Resistor(FactorNode):
    ...
```

The registry IS the deserialiser's allowlist. Nothing else needs to validate "is this class safe to instantiate" — if it's in the registry, it was registered at import time by code the user trusts; otherwise the deserialiser rejects it. This is the security boundary that replaces pickle's arbitrary-code surface.

The naming convention: use the bare class name (`"Resistor"`, `"SN74HC04"`, `"Header2xNMale"`). This keeps the `.circuitry` file readable. Uniqueness is verified at registration; collisions raise at import time.

## 9. Reader / writer API

```python
# framework/format.py
from pathlib import Path
from pydantic import validate_call

@validate_call
def save_circuitry(root: FactorNode, path: Path | str) -> None:
    """Serialise a Circuit / Board / Assembly to a .circuitry file."""
    record = _to_record(root)
    file = CircuitryFile(format_version=CURRENT_FORMAT_VERSION, root=record)
    Path(path).write_text(file.model_dump_json(indent=2))


@validate_call
def load_circuitry(path: Path | str) -> FactorNode:
    """Load a .circuitry file and reconstruct the in-memory model.

    Raises:
        pydantic.ValidationError — schema violation (unknown component
            type, bad refdes, malformed port reference, etc.).
        ValueError — semantic violation (forward references to
            undeclared components, port references that don't resolve,
            mate() failure, _validate() failure).
        FileNotFoundError — path doesn't exist.
    """
    raw = Path(path).read_text()
    file = CircuitryFile.model_validate_json(raw)
    _check_format_version(file.format_version)
    return _from_record(file.root)
```

`_to_record` and `_from_record` are dispatch tables driven by the discriminator: each record type knows how to inflate itself into a live `FactorNode` via the registry, and each component class either provides a `to_record(self) -> ComponentRecord` method or has a default extractor in the format module.

The serialiser walks the in-memory model in deterministic order (sorted refdes; insertion order for refdes-less parts) so two saves of the same design produce byte-identical files. This matters for version control.

## 10. Round-trip discipline

The contract: `load_circuitry(save_circuitry(root)) == root`, structurally. "Structurally" means:

- Same component count and types.
- Same refdes assignments.
- Same component-specific values (ohms, color, level, pin_count, pitch_mm, name, revision, …).
- Same wiring topology — every node in the original is reconstructed with the same set of attached ports.
- Same mate operations and surface ports.

Evaluation cache state (`Port._local_value`, `Node._value`) is *not* preserved. Loaded models are in the same state as freshly constructed ones — i.e. pre-`evaluate()`.

Round-trip is verified by a parametrised test that walks every existing application:

1. Build the in-memory model: `original = WaterAlarm()`.
2. Save and reload: `roundtripped = load_circuitry(save_circuitry(original))`.
3. Assert structural equality.
4. Drive the same input sequence through both models and assert identical outputs.
5. Save the roundtripped model and assert byte-equal output to the first save.

## 11. File-by-file change list

New files:

- `src/framework/registry.py` — the component registry (§8).
- `src/framework/format.py` — `CircuitryFile`, all record types, `save_circuitry`, `load_circuitry`, `to_record` / `from_record` dispatch (§6, §9).
- `src/framework/format_records.py` — the pydantic `BaseModel` subclasses for each component type. Split out for size; format.py imports from here.
- `tests/framework/test_format_roundtrip.py` — the parametrised round-trip test (§10).
- `tests/framework/test_format_schema.py` — pydantic-schema-level tests (unknown component type rejected, bad refdes pattern rejected, missing required field rejected, unknown top-level keys rejected, format version mismatch rejected).

Modified files:

- `pyproject.toml` (or equivalent) — add `pydantic>=2.0` to dependencies. (User runs Python 3.14 per the venv path, so v2 is the only choice.)
- `src/framework/pin.py` — migrate `PinId` to `pydantic.dataclasses.dataclass` per §5.2; add `@validate_call` to `Pin.__init__`, `Pin.other_face`.
- `src/framework/refdes.py` — `validate_refdes` slimmed per §5.4 (or fully replaced by pydantic field constraints inline on each component's `refdes_number`).
- `src/framework/wire.py` — add `@validate_call` on `wire`; relationship checks stay hand-rolled.
- `src/framework/mate.py` — add `@validate_call` on `mate`.
- `src/framework/connector.py` — add `@validate_call` on `Connector.__init__`; add `@register(...)` to every concrete connector class (in the connector library files).
- `src/framework/circuit.py` — add `@validate_call` on `Circuit.__init__`. The logical-net validator from the board-connector spec is untouched.
- `src/framework/chip.py` — add `@validate_call` on `Chip.__init__`.
- `src/framework/board.py` — add `@validate_call` on `Board.__init__`; register `Board` with the registry.
- `src/components/passives/resistor.py`, `led.py`, `rail.py` — add `@validate_call` on `__init__` and `__call__`; register each.
- `src/components/chips/sn74hc04.py`, `cd4069.py`, `lm393.py`, `cd4043.py`, `uln2003a.py` — add `@validate_call` and `@register` (using the bare class name).
- `src/components/connectors/*.py` — every connector class gets `@register`.
- `src/framework/ground.py` — `Ground` registered (note: `Ground` itself doesn't carry refdes but does need to round-trip; record format uses a synthesised `Ground_n` id).
- `src/applications/water_alarm.py` and `water_alarm_split/*.py` — no source edits required; they continue to work and are now round-trip-testable.

Unmodified:

- `src/framework/port.py`, `node.py`, `signals.py`, `units.py`, `factor.py` — these primitives are constructed by other framework code, not by the user. Their `__init__` arguments are already validated by the calling code's validation.

## 12. Test plan

`tests/framework/test_pydantic_adoption.py`:

1. **PinId rejects bad inputs.** `PinId(0, 'X')`, `PinId(-1, 'X')`, `PinId(1, '')`, `PinId(True, 'X')` all raise `pydantic.ValidationError`. (Existing PinId tests updated to assert the new exception type.)
2. **Component `__init__` validation kicks in.** `Resistor(ohms=-10, refdes_number=1)` raises `ValidationError` (negative resistance). `Resistor(ohms=10, refdes_number=0)` raises (zero refdes number). `LED(color='', refdes_number=1)` raises (empty color string).
3. **`mate()` validates argument types.** `mate("not a connector", real_connector)` raises `ValidationError` (a string isn't a `Connector`).
4. **`wire()` validates argument types.** `wire("not a port")` raises `ValidationError`.
5. **`Pin.other_face` validates.** `pin.other_face("not a port")` raises `ValidationError`.

`tests/framework/test_registry.py`:

6. **Registered components are looked up.** `lookup("Resistor") is Resistor`.
7. **Duplicate registration raises.** Re-registering an existing name raises `ValueError` at import time.
8. **Unknown names raise.** `lookup("NonexistentChip")` raises `KeyError` mentioning the known types.

`tests/framework/test_format_schema.py`:

9. **Format-version handling.** Loading a file with `format_version: "2.0.0"` (future major) raises with a clear message naming the unsupported version.
10. **Unknown component type rejected.** A `.circuitry` JSON with `{"type": "FakeChip"}` in `components` raises `ValidationError` at parse time (discriminator union has no `"FakeChip"` arm).
11. **Bad refdes pattern rejected.** A `ResistorRecord` with `refdes: "U1"` (wrong prefix) raises at parse time.
12. **Missing required fields rejected.** A `ResistorRecord` without `ohms` raises.
13. **Extra top-level keys rejected.** `{"format_version": "1.0.0", "root": {...}, "comment": "hello"}` raises (config `extra="forbid"`).
14. **Empty components list is legal.** A board with `components: []` and `wires: []` loads to a board with no parts.

`tests/framework/test_format_roundtrip.py`:

15. **Round-trip preserves structure (parametrised).** For each of `WaterAlarm()`, `SensorBoard(refdes_number=1)`, `ControllerBoard(refdes_number=1)`, `WaterAlarmAssembly()`:
    - Save to temp `.circuitry` file.
    - Load and assert structural equality on (component count, refdes assignments, component values, wire-set as set-of-port-tuples, mate list, surface ports).
    - Drive the same input sequence through both models and assert identical evaluation results.
    - Save the loaded model and byte-compare to the original save.
16. **Determinism.** Two saves of the same model produce byte-identical files.
17. **Hand-edited file loads.** Construct a minimal `.circuitry` file by hand (resistor + LED + Rail wired as a sanity test), load it, assert the model is correct.
18. **Cycle-safe loader.** A `.circuitry` file with a wiring topology that includes a `Pin` walked through (mated connector) loads without infinite recursion. (Regression check against the logical-net walker.)

Existing-test impact: the pin-id tests are updated to assert `pydantic.ValidationError` instead of `TypeError` / `ValueError`. No other test changes required; component behaviour is preserved.

## 13. Acceptance criteria

The work is done when:

1. `python -m pytest` passes including all new tests.
2. `pydantic>=2.0` is in the project's dependencies; the codebase imports from `pydantic` cleanly.
3. `PinId` is a `pydantic.dataclasses.dataclass` and rejects invalid inputs via `pydantic.ValidationError`.
4. Every component class's `__init__` carries `@validate_call`; every argument-bearing framework function and method carries `@validate_call`.
5. The component registry exists; every concrete `FactorNode` subclass (chips, passives, connectors, `Board`) is registered under its bare class name.
6. `save_circuitry(root, path)` writes a valid `.circuitry` file; `load_circuitry(path)` reconstructs the model losslessly.
7. Round-trip is byte-deterministic — two saves of the same design produce identical bytes.
8. The `format_version` field is present and validated; unsupported major versions are rejected at load time.
9. All four existing applications (`WaterAlarm`, `SensorBoard`, `ControllerBoard`, `WaterAlarmAssembly`) round-trip cleanly with identical evaluation behaviour pre- and post-load.
10. No setters added; no public mutators; `__slots__` discipline preserved; physical-fidelity discipline intact.

## 14. Out of scope (for follow-up work packages)

- **Netlist exporters.** SPICE (`.cir`), KiCad netlist (`.net`), EDIF, Yosys JSON. Each is a separate work package that reads a `.circuitry` file and emits the target format. They live in `src/export/spice.py`, `src/export/kicad.py`, etc.
- **Migration tooling between major format versions.** When `format_version` jumps from `1.x.x` to `2.0.0`, an automatic migrator that reads `1.x.x` files and emits `2.0.0` files. Trivial to skip for now (no v2 exists); important once two majors coexist.
- **Schema publication.** Emit a JSON Schema document derived from `CircuitryFile.model_json_schema()` to `docs/circuitry-schema.json` so third-party tools can validate without depending on the Python codebase. Easy to add later; not needed for the round-trip use case.
- **Multi-file projects.** A `.circuitry` file that references another `.circuitry` file by path (sub-boards as files; shared libraries). Useful for large designs; not needed for current scope.
- **Binary / compressed variants.** `.circuitry.gz`, `.circuitry.bson`. Speeds up loading of huge designs at the cost of human-readability. Defer until designs get large.
- **Subclass identity preservation.** Round-tripping a `SensorBoard` currently reconstructs as a `Board` (the registry doesn't know the user's subclasses). Adding a "register-your-subclass" extension lets users opt in.
- **Cache / evaluation-state serialisation.** Saving and reloading a *mid-evaluation* snapshot. Out of scope; the format describes structure, not transient state.
- **Pydantic v3 forward compatibility.** Track only what v2 supports today; revisit when v3 ships.
