# The rules

The framework enforces a small, fixed set of construction-time rules. Each one corresponds to a real-world failure mode that costs at the bench — overheated outputs, undefined logic levels, parts that won't seat, boards that don't power up. The rules feel arbitrary if you encounter them one at a time; they're principled if you see the whole set on one page with the physical referent for each.

This page is the index. For each rule:

- **The rule itself**, one sentence.
- **Why** — the physical-world referent.
- **What fires** — the exception class wirebench raises ([source](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py)).
- **First caught at** — the demo where you'll meet this rule for the first time if you walk the [learning path](learning-path.md) top to bottom.

By the time you've worked through `hello_led/` + `water_alarm/` + `5v_rail_power/` + `digital_thermometer/` + `fan_cooling/` + `isolated_rs232/` + `li_ion_fuel_gauge/`, you've seen the framework catch every rule on this page in a real demo. The rules aren't aspirational — they're the load-bearing checks that keep "the code matches the breadboard" honest.

## Rule 1 — One driver per logical net

If two ports declared `Direction.OUT` end up on the same logical net, `wire()` (or `Circuit._validate` for nets joined through `mate()`) raises [`ShortCircuitError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** Two OUT-direction ports on one net fight each other on the copper. Current sinks through the losing output stage until the FETs overheat. Real silicon has one driver per shared conductor.

**First caught at:** [`hello_led/`](../demos/hello_led/) — the *shorted supply* near-miss snippet.

## Rule 2 — Every BIDIR-only net needs a driver

A net touched only by passive BIDIR ports (resistor terminals, capacitor leads, connector contacts) with no OUT-direction driver anywhere raises [`FloatingNetError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A net with no driver has no defined voltage. CMOS inputs in particular drift to mid-rail and oscillate, picking up nearby switching noise as if the trace were an antenna. The bench equivalent is *"but the LED still lit up"* — a working observation that hides a silent miswire.

You can opt out with `wire(*ports, dynamically_driven=True)` when the net is driven through the surrounding loop (op-amp positive feedback, RC timing networks). The opt-out is the designer's explicit assertion that the framework's static check should yield to a known dynamic driver.

**First caught at:** [`hello_led/`](../demos/hello_led/) — the *floating resistor* near-miss snippet.

## Rule 3 — Mandatory pins must be connected

Some pins are declared `mandatory=True` because the part doesn't function without them — regulator inputs, op-amp V+ supplies, MCU VDD, MCU GND. Leaving any of them unwired raises [`UnconnectedPinError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A mandatory pin left in air leaves the silicon stage tied to nothing. The part either doesn't power up at all (no current path) or behaves unpredictably (floating reference). The bench equivalent is a board that arrives, populates, and refuses to come on — every solder joint is fine, but one wire was missing in the schematic.

**First caught at:** [`5v_rail_power/`](../demos/5v_rail_power/) — the *floating regulator input* near-miss.

## Rule 4 — Signal types stay matched

Every port carries one of two signal families: `Analog` (continuous voltage) or `Digital` (logic level). Mixing them across a `wire()` raises [`SignalTypeMismatchError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** An Analog continuous voltage and a Digital logic level can't share copper — one is a value in volts, the other a one-or-zero state. Converting between them needs an explicit interface (comparator, ADC, level-shifter). The framework refuses the direct wire so the conversion stays visible in the design.

A BIDIR port declared as the generic `Analog` base class acts as a *conductor wildcard* — a piece of copper that takes on whatever type the rest of the wire imposes. This is what lets connector contacts and resistor terminals join either domain without breaking the discipline.

**First caught at:** [`li_ion_fuel_gauge/`](../demos/li_ion_fuel_gauge/) — the *signal-type mismatch on the chip-enable pin* near-miss.

## Rule 5 — Ground domains stay isolated

A `wire()` (or any port-to-node attachment) that crosses two distinct `GroundDomain` instances raises [`DomainCrossingError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** Two ground domains share a net only through an isolator (optocoupler, digital isolator, transformer). A direct wire would tie the references together and defeat the isolation that's the entire point of having two domains. In `isolated_rs232/`, the host-side and iso-side domains exist because the design's whole purpose is keeping them separate at high voltage; collapsing them with a stray jumper would silently undo the isolation.

The framework allows isolator cells (e.g. `ISOW7841`, `Optocoupler`) to have ports in different domains as the legitimate way to bridge.

**First caught at:** [`isolated_rs232/`](../demos/isolated_rs232/) — the *cross-domain wire* near-miss.

## Rule 6 — Connectors only mate with their declared partner

Every connector class declares its physical mate via `MATES_WITH`. Calling `mate(a, b)` where `type(b)` isn't `type(a).MATES_WITH` raises [`IncompatibleMateError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A USB-A receptacle and a TRRS audio jack have different shells, different pin counts, different pitches. Calling them mated is asserting a fact contradicted by the mechanical drawings. The bench equivalent is a parts order with the wrong cable type — the cable arrives and won't seat. The framework catches the mismatch when the code says `mate()`, before the order ships.

**First caught at:** [`fan_cooling/`](../demos/fan_cooling/) — the *wasted parts order — wrong connector mated* near-miss.

## Rule 7 — Connectors match on pin count and pitch

Even when the connector families agree, two connectors with mismatched `pin_count` or `pitch_mm` won't physically seat. Mismatches raise [`PinCountMismatchError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py) or [`PitchMismatchError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A 4-pin plug into a 5-pin receptacle leaves one pin unmated; a 2.54 mm plug into a 2.00 mm receptacle lands the pins between contacts, not on them. Either way the connection is physically incomplete. As with Rule 6, the bench equivalent is a parts order that arrives, doesn't fit, and goes back.

**First caught at:** [`fan_cooling/`](../demos/fan_cooling/) — the *wrong-pin-count power plug* near-miss.

## Rule 8 — Refdes uniqueness per circuit

Every part on a real board carries a one-of-a-kind reference designator (`R1`, `U2`, `D3`). Two parts in the same `Circuit` sharing a refdes raises [`RefdesError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** The refdes is the join key between the schematic, the BOM, the assembly drawing, and the manufactured PCB. If two parts share one, the BOM is ambiguous, the assembler doesn't know which footprint to populate, and the schematic and the layout disagree about which symbol corresponds to which footprint. A duplicate refdes is the documentation equivalent of a short circuit — two things claiming to be the same thing.

**First caught at:** the framework rejects this at construction time on every demo; the surface comes up the first time you accidentally write `refdes_number=1` twice in your own design.

## Rule 9 — Forbidden states stay forbidden

Some logical states are valid wirings whose evaluation produces undefined or destructive output: SR latch with S=R=1, three-phase Hall pattern (0,0,0) or (1,1,1), half-bridge shoot-through. The framework refuses to evaluate them and raises [`ForbiddenStateError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** Real silicon refuses to enter these states — or worse, enters them once and lets the smoke out. The SR latch with both inputs high is the canonical example: each NOR gate would force the other to zero, so neither output settles, and the chip behaviour is undefined. The framework catches this at `evaluate()` time and names the offending state with a suggested fix (drive the two inputs from mutually-exclusive sources, or use a latch type with no forbidden state).

**First caught at:** [`water_alarm/`](../demos/water_alarm/) — the *locked-up latch* near-miss (S=R=1 on the NOR latch).

## Rule 10 — `wire()` doesn't merge pre-existing nets

A `wire()` whose ports are already on two distinct nodes would silently fuse independent design intent into one net. The framework refuses and raises [`NodeMergeError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** Mergeing nets at construction time is a footgun for boards being composed from sub-circuits — a wire intended to extend one net could accidentally connect it to a parallel net the author hadn't realised was nearby. The framework requires the join to be explicit: refactor the code so the two nets are constructed together, or use a `Pin` / connector mate to bridge them deliberately.

**First caught at:** framework-internal — surfaces when you copy-paste a wiring block and one of the destinations is already wired into the parent circuit.

## Rule 11 — Empty wires aren't wires

`wire()` called with zero or one port raises [`EmptyWireError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A wire with no endpoints connects nothing to nothing — it has no physical analogue on a real breadboard. A wire with one endpoint connects something to nothing — same problem. The framework refuses both shapes immediately so accidental `wire()` calls in a refactor don't sit silently in the source.

**First caught at:** framework-internal — surfaces when refactoring removes a port from a `wire()` call and leaves the call with one or zero remaining ports.

## Rule 12 — A wired chip can't be called standalone

A chip whose ports are wired into a parent circuit must be driven through that circuit's `evaluate()`. Calling the chip's standalone `__call__` raises [`WiredChipCallError`](https://github.com/raeq/wirebench/blob/main/src/framework/errors.py).

**Why:** A wired chip's pins are receiving values from the circuit; calling the chip directly with arguments would bypass those wired values and produce a result inconsistent with the rest of the design. The framework treats the chip's standalone callable as a *standalone interface* — useful only when the chip is being exercised in isolation. Once it's part of a wired circuit, the parent owns the evaluation order.

**First caught at:** framework-internal — surfaces when you try to unit-test a chip that's already been instantiated as part of a composite.

## How the rules compose

The rules aren't independent — they reinforce each other. A `mate()` call validates Rule 6 + Rule 7 *and* invokes `wire()` per pin pair, which then validates Rules 1, 2, 4, and 5 on the bridged nets. A `Circuit` construction validates Rule 3 (mandatory pins) and Rule 8 (refdes uniqueness) *and* re-runs Rules 1 and 2 at the *logical net* level — catching shorts and floats that span multiple `wire()` calls through transparent conductors (Pins, connector contacts, transparent composites).

The cumulative effect is the framework's value proposition: a design that passes construction is topologically buildable. Every wire in the source maps to a wire on the breadboard, every chip's pin numbers match the datasheet, every connector mates with what its mechanical drawing says it mates with, and no electrical impossibility the framework can detect at construction time is hiding behind a passing test run.

For the abstract treatment of *why* these rules exist as a single coherent design, see [Design principles](design-principles.md). For graduated exposure to the rules through the demos that catch each one, see [Learning path](learning-path.md).
