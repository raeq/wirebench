# Pydantic Adoption Remediation — Implementation Spec

## 1. Purpose

Close the gap between `docs/circuitry-format-spec.md` as written and the codebase as implemented. The format / registry / round-trip machinery from that spec landed cleanly. The **broad `@validate_call` adoption from §5.3** did not — fewer than a third of the argument-bearing methods carry the decorator, and two of the spec's required tests were softened to assert current loose behaviour rather than the stricter behaviour the spec required.

This spec is a mechanical sweep that finishes that work. It adds nothing new; it just brings the implementation up to the spec as written.

## 2. Scope

**In scope** — adding `@validate_call` to every component class's `__init__` and `__call__` that the original spec listed but the implementation skipped; declaring per-argument field constraints via `Annotated[...]` and `Field(...)` so the new decorators actually catch bad input; restoring the two softened tests in `tests/framework/test_pydantic_adoption.py` to assert `pydantic.ValidationError`; extending the round-trip behavioural-equivalence test to all four applications instead of just `WaterAlarm`.

**Out of scope** — adding pydantic anywhere new in the codebase; refactoring component classes structurally; changing component behaviour beyond what stricter argument validation produces; reopening any decision from the previous specs.

**Prerequisites** — `docs/circuitry-format-spec.md` partially implemented (the format and registry pieces, which are already in place). This spec assumes pydantic v2 is in dependencies, `validate_call` is importable, and the existing tests are green.

## 3. Constraints carried over from CLAUDE.md and prior specs

- Physical fidelity is primary. The decorator and its field constraints describe physical limits of real parts (a resistance cannot be negative, an LED has a non-empty colour, a pin count is a positive integer, a pitch is a positive number of millimetres). Constraints that don't have a physical reading should not be added.
- `__slots__` discipline preserved. `@validate_call` is a function decorator; it does not affect class structure.
- No setters. The decorator validates *call-time* arguments only; it does not introduce mutability.
- Hot-path exemption from the original spec §5.3 stands: if profiling reveals `@validate_call` on `__call__` is in a measurable hot path, the decorator is dropped and a per-class comment notes the deliberate exemption. The default position is "decorate first, profile if it hurts."

## 4. The decorator sweep

### 4.1 Standard import block

Every modified file gets these imports at the top (idempotent — skip if already present):

```python
from typing import Annotated
from pydantic import validate_call, Field, PositiveInt, PositiveFloat
```

`PositiveInt` is `Annotated[int, Field(gt=0)]`; `PositiveFloat` is `Annotated[float, Field(gt=0)]`. They are pydantic v2 conveniences.

### 4.2 Standard decorator form

For every method touched, the decorator form is:

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(self, ...) -> None:
    ...
```

`arbitrary_types_allowed=True` is mandatory because `GroundDomain`, `Ohms`, `Amps`, `Volts`, `Port`, `Pin`, `FactorNode`, `Connector`, `Circuit`, `Board`, `Chip`, `PinId`, and other project types aren't pydantic-known. The config flag tells pydantic to accept them as-is on `isinstance` checks.

### 4.3 Per-component changes

**`src/components/passives/resistor.py` — `Resistor`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    ohms: Annotated[float, Field(gt=0)] | Ohms,
    domain: GroundDomain = ELECTRICAL,
    *,
    refdes_number: PositiveInt,
) -> None:
    ...

@validate_call(config={'arbitrary_types_allowed': True})
def __call__(self, current: float | Amps) -> Volts:
    ...
```

**`src/components/passives/led.py` — `LED`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    color: Annotated[str, Field(min_length=1)],
    domain: GroundDomain = ELECTRICAL,
    *,
    refdes_number: PositiveInt,
) -> None:
    ...

@validate_call(config={'arbitrary_types_allowed': True})
def __call__(self, anode: bool | None) -> bool | None:
    ...
```

**`src/components/passives/rail.py` — `Rail`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    level: bool,
    domain: GroundDomain = ELECTRICAL,
) -> None:
    ...

@validate_call(config={'arbitrary_types_allowed': True})
def __call__(self) -> bool:
    ...
```

`Rail` has no `refdes_number` — it isn't refdes-bearing per the refdes spec.

**`src/components/chips/sn74hc04.py` — `SN74HC04`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    domain: GroundDomain = ELECTRICAL,
    *,
    refdes_number: PositiveInt,
) -> None:
    ...

@validate_call(config={'arbitrary_types_allowed': True})
def __call__(self, *inputs: bool | None) -> tuple:
    ...
