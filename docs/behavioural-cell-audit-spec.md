# Behavioural-Cell Audit — Implementation Spec

## 1. Purpose

A latent defect surfaced during the `demos/5v_rail_power/` work: the framework's logical-net ERC walks through `IS_CONDUCTOR` components (chip pins, connector contacts) looking for a real driver on the other side, and if the chip on that side ships with `cells=[]` — no internal behavioural cell driving its OUT pin's internal face — the entire downstream net is "floating" from the framework's perspective. The framework refuses to construct the design with `FloatingNetError`, *correctly* by its own rules. The problem is that many components in the library *do* ship with `cells=[]` despite having a directional behaviour (LM7805 driving OUTPUT from INPUT, 1N5817 conducting cathode from anode, opamp driving its output from its inputs, transistor switching its drain based on gate, etc.). Any design that places one of these components in the middle of a drive path will raise `FloatingNetError` — even though the design is correct in the real world.

This work package is an **audit**: a systematic walk of every registered component class in the library, identifying which ones have unmodelled directional behaviour, implementing the missing behavioural cells, and establishing a regression test that prevents this category of latent defect from accruing again.

The user's standard: *"I need a dependable framework or no framework at all."* The audit is what raises the project from "passes its existing tests" to "passes a test that would have caught the supply-chain limitation before a beginner did."

## 2. Scope

**In scope** — a complete classification of every registered component class into one of three audit categories (passive, behavioural-cell-needed, application-firmware-driven); implementation of every missing behavioural cell across the library; a new framework-level regression test (`test_behavioural_completeness.py`) that walks every class in the registry and verifies it constructs cleanly in a minimal valid topology; an audit of the existing `backup_power` demo (which the user specifically called out as suspicious — its TPS2660 / LM5002 / LM5160 chips are believed to be black-box and would otherwise have surfaced this same issue); per-class behavioural-cell tests that drive each component through its parameter space and assert outputs match the modelled behaviour.

