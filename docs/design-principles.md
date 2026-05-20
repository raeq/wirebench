# Design principles

If you couldn't do it with a soldering iron, you can't do it in code.

That's the framework's central commitment. Every API choice flows from it. The discipline isn't aesthetic — it's the reason the breadboard build matches the code. Pages of architecture and a hundred-plus implementation choices reduce, ultimately, to that one sentence.

This document explains *what the framework refuses, and why*, in enough depth that the refusals make sense as design choices rather than arbitrary constraints. If you've hit a refusal and want to know what to do about it, this is the right document to read.

## What the framework promises

A wirebench design that passes `pytest` is **topologically buildable**:

- Every wire in the Python source maps to a wire on the breadboard.
- Every component has a stable refdes (`R1`, `U2`, `D3`) that appears in the BOM, the KiCad netlist, and the SPICE deck consistently.
- Every chip's pin numbering matches the manufacturer's datasheet.
- No silent failures: every electrical impossibility the framework can detect at construction time raises before evaluation.

That promise is the value proposition. The discipline below is how the framework keeps it.

## What the framework refuses

These are the construction-time checks. Each one corresponds to a real-world failure mode that costs at the bench.

### Short circuits

```python
u1 = SN74HC04(refdes_number=1)
wire(u1.y_1, u1.y_2)
# ValueError: wire() has multiple drivers ('y_1', 'y_2') — short circuit
```

Two outputs on the same net is a hardware short. The framework counts driver ports per logical net and refuses anything with more than one.