```

Variadic `*inputs: bool | None` is supported in pydantic v2's `validate_call`; per-element type-checking applies.

**`src/components/chips/cd4069.py`, `lm393.py`, `cd4043.py`, `uln2003a.py`** — same pattern as `SN74HC04`, with each chip's `__call__` signature preserved (some return tuples, some return single values; `LM393.__call__` takes the two voltage inputs, etc.). Annotate each parameter with its natural type; if a parameter accepts a `float` for voltage it gets `float | None` (preserving existing None semantics for undriven inputs).

**`src/components/chips/concepts/inverter.py`, `comparator.py`, `nor_latch.py`, `tristate_buffer.py`, `darlington_channel.py`** — cell concepts. They don't carry refdes (per refdes spec) but they are user-facing in tests. Same pattern:

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
    ...

@validate_call(config={'arbitrary_types_allowed': True})
def __call__(self, a: bool | None) -> bool | None:   # Inverter
    ...
```

**`src/framework/connector.py` — `Connector`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    *,
    domain: GroundDomain = ELECTRICAL,
    refdes_number: PositiveInt,
    pin_count: PositiveInt | None = None,
    pitch_mm: PositiveFloat | None = None,
) -> None:
    ...
```

The existing under-specified-part check (raises `TypeError` if neither `PIN_COUNT` class attribute nor constructor arg is supplied) stays in the body.

**`src/framework/board.py` — `Board`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    *,
    name: Annotated[str, Field(min_length=1)],
    revision: Annotated[str, Field(min_length=1)],
    components: list[FactorNode],
    refdes_number: PositiveInt,
) -> None:
    ...
```

The hand-rolled empty-string check that currently raises `ValueError` can be removed — `Field(min_length=1)` covers it. Update the corresponding test (test 6 in board+connector spec §13) to assert `pydantic.ValidationError`.

**`src/framework/circuit.py` — `Circuit`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(
    self,
    factor_nodes: list[FactorNode],
    ports: dict[str, Port],
) -> None:
    ...
```

The relationship checks inside `_validate` (mandatory-port connectivity, multi-OUT short, floating-net detection) stay hand-rolled — pydantic doesn't express cross-field invariants like those.

**`src/framework/chip.py` — `Chip`**

```python
@validate_call(config={'arbitrary_types_allowed': True})
def __init__(self, *, pins: list[Pin], cells: list[FactorNode]) -> None:
    ...
```

### 4.4 Hot-path discipline

The original §5.3 says: *"If profiling reveals `@validate_call` on `__call__` is in a measurable hot path, the decorator is removed and a per-class comment notes the deliberate exemption."*

For this remediation, the default is **decorate first, profile if it hurts**. The four applications in the round-trip test (`WaterAlarm`, `SensorBoard`, `ControllerBoard`, `WaterAlarmAssembly`) drive only a handful of input cycles per test run; pydantic validation overhead is negligible at that scale. If a future stress test or simulation use case shows the validation in a hot loop, that's where exemptions get added, with a comment naming the benchmark that justified each.

No exemptions are added in this work package.

### 4.5 Existing `validate_refdes` and hand-rolled checks

The hand-rolled `validate_refdes()` from `src/framework/refdes.py` is currently called from inside each component's `__init__`. After this sweep, `refdes_number: PositiveInt` in each `__init__` covers the integer-positivity part; the prefix-in-`IEEE_315_PREFIXES` part stays in `validate_refdes()` because it depends on the class attribute, not on the argument.

Option (preferred for elegance, optional for this work package): the prefix check becomes a class-level assertion via `__init_subclass__` instead of a per-instance check. Class definitions that pick a bad prefix fail at import time. This eliminates `validate_refdes()` entirely. Mark as out-of-scope if it conflicts with anything; otherwise apply.

`wire()`'s relationship checks stay hand-rolled (they're cross-argument, not per-argument). `Pin.evaluate`'s BIDIR contention check stays — it's runtime logic, not validation.

## 5. The two softened tests

### 5.1 `tests/framework/test_pydantic_adoption.py` — `test_resistor_rejects_negative_ohms`

**Current (softened) form:** documents that `Resistor(ohms=-10, refdes_number=1)` succeeds and notes "Resistor doesn't yet wrap @validate_call."

**Required form:**

```python
def test_resistor_rejects_negative_ohms() -> None:
    """Per spec §12 #2 — negative resistance is physically impossible."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Resistor(ohms=-10, refdes_number=1)
    with pytest.raises(ValidationError):
        Resistor(ohms=0, refdes_number=1)
```

### 5.2 `tests/framework/test_pydantic_adoption.py` — `test_led_rejects_empty_color`

**Current (softened) form:** accepts `LED(color='red')` and never tests the empty string.

**Required form:**

```python
def test_led_rejects_empty_color() -> None:
    """Per spec §12 #2 — LED must have a non-empty color string."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        LED(color='', refdes_number=1)