**Out of scope** — physical-fidelity SPICE-grade modelling of analog parts (the cells produce *topologically correct* drive paths with quantitatively reasonable but not vendor-accurate output values; SPICE simulation remains the right tool for analog accuracy); cell-level audits for the existing concept classes (`Inverter`, `Comparator`, `NORLatch`, etc. — these are already correct by virtue of being how the working demos pass ERC); modelling firmware behaviour for microcontrollers in their bare form (MCU classes legitimately ship without firmware cells — users add firmware cells via subclassing per the `Uno_ThermometerSketch` pattern); auditing component classes that have no OUT pins at all (purely-passive parts: Resistor, Capacitor, Rail, Connector — these can't have unmodelled directional behaviour because they have no directional surface).

**Prerequisites** — all previous specs implemented and verified. This work assumes the existing `compute_logical_nets`, `IS_CONDUCTOR` walker, `Circuit._validate`, the renderer registry, the component registry, and the `Cell`-style cell concept pattern (per `framework/chip.py`'s `__init__(pins, cells)` contract).

## 3. The class of defect

The defect being audited has this exact shape:

```python
class SomeChip(Chip):
    """A chip with a directional behaviour described in its datasheet."""

    _PIN_TABLE: ClassVar = (
        (1, 'INPUT',  Direction.IN,  Analog),
        (2, 'OUTPUT', Direction.OUT, Analog),
        ...
    )

    def __init__(self, ...) -> None:
        pins = [Pin(...) for ... in self._PIN_TABLE]
        super().__init__(pins=pins, cells=[])    # ← THE DEFECT
```

`cells=[]` means no internal cell drives the OUTPUT pin's internal face. The framework's logical-net walker, encountering a logical net that contains `chip.OUTPUT.external`, walks *through* the Pin (because `Pin.IS_CONDUCTOR=True`) to the internal face, finds it undriven, and reports the entire downstream net as floating.

The fix is to instantiate a behavioural cell, wire its output(s) to the relevant pin internals, and pass `cells=[the_cell]` to `super().__init__`. The cell's `evaluate()` reads its input port(s) and drives its output port(s) based on the modelled behaviour. The framework then sees the cell as a real driver on the chip's internal mesh; the IS_CONDUCTOR walk through the OUTPUT pin terminates at the cell's OUT port; the downstream net has a driver; ERC accepts the design.

**The defect is not a framework bug** — the framework is correctly enforcing physical reality (a chip that doesn't drive its OUT does nothing). The defect is *incomplete component modelling*: a class that declares an OUT pin without backing it with an evaluate-able driver is making a false promise.

## 4. CLAUDE.md constraints carried forward

- Physical fidelity is primary. Every behavioural cell describes what the real silicon does, not a software shortcut.
- `__slots__` discipline preserved on every new cell class.
- No setters; cell state (where it exists) is read-only after construction.
- Pydantic `@validate_call` on every public method.
- New cell classes follow the established concept-class pattern under `src/components/chips/concepts/` (or a sibling directory for non-chip behaviours).
- The behavioural cells are *internal* to their owning components — concepts that consumers shouldn't see directly. The chip's external surface is its pins; the cell's existence is an implementation detail.
- No inheritance between component types; cells compose into chips, they don't form hierarchies.

## 5. The audit procedure

The audit walks every class in the component registry and assigns it to one of three categories:

**Category A — Passive.** Has no OUT pins, or has only OUT pins on conductors (Pin.IS_CONDUCTOR=True acting as transparent wires). Examples: `Resistor`, `Capacitor`, `Rail`, every `Connector` subclass. No cell needed. The framework's existing logic handles these correctly.

**Category B — Behavioural-cell-needed.** Has one or more OUT pins (or input-driven BIDIR pins) whose values should be derived from the chip's input pins via a modelled function. Examples: linear regulators, forward-conducting diodes, transistors as switches, opamps, comparators, optocouplers, RS-232 drivers, oscillator ICs. The audit identifies the cell pattern, implements it, instantiates it in the chip's `__init__`.

**Category C — Application-firmware-driven.** Has OUT pins whose values are determined by code the chip executes, not by a function of its input pins alone. Examples: microcontrollers, FPGAs. The framework can't model "what firmware does"; instead, users subclass the bare chip and inject a private firmware-as-cell (per `Uno_ThermometerSketch`, `Uno_BLDCCommutator`, etc.). The bare chip legitimately ships without cells; the regression test for Category-C classes uses a stub "all-pins-driven-from-VCC" cell as the application stand-in.

**The audit's deliverable** is `docs/behavioural-cell-audit.md` — a markdown table with one row per registered class, columns: `Class`, `Category`, `Cell instantiated`, `Audit status` (`pass` if already correct, `fix-needed` if requires implementation), and `Notes`. The implementer fills this table during the audit walk; the regression test cross-references it.

### 5.1 Per-class audit procedure

For each registered class `C`:

1. **Inspect `C._PIN_TABLE` (or equivalent).** Categorise every pin by direction:
   - All pins are IN or BIDIR-passive (no OUTs): **Category A**. Continue.
   - At least one OUT pin: check whether `C.__init__` instantiates and wires a behavioural cell. If yes → **Category A** (already covered). If no → continue.
   - At least one OUT pin and the chip is fundamentally firmware-driven (MCU, FPGA): **Category C**. Document the firmware-cell pattern users should follow.
   - At least one OUT pin and the behaviour is a deterministic function of the input pins: **Category B**. Identify the function and write the cell.

2. **Identify the behavioural cell pattern** (Category B only). The cell's input ports correspond to the chip's input pins; the cell's output ports correspond to the chip's output pins; the cell's `evaluate()` implements the modelled function (e.g. `output = clamp(input - dropout, 0, max_output)` for a linear regulator).

3. **Implement the cell** in `src/components/chips/concepts/`.

4. **Wire the cell into the chip's `__init__`.** Connect each `cell.input.external` (no, wait — concept cells aren't `Pin`s; they're plain `FactorNode`s with `Port`s) to the matching `chip_pin.internal`. Pass `cells=[the_cell]` to `super().__init__`.

5. **Add a behavioural test** in `tests/components/test_<class_lower>.py` that drives the chip through its parameter space and asserts the cell's output matches the modelled behaviour. (Per-cell unit tests live in `tests/components/concepts/test_<cell>.py`.)

6. **Run the regression test** (next section) to verify the chip now constructs cleanly in the minimal-supply-chain topology.

## 6. Defence in depth: construction-time enforcement + regression test

Two coordinated defences. The **primary** one is at the type system: `Chip` (and every other framework base class with a directional contract) refuses to construct a subclass whose declared OUT pins aren't backed by an internal driver. A contributor adding a new chip class with `cells=[]` and an OUT pin doesn't get a passing unit test that they then have to remember to extend — they get a `PartConfigurationError` raised the first time they try to instantiate the class. The defect is *unconstructible*.

The **secondary** defence is the regression test that walks every class in the registry. It catches anyone who subclasses `Chip` directly to bypass the primary check, or who incorrectly sets the `BARE_FIRMWARE_DRIVEN` opt-out flag, or who adds a non-`Chip` directional component the primary check doesn't cover yet. It is a belt-and-braces backstop, not the load-bearing constraint.

The two defences together change the trust statement from *"we test for this defect"* to *"the framework cannot construct a component with this defect, and the test confirms it"*.

### 6.1 Construction-time invariant enforcement (primary defence)

**The invariant.** Every `Chip` subclass must drive every pin it declares as `Direction.OUT`. "Drive" means a behavioural cell instantiated in the chip's `__init__` has an OUT (or active-BIDIR) port wired to the chip pin's internal face.

**Where it lives.** In `framework/chip.py`'s `Chip.__init__`, after the user's chip-class `__init__` completes constructing pins and cells. The check walks every pin; for each OUT pin it asserts the internal-face invariant. Violations raise `PartConfigurationError` from the framework's existing error hierarchy.

```python
class Chip(Circuit):
    # Opt-out flag for chip classes that legitimately ship without
    # behavioural cells because their OUT pins are driven by
    # something *outside* the chip class itself — namely, user
    # firmware injected via subclassing.  Set this True on bare
    # MCU classes.  Every other use is wrong: add a behavioural
    # cell instead.
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = False

    def __init__(self, *, pins: list[Pin], cells: list[FactorNode]) -> None:
        # … existing pin/cell wiring and super().__init__ …

        if not self.BARE_FIRMWARE_DRIVEN:
            self._assert_every_out_pin_is_internally_driven(pins)

    def _assert_every_out_pin_is_internally_driven(
        self, pins: list[Pin],
    ) -> None:
        """Refuse to construct a Chip whose declared OUT pins aren't
        backed by an internal driver. This is the construction-time
        enforcement of the contract behavioural cells exist to
        satisfy. Without this check, a chip class with cells=[] and
        an OUT pin compiles, instantiates, and silently produces
        floating nets in any design that uses it — the defect class
        documented in §3 of this spec."""
        for pin in pins:
            if pin._role is not Direction.OUT:
                continue
            internal = pin.internal
            has_driver = (
                internal.node is not None
                and any(
                    p is not internal
                    and (
                        p.direction is Direction.OUT
                        or (p.direction is Direction.BIDIR and p.can_drive)
                    )
                    for p in internal.node.ports
                )
            )
            if not has_driver:
                raise PartConfigurationError(
                    f"{type(self).__name__} declares pin "
                    f"{pin.id.name!r} (pin {pin.id.number}) as "
                    f"Direction.OUT but no behavioural cell drives its "
                    f"internal face. Add a cell to __init__ that drives "
                    f"this pin's internal face, or — if this chip is "
                    f"firmware-driven — set BARE_FIRMWARE_DRIVEN=True on "
                    f"the class. See docs/behavioural-cell-audit-spec.md "
                    f"for the cell pattern."
                )
```

**The opt-out (`BARE_FIRMWARE_DRIVEN`)** is the *only* legitimate way to skip the check. The semantics are explicit: "this class ships without cells *on purpose* because user firmware drives the pins." Set it on every MCU class (Category C); every other use should be flagged at code-review time. The flag's presence in source is the design statement that justifies the missing cells.

**Order of operations.** This check would refuse to construct *every existing chip that lacks a cell* the moment it lands. So the order is non-negotiable:

1. First, **land the audit fixes** (every chip in §7.2 gains its behavioural cell). The check would already pass for the chips covered by §7.2 once they're fixed.
2. Then, **turn on the check** in `Chip.__init__`. From that moment on, no new chip class can ship with the defect.
3. The regression test in §6.2 backs this up.

**Coverage beyond `Chip`.** The same pattern applies in principle to other framework base classes with directional contracts, but for this work package the check only lands on `Chip`. The rationale:

- **`Diode`** — diodes are **Category A passive** per the §7.2.2 decision. Their directional function is modelled at the *circuit level* (via `SeriesRectifier`, `ZenerShunt`, or the existing `DiodeOR` pattern in the `dice` demo) alongside the passive part. There is therefore no per-class invariant for `Diode` to enforce: a diode class with `cells=[]` is correct, not defective. No `Diode.__init__` check is added.
- **`Transistor`** (if a framework base class is introduced as part of §7.2.4; otherwise per-class) — every transistor subclass instantiates a `BJTSwitch` / `MOSFETSwitch` cell because a transistor in circuit *is* the active element on its collector/drain net. Add the analogous check when the base class lands.

For day one of this work package, the only framework base class whose `__init__` enforces the invariant is `Chip`. Transistors get their cells, but their construction-time check is sequenced with the §7.2.4 transistor work.

### 6.2 The regression test (secondary defence)

This is the belt-and-braces backstop. It walks every Category-A and Category-B class in the registry and asserts each can be placed in a minimal valid topology without raising `FloatingNetError` or any other ERC error. Category-C classes use a stub firmware cell to stand in for the user's application code.

The test catches: subclasses that bypass the primary check by subclassing `Chip` directly without going through a base class; incorrect use of `BARE_FIRMWARE_DRIVEN` (an MCU subclass that genuinely has unmodelled OUTs and shouldn't be opting out); non-`Chip` directional components that the primary check doesn't yet cover; topology-level errors that aren't construction-time invariants (e.g., a cell-instantiated chip used in a context that the cell's behaviour can't drive).

The test file is `tests/framework/test_behavioural_completeness.py`. Its skeleton:

```python
import pytest
from framework.registry import _REGISTRY
from framework.errors import CircuitryError

# Import every component sub-package so registrations happen.
import components.chips       # noqa: F401
import components.passives    # noqa: F401
import components.connectors  # noqa: F401
import components.transistors # noqa: F401
import components.diodes      # noqa: F401


# Per-class minimal-topology fixtures.  Keys are class names from
# the registry; values are factory functions that build a minimal
# Circuit containing the class and rails as needed, with all the
# wiring required to make the class's input pins driven.
_MINIMAL_FIXTURES: dict[str, Callable[[], Circuit]] = {
    'Resistor':   lambda: _wrap_two_terminal(Resistor(330, refdes_number=1)),
    'LED':        lambda: _wrap_two_terminal(LED('red', refdes_number=1)),
    'LM7805':     lambda: _wrap_linear_regulator(LM7805(refdes_number=1)),
    'D1N5817':    lambda: _wrap_diode(D1N5817(refdes_number=1)),
    # … one entry per registered class
}


@pytest.mark.parametrize('name', sorted(_REGISTRY))
def test_class_constructs_in_minimal_topology(name: str) -> None:
    """Every registered class must construct in a minimal valid
    topology.  If this raises FloatingNetError or any other
    CircuitryError, the class has unmodelled directional behaviour
    that prevents it from being used in real designs."""
    fixture = _MINIMAL_FIXTURES.get(name)
    if fixture is None:
        pytest.fail(
            f"No minimal-topology fixture for class {name!r}. "
            f"Add one to _MINIMAL_FIXTURES in this test file, "
            f"following the patterns documented in "
            f"docs/behavioural-cell-audit-spec.md §6.1."
        )
    # If the class is Category C (firmware-driven), the fixture
    # wraps it with a stub firmware cell; the result should still
    # construct cleanly.
    circuit = fixture()
    assert circuit is not None
```

### 6.3 Fixture patterns

The fixtures follow a small set of standardised topologies:

**`_wrap_two_terminal(part)`** — for any 2-terminal passive (resistor, LED, capacitor, diode, single transistor lead-pair):

```
Rail(True) → part → Rail(False)
```

The part is the only thing between the rails. For directional parts (diodes), the anode goes to `Rail(True)` and cathode to `Rail(False)`.

**`_wrap_linear_regulator(part)`** — for any linear regulator chip:

```
Rail(True) → part.INPUT, part.GND ← Rail(False)
part.OUTPUT → load (LED + resistor to Rail(False))
```

The load is a real driver-readable element (an LED) so the regulator's OUTPUT pin's net has a real reader as well as a driver.

**`_wrap_diode(part)`** — for any forward-conducting diode (`D1N4148`, `D1N4001`, `D1N4007`, `D1N5817`):

```
Rail(True) → part.anode, part.cathode → load (LED + resistor to Rail(False))
```

**`_wrap_zener(part)`** — for any Zener diode (`D1N4733A`, `D1N4742A`):

```
Rail(True) → resistor → part.cathode, part.anode → Rail(False)
```

Reverse-biased shunt configuration (the canonical Zener use case). The Rail at the top drives the net; the Zener is a passive BIDIR on the net.

**`_wrap_transistor_switch(part, kind='bjt'|'mosfet')`** — for any discrete transistor:

```
Rail(True) → load (LED + resistor) → part.collector/drain
Rail(True or False) → part.base/gate
part.emitter/source → Rail(False)
```

**`_wrap_opamp(part)`** — for any opamp chip:

```
non-inverting input ← Rail(True)
inverting input ← part.OUT (unity-gain buffer)
part.V_POS ← Rail(True), part.V_GND ← Rail(False)
part.OUT → load (LED + resistor to Rail(False))
```

**`_wrap_comparator(part)`** — like opamp but no feedback:

```
non-inverting input ← Rail(True)
inverting input ← Rail(False)
part.V_POS ← Rail(True), part.V_GND ← Rail(False)
part.OUT → load
```

**`_wrap_optocoupler(part)`** — for any optocoupler:

```
Rail(True) → resistor → part.anode → part.cathode → Rail(False)
part.collector → load → Rail(True)
part.emitter → Rail(False)
```

**`_wrap_specialty(part)`** — for ICs with specific topology requirements (NE555 needs RC timing, MAX232 needs charge-pump caps, MAX7219 needs SPI bus stimulation, DS18B20 needs 1-Wire bus). The fixtures here are part-specific and the longest of the bunch. Each one wraps the chip in its datasheet-canonical "smoke test" topology.

**`_wrap_mcu(part)` (Category C)** — for any microcontroller:

```
stub_firmware_cell = _StubFirmwareCell(drive_all_outputs_high=True)
chip.<each Port pin>.internal ← stub_firmware_cell.<corresponding output>
Rail(True) → chip.VCC, Rail(False) → chip.GND
```

The stub firmware cell drives every GPIO to a known state (e.g. all HIGH or per-pin configurable). This stands in for whatever the user's actual firmware will do.

**`_wrap_sensor(part)`** — for sensors whose behaviour depends on Python state (TMP36 with `temperature_c`, BMP280 with `pressure_pa`, etc.). The fixture sets a known state on the part and asserts the output port reflects it.

### 6.4 Coverage guarantee

The parametrised test asserts every entry in `_REGISTRY` has a matching fixture, and every fixture constructs cleanly. Adding a new component class without adding a fixture causes the test to fail with a clear "add a fixture" message — making it impossible to ship a new class that hasn't been audited.

## 7. Per-category analysis

This section walks every registered class and assigns its category. The implementer fills `docs/behavioural-cell-audit.md` from this analysis during implementation.

### 7.1 Category A — Passive (no cell needed)

These classes have no OUT pins or only OUT pins on conductor structures:

- **Passives**: `Resistor`, `Capacitor`, `LED` (anode is IN, cathode is IN — passive 2-terminal), `Rail` (declared OUT, but is itself a driver — not a chip with cells).
- **All connector classes** under `src/components/connectors/` — every connector is built from `Pin` instances which are conductors; the connector is transparent in ERC walks. No internal driver needed.

### 7.2 Category B — Behavioural cell needed

#### 7.2.1 Linear regulators

**New cell**: `LinearRegulator` in `src/components/chips/concepts/linear_regulator.py`.

```python
@register('LinearRegulator')
class LinearRegulator(FactorNode):
    __slots__ = ('_ports',)

    OUTPUT_VOLTAGE: ClassVar[float]   # set by container
    DROPOUT_V:      ClassVar[float]

    def __init__(self, output_voltage: float, dropout_v: float,
                 domain: GroundDomain = ELECTRICAL) -> None:
        self._output_voltage = float(output_voltage)
        self._dropout_v = float(dropout_v)
        self._ports = {
            'v_in':  Port('v_in',  Direction.IN,  domain,
                          mandatory=True, signal_type=Analog),
            'v_out': Port('v_out', Direction.OUT, domain,
                          mandatory=False, signal_type=Analog),
            'gnd':   Port('gnd',   Direction.IN,  domain,
                          mandatory=True, signal_type=Analog),
        }

    def evaluate(self) -> None:
        v_in = self._ports['v_in'].value or 0.0
        v_gnd = self._ports['gnd'].value or 0.0
        v_unclamped = (v_in - v_gnd) - self._dropout_v
        v_regulated = max(0.0, min(self._output_voltage, v_unclamped))
        self._ports['v_out'].drive(v_gnd + v_regulated)
```

**Affected classes** (each instantiates a `LinearRegulator` with appropriate constants and wires it):

| Class            | OUTPUT_VOLTAGE | DROPOUT_V | Notes                                     |
|------------------|---------------:|----------:|-------------------------------------------|
| `LM7805`         | 5.0            | 2.0       | TO-220, standard +5 V                     |
| `LM7812`         | 12.0           | 2.0       | TO-220, standard +12 V                    |
| `LM7905`         | -5.0           | 2.0       | TO-220, **negative** rail (sign-flipped)  |
| `LM317`          | configurable   | 2.0       | adjustable; output set via constructor arg |
| `LM337`          | configurable   | 2.0       | adjustable negative                       |
| `AMS1117_33`     | 3.3            | 1.1       | SOT-223, fixed 3.3 V LDO                  |
| `AMS1117_50`     | 5.0            | 1.1       | SOT-223, fixed 5.0 V LDO                  |
| `LP2950`         | 5.0            | 0.4       | TO-92, low-dropout                        |

For LM7905 / LM337 (negative), the cell needs a sign flip — wire `v_in` to the chip's INPUT pin (which is at GND for negative regulators in normal operation) and `gnd` to the negative supply. Or use a `NegativeLinearRegulator` cell variant. The implementer picks the cleanest representation; the audit table records the choice.

#### 7.2.2 Forward-conducting diodes — passive parts, behaviour at circuit level

**Decision (revised from earlier draft):** forward-conducting diodes (`D1N4148`, `D1N4001`, `D1N4007`, `D1N5817`) are **Category A — passive**. They do not ship with a behavioural cell baked into the class.

Why: a diode is a passive part on the BOM; the directional function it performs is a property of the *circuit* using it, not of the part itself. The same 1N4148 sits in:

- An OR matrix (the `dice` demo) — six diodes' cathodes share a net; the OR-ing function is modelled by a separate `DiodeOR(FactorNode)` cell at the circuit level.
- A series rectifier (the `5v_rail_power` demo) — one diode in the supply path; the rectifier function is modelled by a separate `SeriesRectifier(FactorNode)` cell.
- A flyback across a relay coil (the `doorbell_protector` demo) — passive on an already-driven net; no behavioural cell needed.

Baking a `DiodeForward` cell into every diode class would (a) short the dice's OR matrix by putting six drivers on the OR net and (b) impose a single role on a part that has multiple roles. The right model is to keep the diode passive and add a circuit-level cell that models the function whenever the framework needs to propagate signal through it.

**New cell — `SeriesRectifier`** in `src/components/chips/concepts/series_rectifier.py`:

```python
@register('SeriesRectifier')
class SeriesRectifier(FactorNode):
    """Behavioural model of a forward-conducting diode in a series
    rectifier role. Wired alongside the passive physical diode in
    the BOM. Drives `output` to (input - V_F) when input > V_F;
    drives output to 0 otherwise (reverse-blocked / no input).

    Use this whenever a passive diode sits in a supply chain where
    the framework needs to propagate the upstream voltage through to
    the downstream net (e.g. reverse-polarity protection on a power
    rail). For OR-matrix uses, use `DiodeOR` instead. For passive
    uses (flyback, decoupling, clamp), no cell is needed — the diode
    sits on an already-driven net.
    """

    REFDES_PREFIX: ClassVar[str] = 'A'   # behavioural cell, not a BOM part
    FOOTPRINT:     ClassVar[str | None] = None

    __slots__ = ('_ports', '_v_f', '_refdes_number')

    def __init__(self, v_f: float, *, refdes_number: int,
                 domain: GroundDomain = ELECTRICAL) -> None:
        self._v_f = float(v_f)
        self._refdes_number = refdes_number
        self._ports = {
            'input':  Port('input',  Direction.IN,  domain,
                           mandatory=True, signal_type=Analog),
            'output': Port('output', Direction.OUT, domain,
                           mandatory=False, signal_type=Analog),
        }

    def evaluate(self) -> None:
        v_in = self._ports['input'].value or 0.0
        if v_in > self._v_f:
            self._ports['output'].drive(v_in - self._v_f)
        else:
            self._ports['output'].drive(0.0)
```

**Usage pattern.** A power-supply circuit instantiates both the passive diode (for the BOM) and the `SeriesRectifier` cell (for ERC), wiring them in parallel:

```python
self.d1 = D1N5817(refdes_number=1)             # passive part
self.rect1 = SeriesRectifier(v_f=0.3, refdes_number=1)
wire(self.bt1.pos, self.d1.anode, self.rect1.input)
wire(self.d1.cathode, self.rect1.output, self.u1.INPUT)
```

This mirrors the existing `DiodeOR` pattern in the `dice` demo. The passive diode is on the BOM and on the KiCad netlist; the cell is what makes the framework's logical-net walk find a driver on the cathode-side net.

**Affected diode classes** (none need modification — they stay Category A passive):

| Class       | V_F  | Notes                                          |
|-------------|-----:|------------------------------------------------|
| `D1N4148`   | 0.7  | small-signal silicon — passive                 |
| `D1N4001`   | 1.0  | rectifier, 50 V / 1 A — passive                |
| `D1N4007`   | 1.0  | rectifier, 1000 V / 1 A — passive              |
| `D1N5817`   | 0.3  | Schottky, 20 V / 1 A — passive                 |

#### 7.2.3 Zener diodes — passive parts, two circuit-level cells

**Decision:** Zeners are **Category A — passive**, by the same reasoning as §7.2.2. A Zener is a passive part on the BOM; the role it plays in a circuit (forward conductor, reverse-bias shunt clamp, signal-level reference) is a property of *how it's wired*, not of the part itself. The same `D1N4733A` is used as a forward-conducting diode in some designs and a 5.1 V shunt reference in others.

Two circuit-level cells exist alongside the passive Zener — pick the one that matches the role:

**`SeriesRectifier`** (already specified in §7.2.2) — forward-conducting use. Parameterised with the Zener's forward V_F (≈0.7 V); no different from a regular silicon diode used forward.

**New cell — `ZenerShunt`** in `src/components/chips/concepts/zener_shunt.py`:

```python
@register('ZenerShunt')
class ZenerShunt(FactorNode):
    """Behavioural model of a reverse-biased Zener acting as a voltage
    clamp / shunt regulator. Wired alongside the passive physical
    Zener in the BOM. Drives `cathode` to (anode + V_Z) whenever an
    upstream source on the cathode net would otherwise exceed that
    value; otherwise leaves the cathode floating (the net's existing
    driver wins).

    Use this whenever a passive Zener sits between a series resistor
    and ground (the canonical shunt-clamp role) and the framework
    needs a real driver on the Zener's cathode net. For forward use,
    use `SeriesRectifier` instead.

    Note: the framework's voltage-only graph cannot model the
    'whichever value is lower wins' interaction between the upstream
    driver and the clamp; the cell drives the clamp value
    unconditionally. SPICE remains the right tool for clamp-voltage
    accuracy. The cell exists so the topology validates.
    """

    REFDES_PREFIX: ClassVar[str] = 'A'   # behavioural cell, not a BOM part
    FOOTPRINT:     ClassVar[str | None] = None

    __slots__ = ('_ports', '_v_z', '_refdes_number')

    def __init__(self, v_z: float, *, refdes_number: int,
                 domain: GroundDomain = ELECTRICAL) -> None:
        self._v_z = float(v_z)
        self._refdes_number = refdes_number
        self._ports = {
            'anode':   Port('anode',   Direction.IN,  domain,
                            mandatory=True,  signal_type=Analog),
            'cathode': Port('cathode', Direction.OUT, domain,
                            mandatory=False, signal_type=Analog),
        }

    def evaluate(self) -> None:
        v_anode = self._ports['anode'].value or 0.0
        self._ports['cathode'].drive(v_anode + self._v_z)
```

**Usage pattern.** Identical to `SeriesRectifier` — passive Zener on the BOM, behavioural cell wired in parallel:

```python
self.d2 = D1N4733A(refdes_number=2)              # passive part
self.shunt2 = ZenerShunt(v_z=5.1, refdes_number=2)
wire(self.d2.cathode, self.shunt2.cathode, self.u1.OUTPUT)
wire(self.d2.anode,   self.shunt2.anode,   self.gnd_rail.line)
```

The 5v_rail_power demo uses exactly this pattern for D2 (the over-voltage clamp on the LM7805's output).

**Affected Zener classes** (none need modification — they stay Category A passive):

| Class       | V_Z  | Notes                                          |
|-------------|-----:|------------------------------------------------|
| `D1N4733A`  | 5.1  | Zener, 1 W — passive                           |
| `D1N4742A`  | 12.0 | Zener, 1 W — passive                           |

#### 7.2.4 Discrete transistors

**New cells**: `BJTSwitch`, `MOSFETSwitch` in `src/components/chips/concepts/`.

For BJTs (NPN), the cell drives the collector pin's internal face. The collector is pulled to the emitter potential when the base is above its threshold relative to emitter:

```python
@register('BJTSwitch')
class BJTSwitch(FactorNode):
    __slots__ = ('_ports', '_polarity')

    V_BE_ON: ClassVar[float] = 0.7  # threshold

    def __init__(self, polarity: Literal['npn', 'pnp'],
                 domain: GroundDomain = ELECTRICAL) -> None:
        self._polarity = polarity
        # ... ports: base (IN), collector (OUT), emitter (IN)

    def evaluate(self) -> None:
        v_b = self._ports['base'].value or 0.0
        v_e = self._ports['emitter'].value or 0.0
        if self._polarity == 'npn':
            on = (v_b - v_e) > self.V_BE_ON
        else:  # pnp
            on = (v_e - v_b) > self.V_BE_ON
        if on:
            self._ports['collector'].drive(v_e)  # saturated
        else:
            self._ports['collector'].drive(None)  # off; hi-Z
```

For MOSFETs, analogous with `V_GS_TH`. Implementer fills in.

**Affected classes**:

| Class         | Type           | Polarity | Cell           |
|---------------|----------------|----------|----------------|
| `BC547`       | NPN BJT        | npn      | BJTSwitch      |
| `BC557`       | PNP BJT        | pnp      | BJTSwitch      |
| `Q2N3904`     | NPN BJT        | npn      | BJTSwitch      |
| `Q2N3906`     | PNP BJT        | pnp      | BJTSwitch      |
| `Q2N2222`     | NPN BJT        | npn      | BJTSwitch      |
| `Q2N7000`     | N-MOSFET       | n        | MOSFETSwitch   |
| `BS170`       | N-MOSFET       | n        | MOSFETSwitch   |
| `IRLB8721`    | N-MOSFET power | n        | MOSFETSwitch   |
| `IRFZ44N`     | N-MOSFET power | n        | MOSFETSwitch   |
| `TIP120`      | NPN Darlington | npn      | BJTSwitch (V_BE ≈ 1.4 V due to Darlington) |

#### 7.2.5 Op-amps and comparators

**Existing cell**: `Comparator` (already in `src/components/chips/concepts/comparator.py`). Used by `LM393` already.

**Audit task**: verify the following classes wire a `Comparator` (or new `OpAmp`) cell per channel:

| Class       | Cell needed                | Channels | Audit status               |
|-------------|----------------------------|----------|----------------------------|
| `LM393`     | `Comparator` (have)        | 2        | already correct            |
| `LM339`     | `Comparator`               | 4        | check                      |
| `LM311`     | `Comparator`               | 1        | check                      |
| `TLV3401`   | `Comparator`               | 1        | check                      |
| `LM358`     | `OpAmp` (new)              | 2        | implement                  |
| `LM324`     | `OpAmp`                    | 4        | implement                  |
| `TL072`     | `OpAmp`                    | 2        | implement                  |
| `TL074`     | `OpAmp`                    | 4        | implement                  |
| `LM741`     | `OpAmp`                    | 1        | implement                  |
| `MCP6002`   | `OpAmp` (rail-to-rail)     | 2        | implement                  |
| `LMV358`    | `OpAmp`                    | 2        | implement                  |
| `OPA2134`   | `OpAmp` (audio)            | 2        | implement                  |

**New cell**: `OpAmp` in `src/components/chips/concepts/opamp.py`. Behaviour: output = high gain (10^5) times (V+ − V−), clamped to V_pos and V_gnd supplies. For framework-topology purposes, the cell just needs to *drive* its output; quantitative gain accuracy is SPICE's job. A simplified model:

```python
def evaluate(self) -> None:
    v_pos_in  = self._ports['in_pos'].value or 0.0
    v_neg_in  = self._ports['in_neg'].value or 0.0
    v_supply  = self._ports['v_supply'].value or 0.0
    v_gnd     = self._ports['v_gnd'].value or 0.0
    # Output saturates at the supply rails; ideal op-amp transfer
    # function has infinite gain.
    if v_pos_in > v_neg_in:
        self._ports['out'].drive(v_supply)
    elif v_pos_in < v_neg_in:
        self._ports['out'].drive(v_gnd)
    else:
        self._ports['out'].drive((v_supply + v_gnd) / 2.0)
```

This is **the comparator's behaviour** — high gain produces rail-to-rail output. The real op-amp's linear region is too narrow to matter for topology-validation purposes. Users who need linear-region accuracy run SPICE.

For multi-channel chips, instantiate one cell per channel.

#### 7.2.6 Optocouplers

**New cell**: `Optocoupler` in `src/components/chips/concepts/optocoupler.py`. Treats the input LED + photodetector as a single behavioural unit:

```python
@register('Optocoupler')
class Optocoupler(FactorNode):
    def evaluate(self) -> None:
        v_anode   = self._ports['anode'].value or 0.0
        v_cathode = self._ports['cathode'].value or 0.0
        led_on = (v_anode - v_cathode) > self.V_F_LED   # ~1.2 V for IR LED
        if led_on:
            # Phototransistor conducts; collector pulled to emitter.
            v_emitter = self._ports['emitter'].value or 0.0
            self._ports['collector'].drive(v_emitter)
        else:
            self._ports['collector'].drive(None)
```

**Affected classes**:

| Class           | Notes                                          |
|-----------------|------------------------------------------------|
| `MOC3021`       | Triac driver opto — different output side (triac, not transistor). May need a separate `TriacOptocoupler` cell. |
| `OPTO_4N25`     | Standard phototransistor opto                  |
| `OPTO_TLP521`   | Standard phototransistor opto                  |

#### 7.2.7 RS-232 / level shifters

**New cell**: `RS232Driver` in `src/components/chips/concepts/rs232_driver.py`. Drives each TX_OUT from each TX_IN, inverted and level-shifted to RS-232 levels (±5 V to ±12 V). Drives each RX_OUT from each RX_IN, inverted and level-shifted back to logic levels.

For framework-topology purposes, the inversion is the important part — without the cell, the OUT pins float. The level shift can be modelled as a simple gain or just by saying "output is anti-correlated with input."

**Affected classes**:

- `MAX232` — instantiates two `RS232Driver` channels (chip is dual driver / dual receiver).

#### 7.2.8 Specialty ICs

Each specialty IC needs its own behavioural cell. The implementer audits each and writes the matching cell:

| Class       | Cell to write          | Notes                                          |
|-------------|------------------------|------------------------------------------------|
| `NE555`     | `NE555Oscillator`      | Astable / monostable per pin config; complex. |
| `LM386`     | `AudioAmp`             | Audio amplifier; drives output from input. Reuse `OpAmp` if topology allows. |
| `DS18B20`   | `OneWireSlave`         | 1-Wire bus device; bus master in tests. Complex. |
| `DS1307`    | `I2CRTC`               | I²C RTC; bus stimulation in tests. Complex. |
| `MAX7219`   | `SerialDisplayDriver`  | Shift-register display driver; SPI in tests. Complex. |
| `TLC5940`   | `PWMLEDDriver`         | 16-channel PWM driver; SPI/serial input.   |

For the protocol-bus chips (DS18B20, DS1307, MAX7219, TLC5940), the cell models the chip's response to bus stimulation. The fixtures in the regression test mock the bus master.

#### 7.2.9 Sensors

| Class       | Cell to write          | Notes                                          |
|-------------|------------------------|------------------------------------------------|
| `TMP36`     | `AnalogTempSensor`     | Output voltage = (T_c × 0.01) + 0.5; Python state for T_c. |
| `BMP280`    | `I2CPressureSensor`    | I²C bus; Python state for pressure_pa.         |
| `MPU6050`   | `I2CIMU`               | I²C bus; Python state for accel/gyro.          |
| `HCSR04`    | `UltrasonicRanger`     | Trigger/echo pulses; Python state for distance_cm. |

### 7.3 Category C — Application-firmware-driven

These classes legitimately ship with `cells=[]` because their output behaviour is determined by user firmware, not by a function of their input pins. Users subclass and inject a firmware-as-cell per the established demos pattern.

**Affected classes**:

- All MCUs: `ATmega328P`, `ATmega2560`, `ATmega32U4`, `ATtiny85`, `ATtiny84`, `STM32F103C8T6`, `STM32F411CEU6`, `RP2040`, `ESP32_WROOM_32`, `ESP8266_12F`.

**The regression-test fixture** for each MCU uses a stub `_StubFirmwareCell` that drives every GPIO pin to a known state (configurable per pin via a dict). This stand-in lets the framework see the chip as fully driven; the user's real firmware replaces the stub.

The bare MCU class is **explicitly documented** as Category C in `docs/behavioural-cell-audit.md` — it's not a defect; it's a deliberate design choice the user must build on top of.

## 8. The `backup_power` demo audit

The user specifically called out the `demos/backup_power/` demo as suspicious. It uses `TPS2660`, `LM5002`, `LM5160` — all of which are believed to be black-box chips with `cells=[]`. By the analysis in §3, these should produce `FloatingNetError` when the demo is constructed. But the demo currently constructs without raising (it's in the demos directory with working golden exports).

**The audit explicitly investigates this discrepancy.** Three possibilities:

1. The chips have cells the implementer added quietly; the audit verifies this and documents.
2. The wiring puts a Rail at every intermediate net, so the supply chain happens to have a driver at every step despite the chips being black-box. The audit verifies this and documents the topology.
3. The demo's `Circuit._validate` is somehow not running (e.g. the demo bypasses normal construction). The audit verifies this and **fixes** the demo to validate cleanly.

The audit produces a `docs/backup-power-audit.md` documenting which of (1), (2), or (3) is the case, with concrete evidence. If (3), the demo is repaired in the same work package by adding the cells to TPS2660 / LM5002 / LM5160 (per the general pattern in §7).

This is non-negotiable. The user's standard requires the demo to be *correct*, not *passing-by-accident*.

## 9. File-by-file change list

**New files**:

- `src/components/chips/concepts/linear_regulator.py` — `LinearRegulator` cell.
- `src/components/chips/concepts/series_rectifier.py` — `SeriesRectifier` cell (circuit-level, paired with passive diode).
- `src/components/chips/concepts/zener_shunt.py` — `ZenerShunt` cell (circuit-level, paired with passive Zener).
- `src/components/chips/concepts/bjt_switch.py` — `BJTSwitch` cell.
- `src/components/chips/concepts/mosfet_switch.py` — `MOSFETSwitch` cell.
- `src/components/chips/concepts/opamp.py` — `OpAmp` cell.
- `src/components/chips/concepts/optocoupler.py` — `Optocoupler` cell (plus `TriacOptocoupler` if `MOC3021` needs distinct modelling).
- `src/components/chips/concepts/rs232_driver.py` — `RS232Driver` cell.
- `src/components/chips/concepts/ne555_oscillator.py` — `NE555Oscillator` cell.
- One file per specialty IC's cell as listed in §7.2.8 (TLC5940 / MAX7219 / DS18B20 / DS1307 driver cells).
- One file per sensor cell as listed in §7.2.9.
- `tests/framework/test_behavioural_completeness.py` — the regression test (§6).
- `tests/components/concepts/test_<cell>.py` — per-cell unit tests for each new cell.
- `docs/behavioural-cell-audit.md` — the audit table (generated by the implementer during the walk).
- `docs/backup-power-audit.md` — the specific investigation of the `backup_power` demo (§8).

**Modified files** (each gets its behavioural cell instantiated in `__init__`):

- Every linear regulator: `src/components/chips/lm7805.py`, `lm7812.py`, `lm7905.py`, `lm317.py`, `lm337.py`, `ams1117_33.py`, `ams1117_50.py`, `lp2950.py`.
- Every transistor: `src/components/transistors/bc547.py`, `bc557.py`, `q2n3904.py`, `q2n3906.py`, `q2n2222.py`, `q2n7000.py`, `bs170.py`, `irlb8721.py`, `irfz44n.py`, `tip120.py`.
- Every op-amp: `lm358.py`, `lm324.py`, `tl072.py`, `tl074.py`, `lm741.py`, `mcp6002.py`, `lmv358.py`, `opa2134.py`.
- Comparators if any lack cells: audit `lm339.py`, `lm311.py`, `tlv3401.py`.
- Every optocoupler: `moc3021.py`, `opto_4n25.py`, `opto_tlp521.py`.
- Every specialty IC needing a cell per §7.2.8.
- Every sensor per §7.2.9.
- The `backup_power` demo's chip classes if those need cells (per §8).

**Framework-level changes** (the construction-time invariant from §6.1):

- `src/framework/chip.py` — add `BARE_FIRMWARE_DRIVEN: ClassVar[bool] = False` to `Chip`. After `super().__init__(...)` in `Chip.__init__`, call `self._assert_every_out_pin_is_internally_driven(pins)` unless the opt-out flag is set. Implement the method per the code sketch in §6.1.
- `src/framework/transistor.py` (if a `Transistor` base class is introduced as part of the BJT/MOSFET cell work in §7.2.4; otherwise the check lands per-class) — analogous pattern: refuse to construct a transistor subclass with `cells=[]`.
- Every MCU class (`ATmega328P`, `ATmega2560`, `ATmega32U4`, `ATtiny85`, `ATtiny84`, `STM32F103C8T6`, `STM32F411CEU6`, `RP2040`, `ESP32_WROOM_32`, `ESP8266_12F`) — add `BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True` as a class attribute. This is the deliberate opt-out per §6.1; the audit table records each one as Category C.

`src/framework/diode.py` is *not* modified — diodes are Category A passive (§7.2.2, §7.2.3) and don't need cells; there's no per-class invariant to enforce.

These framework changes land **after** the audit fixes for every existing chip (per §7.2). Activating the check before the audit fixes would refuse to construct LM7805 et al. — see §6.1 for the order-of-operations rationale.

**Unmodified**:

- Already-cellled chips: `SN74HC04`, `CD4069`, `CD4043`, `LM393`, `ULN2003A`, `ISOW7841`. These are already correct.
- All passive classes (Resistor, Capacitor, Rail, LED, every connector) — Category A; untouched.
- All diode classes (`D1N4148`, `D1N4001`, `D1N4007`, `D1N5817`, `D1N4733A`, `D1N4742A`) — Category A; untouched. Circuit-level cells (`SeriesRectifier`, `ZenerShunt`, existing `DiodeOR`) are added in the circuits that need them, not on the diode classes themselves.
- Other framework files (`circuit.py`, `wire.py`, `node.py`, `diode.py`, etc.) — the framework changes are scoped to `chip.py` and (later) `transistor.py`, the base classes that own the directional contracts being enforced.

## 10. Test plan

**Per-cell unit tests** (`tests/components/concepts/test_<cell>.py`, one per new cell):

For each new cell, walk it through its parameter space and assert the output port values match the modelled behaviour:

- `LinearRegulator`: input above dropout → output at OUTPUT_VOLTAGE; input below dropout → output sags; input below output → near-zero output.
- `SeriesRectifier`: input > V_F → output = input − V_F; input ≤ V_F → output = 0.
- `ZenerShunt`: drives cathode to (anode + V_Z) unconditionally; verify the drive value across V_Z range.
- `BJTSwitch`: base above threshold → collector pulled to emitter; base below → collector floats.
- (analogous for every other cell)

**Per-chip integration tests** (`tests/components/test_<chip>.py`, extending existing per-chip tests):

For each chip that gained a cell, assert that:

- The chip's `__init__` instantiates the right cell with the right parameters.
- Driving the chip's input pins produces expected behaviour on the output pins (via the cell's evaluate).
- The chip still passes its existing tests (refdes, pin count, footprint, etc.).

**Construction-time invariant tests** (`tests/framework/test_chip_construction_invariant.py`, new):

- Define a `_BrokenChip(Chip)` subclass that declares an OUT pin but passes `cells=[]`. Assert instantiating it raises `PartConfigurationError` whose message names the OUT pin and points the user at this spec.
- Define a `_FixedChip(Chip)` subclass that declares an OUT pin and wires a driving cell. Assert it instantiates cleanly.
- Define a `_FirmwareDrivenChip(Chip)` subclass with `BARE_FIRMWARE_DRIVEN = True` and `cells=[]`. Assert it instantiates cleanly (the opt-out path).
- These tests pin the construction-time invariant to a specific behaviour; if the check is accidentally removed or weakened, they fail.

**The framework-level regression test** (`tests/framework/test_behavioural_completeness.py`):

- Walks every class in the registry. For each class:
  - Looks up the minimal-topology fixture.
  - Asserts the fixture exists (failure if missing — keeps coverage 100%).
  - Asserts the fixture's circuit constructs without raising any `CircuitryError`.
- Total test count: one per registered class.
- This is the **secondary** defence per §6.2; with the primary §6.1 check turned on, most classes will already construct correctly when the test merely tries to instantiate them in a minimal topology. The regression test still earns its keep by catching topology-level issues (the cell drives wrong; the topology can't be satisfied) and by ensuring the per-class fixture coverage stays at 100% (new classes can't ship without a fixture entry).

**The `backup_power` audit test** (`tests/applications/test_backup_power_audit.py`):

- Constructs the `backup_power` demo.
- Asserts no `FloatingNetError` (or any other ERC error).
- Walks the demo's logical nets and asserts every net has at least one real (non-conductor) driver.
- Documents the audit result in the test's docstring.

**Golden tests**: every existing demo's golden exports must continue to pass byte-identically. The behavioural cells must not perturb any existing output — they affect only ERC validation, not the export adapters' walks. If a golden changes, the implementer must investigate (typically the cell is mis-wired or the chip's cell-instantiation order is different).

## 11. Acceptance criteria

1. `python -m pytest` passes. Test count up by at least the number of new cell tests + per-chip integration test additions + the framework-level regression-test parametrisation (one per registered class, currently ~120).
2. `docs/behavioural-cell-audit.md` exists and lists every registered class with category and audit status. Every Category-B row marked `pass` has its cell implemented and wired.
3. `tests/framework/test_behavioural_completeness.py` exists and passes for every registered class.
4. Adding a new component class without adding a fixture causes the regression test to fail with a clear message.
5. Every linear regulator, every transistor, every op-amp, every optocoupler, every specialty IC with directional behaviour, and every sensor with state-driven output has a behavioural cell instantiated. Diodes (including Zeners) remain Category A passive — they do not gain class-level cells; circuit-level cells (`SeriesRectifier`, `ZenerShunt`, the existing `DiodeOR`) are added in the circuits that need them.
6. The `SeriesRectifier` and `ZenerShunt` circuit-level cells exist and are wired into the `5v_rail_power` demo, replacing its current dependence on (now-absent) class-level diode cells.
7. MCUs remain bare (Category C) but pass the regression test via the stub firmware fixture, and each MCU class declares `BARE_FIRMWARE_DRIVEN = True` explicitly.
8. The `backup_power` demo is audited and either confirmed correct (with documentation of why) or repaired (with the audit explaining the original defect).
9. Every existing demo's golden exports remain byte-identical.
10. No new `pytest.skip` / `xfail` / softening introduced.
11. `__slots__` discipline preserved on every new cell. No setters introduced on any chip class.
12. Per-cell unit tests pass for every new cell; the cells' behaviour is exercised across the parameter ranges they support.
13. **`Chip.__init__` enforces the OUT-pin-driven invariant** at construction time. Attempting to instantiate a `Chip` subclass with an OUT pin and `cells=[]` raises `PartConfigurationError`, *unless* the class declares `BARE_FIRMWARE_DRIVEN = True`. Verified by the construction-invariant tests in §10.
14. The two enforcement layers are independent: the primary check (§6.1) and the regression test (§6.2) both pass on the same codebase, and the regression test is sized to catch defects the primary check by design cannot (non-`Chip` directional components, opt-out misuse, topology-level issues beyond mere construction).

## 12. Out of scope

- **Quantitative accuracy** of the behavioural cells. The cells produce topologically-correct drive paths with reasonable-but-not-vendor-accurate output values. SPICE simulation remains the right tool for accuracy; the cells exist to make ERC pass and to give the framework a sensible value to propagate through evaluation.
- **Cell-level audits for existing concept classes** (`Inverter`, `Comparator`, `NORLatch`, `TriStateBuffer`, `DarlingtonChannel`, `IsolatedChannel`, `Commutator`, `BLDCMotor`). These are already correct by virtue of passing in their host chip designs. A future "concept-cell verification pass" could audit them, but it's not required for the trust statement this audit is about.
- **Firmware-cell auditing for MCU subclasses**. `Uno_ThermometerSketch`, `Uno_BLDCCommutator`, etc. are user-firmware classes; their correctness is the application author's responsibility.
- **Vendor-supplied SPICE models**. Deferred (separately tracked).
- **Cross-cell interactions**. Cells today produce values independently; multi-cell feedback loops (an opamp with feedback through external resistors back to its inverting input) aren't modelled at the cell level — they'd require iterative evaluation, which is a framework-level extension out of scope here.
- **Heat / dissipation modelling**. Linear regulators heat up at high dropout × current; transistors fail open under thermal stress. The framework doesn't model heat; the cell ignores it.
- **Behavioural modelling of pure-passive parts**. Resistor's evaluate() is correctly a no-op; the framework doesn't solve Ohm's law. No cell is needed.

## 13. The trust statement

When this work package lands, the project's public claim becomes:

*"The framework's `Chip` base class refuses to construct a subclass that declares directional behaviour without a behavioural cell to back it. The defect class of 'a chip with OUT pins that don't actually drive' is **unconstructible** — a contributor who tries to add a new component without the cell receives a `PartConfigurationError` from the framework itself, with an error message that names the offending pin and points at the cell pattern they need to add. The only legitimate way to ship a chip with `cells=[]` is to set `BARE_FIRMWARE_DRIVEN = True` on the class, a deliberate opt-out reserved for microcontrollers and similar firmware-driven parts; that flag's presence in source is a reviewable design statement. Diodes are deliberately not covered by an analogous per-class check — they're passive parts whose directional role is a property of the circuit using them, modelled at the circuit level by `SeriesRectifier`, `ZenerShunt`, or the existing `DiodeOR` pattern. Transistors get the analogous check when the §7.2.4 BJT/MOSFET cell work lands. A secondary regression test walks every class in the registry to catch anything the primary check by design cannot — non-`Chip` directional components, topology-level issues, opt-out misuse, circuit-level uses of passive parts that need a paired behavioural cell to make ERC pass. New classes added in the future cannot bypass both defences, by construction."*

That is the dependable framework — the trust no longer rests on "we ran the regression test and it passed" but on "the type system refuses the defect, full stop." The audit's deliverable is exactly that statement, backed by exactly that pair of mechanisms.

**What this changes about the project's posture.** Before this work package, the framework was correct *for the demos that had been built*; floating-net detection caught defects when an actual circuit was constructed, but a class that nobody had wired into a circuit could ship with the defect latent. After this work package, defective components fail at the earliest possible point — class instantiation, not circuit construction — and the error message tells the contributor exactly what to write next. The latency window between "ship the defective class" and "user trips over it" collapses to zero. That is what raises the framework from "passes its existing tests" to "dependable."