The "logical net" qualifier matters. After a `mate()` call joins two boards' connector pins, the resulting net might span both boards. The framework's `IS_CONDUCTOR` walk treats pins and connector contacts as transparent (they're conductors, not drivers); the check looks for *real* originating drivers anywhere on the extended net. A multi-driver short on a mated bus is caught the same as a single-board short.

### Floating nets

```python
r1 = Resistor(1000, refdes_number=1)
r2 = Resistor(1000, refdes_number=2)
wire(r1.t1, r2.t1)
Circuit(parts=[r1, r2], ports={})
# ValueError: Floating logical net — multiple passive BIDIRs with no driver
```

Two passive components touching at a node with nothing driving them produces a node whose voltage is undefined. Real silicon does this too — a floating CMOS input drifts and the chip behaves unpredictably. The framework treats it as an error.

Note that this rule reflects the framework's logic-level fidelity. A voltage divider in the real world has a well-defined intermediate voltage (Kirchhoff's voltage law and Ohm's law together determine it). The framework can't solve those equations — it's not an analog simulator. From its perspective, a node with only passive endpoints has no driver, which is correct *for the framework's job* (topology validation) even though it's incomplete for a continuous-voltage simulator. If you need real divider behaviour, export to SPICE and let ngspice handle it.

### Mismatched mates

```python
host  = Pin2x20MaleHeader(pin_count=40, pitch_mm=2.54, refdes_number=1)
wrong = JSTPHCableHousing(pin_count=4, refdes_number=1)
mate(host, wrong)
# TypeError: Pin2x20MaleHeader mates with Pin2x20FemaleHeader, not JSTPHCableHousing
```

A 2×20 0.1" male header doesn't physically mate with a JST PH cable housing. The framework knows what mates with what (each connector class declares its `MATES_WITH` partner) and refuses anything else.

### Refdes collisions

```python
r1a = Resistor(330, refdes_number=1)
r1b = Resistor(470, refdes_number=1)
Circuit(parts=[r1a, r1b], ports={})
# ValueError: Duplicate refdes: R1 used by Resistor and Resistor
```

Two parts sharing a refdes makes the silkscreen ambiguous. Refdes uniqueness is checked per-board (per the IEEE 315 / ASME Y14.44 conventions); a stacked assembly can contain `A1.R1` and `A2.R1` because they're on different boards, but two `R1`s on the same board is a hard error.

### Cross-domain wires

```python
host_port  = Port('TX', Direction.OUT, ELECTRICAL, signal_type=Digital)
iso_port   = Port('RX', Direction.IN,  ISOLATED,   signal_type=Digital)
wire(host_port, iso_port)
# ValueError: Cannot wire ports across ground domains: 'TX' (ELECTRICAL), 'RX' (ISOLATED)
```

Connecting two grounds that aren't supposed to share a reference is the failure mode that defeats every isolation barrier ever built. The framework requires you to declare ground domains explicitly and refuses wires that cross between them. The only legal crossing is through an isolation component whose internal cells span both domains (see `demos/isolated_rs232/` for the canonical example).

### Mandatory ports left unwired

```python
led = LED('red', refdes_number=1)
Circuit(parts=[led], ports={})
# ValueError: Unconnected mandatory port(s): 'LED.anode'
```

An LED with a floating anode is a packaged failure — the chip exists but does nothing. Components mark ports as `mandatory=True` when they must be connected before evaluation. A composite circuit that omits a mandatory port either has to wire it internally or expose it as a boundary port for the caller to drive.

### Invalid hardware states

```python
latch = NORLatch()
latch(s=True, r=True)
# ValueError: NORLatch: S=R=1 is forbidden (race condition)
```

Some hardware states are physically forbidden, not just unusual. S=R=1 on an SR latch races; both outputs depend on transistor switching speeds and the latch may or may not settle deterministically. The framework refuses, with the failure named clearly, rather than silently picking an outcome.

## What the framework *won't* refuse

The discipline cuts both ways. There are real-world failures the framework cannot detect — and the README is honest about them so you know where the rules don't reach.

### Continuous-voltage problems

A voltage-divider design with the wrong resistor ratios is topologically fine but practically wrong. The framework can't tell you a 10 MΩ pull-up on a fast-switching line will give you a slow edge; that's an RC time-constant question. Export to SPICE and simulate.

### Component value mismatches

Wiring a 1N4148 signal diode where a 1N4001 rectifier is needed (or vice versa) is topologically valid — both are diodes, both have an anode and a cathode. The framework can't catch the reverse-voltage rating mismatch. Datasheets and a careful BOM review remain your job.

### Firmware bugs

An ATmega328P with a sketch that drives a GPIO HIGH when it should be LOW will produce wrong outputs. The framework models the silicon and pin map; the firmware is your code, modelled as a private cell inside the MCU class. The framework doesn't run Arduino sketches or step through C++ logic.

### Mechanical and thermal problems

Two connectors that mechanically interfere on a stacked assembly is not a refdes problem or a wiring problem. A power MOSFET that needs a heatsink the design omits is not a wiring problem. PCB layout decisions (trace widths, return paths, decoupling-cap placement) are not in the framework's scope.

### What you're trying to model isn't physical

If you try to model a Bode plot, an antenna pattern, or anything in the frequency domain, the framework can't help. Logic-level, steady-state, topological — that's the box.

## Why these rules and not others

Some readers will recognise that the project could have chosen looser or stricter rules. A few specific calls worth knowing about:

### Why pin *numbers* are canonical, not pin names

Real chips have pin *numbers* stamped on the silkscreen. Pin *names* (`VCC`, `GND`, `PB5`) are convenience labels in the datasheet — useful for humans, but multiple pins can share a name (a chip can have four VCC pins) and you can't address them by name unambiguously. The framework's `Chip.ports_by_number` is the canonical lookup; `Chip.ports['VCC']` works when the name is unique and raises a helpful disambiguation error when it isn't. This is how KiCad, SPICE, and every real EDA tool model chips — by pin number.

### Why there are no setters

A soldered resistor has a fixed value. There is no operation in the physical world equivalent to `resistor.value = 470` on a resistor that's already wired into a circuit. The framework reflects that: components are constructed with their values and never mutated afterward. The discipline catches a class of bug — "I changed a value but forgot to re-validate the topology" — by making it inexpressible.

### Why connectors are themselves components

A connector takes up board space, has a refdes, appears on the BOM, and gets a footprint in the PCB layout. It is a *part*, not a framework abstraction. The framework models it that way: `Connector` is a `Part` subclass with refdes prefix `J` (chassis-side) or `P` (cable-side) per IEEE 315, with its own pin numbers and footprint.

### Why no inheritance between component types

Cells inside chips (`Inverter`, `NORLatch`, `Comparator`) are concept classes, not subclasses of each other. A comparator is not a subclass of an op-amp even though their input topology is similar; the comparator's output saturates and the op-amp's doesn't, and that difference is the whole point. Composition over inheritance, for the same reason it's the right call in any modelling problem: real things don't inherit; they compose.

### Why every design is logic-level

The framework targets the design *topology* — what's wired to what, what parts go on the BOM, what the silkscreen says. Continuous-voltage behaviour is the simulator's job. Splitting the responsibilities cleanly lets each tool be excellent at its part: SPICE for analog, KiCad for layout, wirebench for the source of truth.

## How the discipline maps to the API

The principles above appear as specific patterns throughout the code:

- **`@register('ClassName')`** on every component class — every part appears in a global registry that exporters consult by name. There's no way to silently introduce a part that exporters can't render.
- **`@validate_call`** on every `__init__` and `__call__` — pydantic runs validation at every API surface; passing a `str` where an `int` is expected fails fast with a clear error.
- **`__slots__`** on every component class — a `Resistor` instance has exactly the attributes its `__slots__` declares, no more. Typo'd attribute access at the call site is an `AttributeError`, not silent attribute creation.
- **Read-only properties** for state observation — `led.lit`, `latch.q_1`, `chip.refdes` all return the current state without allowing modification.
- **`evaluate()` is a graph-ordered method** — the framework topologically sorts the components and calls `evaluate()` in dependency order. You don't call `evaluate()` directly on a single component within a circuit; the circuit's `evaluate()` does the right thing.
- **`__call__` is the test surface** — for isolated component testing, every component is callable with its input ports as arguments and returns its output state. The framework refuses to let you call `__call__` on a component whose ports are wired into a parent circuit (would silently overwrite the parent's signal).
- **Auto-collection from `self.__dict__`** — components stored as `self.<name>` attributes are picked up automatically when `super().__init__()` finalises the `Circuit` or `Board`. The framework refuses to construct an empty composite (Rule 1: the auto-collected `parts` is empty — almost certainly because the developer used local variables instead of attribute storage) or one with wires reaching outside its known parts (Rule 2: a port wired to a known port belongs to a component not in `parts` — partial coverage from mixed self/local usage). Both refusals raise with error messages that show the canonical attribute-storage pattern by example, so the framework teaches the right shape the first time a developer slips.

Each pattern is a specific application of the central commitment: *every line of code maps to a physical operation*.

## Rules for component-class authors

If you're adding a new component to `src/components/`, the [scaffold script](#scaffolding-a-new-component) machine-applies most of the rules below. The list is here so the *why* of each rule stays visible — if a refactor tempts you to bypass one, the physical referent is the test.

### Physical fidelity is primary

Each component exposes only the interfaces a real component has. If you couldn't do it with a soldering iron, you cannot do it in code.

**Why:** Every other rule below is a corollary of this one. A class that surfaces an interface no physical part offers is no longer modelling the part — it's modelling something convenient for software, which is what the framework was built to refuse.

### Callable components (functor pattern)

Every component implements `__call__` as its sole signal interface. Invoke components like functions — input in, output out — because that is what physical components are.

**Why:** A real component has no API beyond its electrical interface. A resistor has two leads; you apply a signal, you read a signal. Methods named `apply()` or `update()` are software-layer convenience that has no physical analogue — and once present, they're how the framework's discipline starts leaking.

### No direct state manipulation

Component state may only change via the designated signal path (`__call__`). Never add setters, mutator methods, or public attributes that allow state to be written directly from outside.

**Why:** A real LED isn't lit because something wrote `True` to it — it's lit because current flows from anode to cathode. Setters that bypass the signal path break the *the code matches the breadboard* contract: a `wire()` failure can no longer guarantee the component is in a defined state.

### Explicit wiring in composite components

When composing components, the wiring must be written out explicitly and directionally — each line is a wire, signal flows one way. No component knows about any other; they are connected only by the composite's `__call__` method.

**Why:** Every `wire()` call is a jumper on the breadboard. Hiding the wiring inside a helper or a loop hides the topology — and the framework's whole construction-time validation pass walks the explicit `wire()` calls to detect shorts, floats, and ground-domain crossings. Implicit wiring would have nothing to walk.

### `__slots__` on every component

All component classes must declare `__slots__`. Physical components cannot grow new pins at runtime.

**Why:** A real chip's pinout is fixed at the factory. A class without `__slots__` can grow attributes (and ports) at runtime through accidental assignment — which would be a part that magically grows a third terminal once installed. The framework relies on the pin count being immutable when it validates net topology; `__slots__` is what makes that load-bearing.

### Invalid states must raise

Hardware has forbidden states (e.g. S=R=1 on an SR latch). Model them with leaves from `framework.errors` — `ForbiddenStateError`, `PartParameterError`, `PartConfigurationError`. Never raise bare `ValueError` / `TypeError`.

**Why:** Real silicon doesn't ignore S=R=1 on an SR latch — it enters an undefined state that often costs hardware. The framework's job is to refuse those states with a specific, named exception so the designer learns *what's wrong physically*, not just *something raised*. Bare `ValueError` collapses every defect class into one bucket and erases the teaching the hierarchy was built to deliver.

### Signal types: always `Analog` and `Digital`

Ports, wiring, and signal handling must use `Analog` / `Digital` — never raw `float` / `bool`.

**Why:** Real copper carries either a continuous voltage or a logic level — never both, never something in between. Tagging ports with `Analog` / `Digital` is how the framework refuses cross-type wires at construction time; using raw `bool` / `float` collapses both worlds into one untyped substrate and the check disappears.

### Output polarity matches physical pin behaviour

Model the pin voltage, not the internal device state. An open-collector output is LOW when conducting and HIGH when off — drive `False` for the conducting case.

**Why:** The framework models pins, not silicon insides. A downstream component reading `True` from an open-collector pin should see HIGH (the rest state) — which is what a multimeter would read at that pin. Inverting the polarity inside the part to make the wiring "look right" hides a real-world inversion the schematic still has to show.

### Hardware-pin-name parameters

`__call__` parameter names must be hardware pin names (`s`, `r`, `v_plus`) — not application-layer names (`low`, `high`, `sensor`).

**Why:** Pin names are the join between the model and the datasheet. A reader cross-referencing the chip's pinout should land on the same identifier wirebench uses; software-layer names break that cross-reference and force the reader to translate.

### What not to do

- **No convenience methods that bypass the signal path.**
  *Why:* A real part has no API beyond its electrical interface. Convenience methods are a software-layer concern; once present, they're how the *callable components* discipline starts leaking and downstream code grows habits that no longer match what the breadboard does.

- **No logging, observers, or callbacks inside component classes.**
  *Why:* A physical resistor has no logger. Observers and callbacks belong to the surrounding orchestration (the harness, the simulator, the visualiser) — not to the part itself. Putting them on the component invites a class hierarchy that diverges from physical reality.

- **No inheritance between component types — compose, don't inherit.**
  *Why:* Physical parts don't inherit. A comparator and an op-amp share a package shape and some pin-name conventions, but they're distinct silicon. Inheritance would assert an *is-a* relationship the datasheets don't claim; composition (one part instantiating another as an internal cell) matches how real parts are designed.

- **No default power-on state unless the real part has one.**
  *Why:* A real chip at power-on may be in any state its silicon allows; some latch types come up in a defined state, most don't. A scaffold that initialises every component to a defined state lies about the bench reality — the user's downstream check for "is this in the right state yet?" never sees the indeterminate-at-power-on case the real chip exhibits.

### Scaffolding a new component

`scripts/scaffold_component.py` machine-applies the rules above. See [`CONTRIBUTING.md`](https://github.com/raeq/wirebench/blob/main/CONTRIBUTING.md#adding-a-new-part) for the invocation; the scaffold's output passes every framework rule by construction, so the contributor only fills in part-specific specification (pin logic, `VERIFY` / `GOTCHAS` strings, layout descriptor).

## Further reading

- The source code at [github.com/raeq/wirebench](https://github.com/raeq/wirebench) — every framework primitive is annotated with comments explaining the design decisions and trade-offs that produced its current shape.