```

Both tests pass once the corresponding `@validate_call` decorators land in §4.3.

## 6. Round-trip behavioural-equivalence test extension

`tests/framework/test_format_roundtrip.py::test_roundtrip_water_alarm_behaves_identically` currently exercises only `WaterAlarm`. Per `circuitry-format-spec.md` §10, equivalence must be checked for all four applications.

Add three parametrised cases — one per application that takes input drive:

```python
@pytest.mark.parametrize('builder, drive_sequence', [
    (lambda: WaterAlarm(),
     [(False, False), (True, False), (True, True), (False, False)]),
    (lambda: WaterAlarmAssembly(),
     [(False, False), (True, False), (True, True), (False, False)]),
    # SensorBoard and ControllerBoard don't have user-driveable surface ports
    # in the same shape — for those, drive the appropriate surface port and
    # observe the appropriate output, then compare original vs. loaded.
])
def test_roundtrip_behaviour_equivalence(builder, drive_sequence, tmp_path) -> None:
    original = builder()
    path = tmp_path / 'test.circuitry'
    save_circuitry(original, path)
    loaded = load_circuitry(path)

    for inputs in drive_sequence:
        original_out = original(*inputs)
        loaded_out   = loaded(*inputs)
        assert original_out == loaded_out, (
            f"Behavioural divergence at inputs={inputs}: "
            f"original={original_out!r}, loaded={loaded_out!r}"
        )
```

`SensorBoard` and `ControllerBoard` standalone aren't driven the same way as their parent assembly (they expect signals on their connector pin internals, not on probe-style surface ports). For those two: drive an appropriate header pin's external face with a representative sequence, evaluate, and compare the same output port's value pre- and post-load. The exact pin choice is the implementer's call; the test's goal is *parity*, not behavioural meaningfulness.

## 7. File-by-file change list

Modified files (only — no new files in this work package):

- `src/components/passives/resistor.py` — `@validate_call` on `__init__` and `__call__` per §4.3; pydantic-style constraints on `ohms` and `refdes_number`.
- `src/components/passives/led.py` — same for `LED`; `color` becomes `Annotated[str, Field(min_length=1)]`.
- `src/components/passives/rail.py` — `@validate_call` on `__init__` and `__call__`.
- `src/components/chips/sn74hc04.py` — `@validate_call` on `__init__` and `__call__` (variadic `*inputs`).
- `src/components/chips/cd4069.py` — same.
- `src/components/chips/lm393.py` — same; `__call__` takes voltage inputs.
- `src/components/chips/cd4043.py` — same.
- `src/components/chips/uln2003a.py` — same.
- `src/components/chips/concepts/inverter.py` — `@validate_call` on `__init__` and `__call__`.
- `src/components/chips/concepts/comparator.py` — same.
- `src/components/chips/concepts/nor_latch.py` — same.
- `src/components/chips/concepts/tristate_buffer.py` — same.
- `src/components/chips/concepts/darlington_channel.py` — same.
- `src/framework/connector.py` — `@validate_call` on `Connector.__init__` with `PositiveInt` / `PositiveFloat` constraints on `pin_count` and `pitch_mm`.
- `src/framework/board.py` — `@validate_call` on `Board.__init__` with `min_length=1` on `name` and `revision`; remove the now-redundant hand-rolled empty-string check.
- `src/framework/circuit.py` — `@validate_call` on `Circuit.__init__`.
- `src/framework/chip.py` — `@validate_call` on `Chip.__init__`.
- `src/framework/refdes.py` — optional simplification per §4.5 (move prefix check to `__init_subclass__`); otherwise unchanged.
- `tests/framework/test_pydantic_adoption.py` — restore §12 #2 and #3 per §5 above; ensure the file no longer contains comments noting "current loose behaviour."
- `tests/framework/test_format_roundtrip.py` — extend behavioural-equivalence to all four applications per §6.
- `tests/applications/test_water_alarm.py` (if it exists) and any other test that calls these constructors with invalid arguments and currently expects `ValueError` / `TypeError`: update assertions to `pydantic.ValidationError` if applicable. Spot-check during implementation.

Unmodified:

- `src/framework/pin.py`, `wire.py`, `mate.py`, `format.py`, `format_records.py`, `registry.py`, `factor.py`, `port.py`, `node.py`, `ground.py`, `signals.py`, `units.py` — already done in the first pass or never required.
- `src/components/connectors/*.py` — connector subclasses inherit `Connector.__init__`; the decorator there covers them.
- `src/applications/water_alarm.py` and `water_alarm_split/*.py` — no source edits; behaviour is preserved through the stricter constructors.

## 8. Test plan

The bar is: **every spec test that was softened or skipped now passes against the spec as written**.

1. `test_resistor_rejects_negative_ohms` (and zero ohms) — passes per §5.1.
2. `test_led_rejects_empty_color` — passes per §5.2.
3. **`test_chip_rejects_invalid_refdes`** — new. `SN74HC04(refdes_number=0)`, `SN74HC04(refdes_number=-1)`, `SN74HC04(refdes_number=1.5)`, `SN74HC04(refdes_number=True)` all raise `pydantic.ValidationError`. Similar for one passive (`Resistor`).
4. **`test_connector_rejects_invalid_pin_count`** — new. `Header2xNMale(pin_count=0, pitch_mm=2.54, refdes_number=1)` raises; `Header2xNMale(pin_count=-1, pitch_mm=2.54, refdes_number=1)` raises; `Header2xNMale(pin_count=10, pitch_mm=0, refdes_number=1)` raises; `Header2xNMale(pin_count=10, pitch_mm=-2.54, refdes_number=1)` raises.
5. **`test_board_rejects_empty_name_and_revision`** — new. `Board(name='', revision='A', components=[], refdes_number=1)` raises `ValidationError`; same for empty revision. (Replaces the existing hand-rolled `ValueError` test if any.)
6. **`test_call_path_validates_inputs`** — new. `Resistor(330, refdes_number=1)(current='hot')` raises (string isn't `float | Amps`). `LED('red', refdes_number=1)(anode='maybe')` raises (string isn't `bool | None`).
7. **`test_roundtrip_behaviour_equivalence`** (parametrised) — passes for `WaterAlarm`, `WaterAlarmAssembly`, `SensorBoard`, `ControllerBoard` per §6.
8. **Existing 287 tests** — all continue to pass. The decorator adds validation, not behaviour change, so structural and behavioural tests for valid inputs are unaffected. The two previously-softened tests (now restored) pass for the right reason: the decorator catches the bad input.

## 9. Acceptance criteria

The remediation is done when:

1. `python -m pytest` passes, with the test count up by at least the additions in §8 (4 new tests minimum, plus parametrisation of round-trip behavioural equivalence).
2. Every component `__init__` and `__call__` listed in §4.3 carries `@validate_call(config={'arbitrary_types_allowed': True})`.
3. Per-argument constraints (`Annotated`, `Field`, `PositiveInt`, `PositiveFloat`) are present where the spec defines them.
4. The two softened tests in `test_pydantic_adoption.py` are restored — they assert `pydantic.ValidationError` and pass against the now-decorated `Resistor.__init__` and `LED.__init__`.
5. Round-trip behavioural equivalence covers all four applications in `test_format_roundtrip.py`, not just `WaterAlarm`.
6. No new tests are softened to accommodate undecorated code paths. If a test fails because the decorator is missing somewhere, the fix is *to add the decorator*, not to lower the test bar.
7. The original `circuitry-format-spec.md` acceptance criterion #4 ("every component class's `__init__` carries `@validate_call`") is now true.

## 10. Out of scope (for follow-up)

- **Performance benchmarking and selective exemption.** The default is "decorate everywhere." If a downstream simulator-style use case shows real overhead, add a separate work package to profile and exempt specific hot-path `__call__`s with explicit comments.
- **Replacing `validate_refdes` entirely.** §4.5 mentions a `__init_subclass__`-based prefix check that would let `validate_refdes()` be deleted. Optional now; can be done here or deferred.
- **Cross-argument validation via `model_validator`.** `wire()` and `Circuit._validate` have relationship rules that pydantic doesn't express well. Keep them hand-rolled.
- **Generating the JSON Schema document.** `CircuitryFile.model_json_schema()` would emit a publishable schema. Useful for third-party tools; not needed for round-trip and not addressed here.
- **Deeper format-version migration tooling.** Same as the original format spec's deferral.
