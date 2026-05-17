# What wirebench prevents — comparison with KiCad ERC and SKiDL ERC

This benchmark puts wirebench side-by-side with KiCad ERC (the
established schematic-checking tool) and SKiDL ERC (the closest
code-first competitor) across 20 defect classes spanning four bench
harms: burnt components, wasted bench sessions, hours of fault-tracing,
and wrong-part purchases. For each row we record **whether** each tool
catches the defect and **at what stage** — `construct` (when the design
is built in code), `erc` (when the user runs ERC), `never` (no built-in
check fires), or `scope` (the tool explicitly doesn't model the
concept).

The wedge is the stage axis: `construct` < `erc` < `never`. A defect
caught at `construct` is one the user never has to think about again.

## Methodology

Each row is backed by a minimal-reproducer test case archived under
`.plans/prevention-benchmark/{wirebench,skidl,kicad}/`. The wirebench
and SKiDL columns are verified output from `uv run python <reproducer>`
on this machine; re-running any script will reproduce the recorded
message.

| Tool      | Version | How ERC ran |
|-----------|---------|-------------|
| wirebench | 0.1.0 (current `main`) | Each reproducer either raises at wire/mate/`__init__` time (the `construct` stage) or calls `export_to_string(design, 'assembly_guide')` which runs the assembly-guide ERC (the `erc` stage). |
| SKiDL     | 2.2.3 (PyPI, installed via `uv pip install skidl`) | Each reproducer calls `ERC()` and the salient line is captured from stdout. The SKiDL built-in library was used (`set_default_tool(SKIDL)`) — the KiCad symbol library was not available in this environment. |
| KiCad ERC | *not installed* | **Pending hands-on capture** — `kicad-cli` wasn't installed when this document was first written, so the KiCad cells below reflect *documented* ERC behaviour rather than measured output. See [`../.plans/prevention-benchmark/kicad/README.md`](../.plans/prevention-benchmark/kicad/README.md) for what each schematic should contain and the expected ERC substring. Re-run with `kicad-cli sch erc` and update each cell when the schematics land. |

Cells marked **pending** are the unverified ones. Cells marked
`construct` / `erc` / `never` / `scope` reflect *what the tool actually
did on this machine*.

## The comparison

### Burnt components

Defects that physically damage parts on assembly.

| Defect | wirebench | KiCad ERC | SKiDL ERC |
|---|---|---|---|
| **#1** Two outputs wired to one net | **construct** — `ShortCircuitError: wire() has multiple drivers ('y_1', 'y_2') — short circuit` | erc *(pending)* — *"Pins of type Output and Output are connected"* | **erc** — `ERC ERROR: Pin conflict on net OUT_NET, OUTPUT pin 4/~ ... <==> OUTPUT pin 2/~ ... (OUTPUT connected to OUTPUT)` |
| **#2** Two power rails wired together via a mated connector pair | **construct** — `NodeMergeError: wire() would merge two existing nodes — not supported` (raised by `mate()`) | erc *(pending)* — *"Net X has conflicting power signals"* | erc — `ERC WARNING: Merging two named nets (VCC and SHARED_PIN_1) into VCC` (warning, not error) |
| **#3** Two MCU GPIOs both configured as output driving one line | **never** — GPIOs are modelled as `Direction.BIDIR`; the OUT/OUT conflict is a runtime firmware state wirebench doesn't see | erc *(pending)* — *"Bidirectional / Bidirectional"* (typically a warning) | never — BIDIRECTIONAL pin type doesn't trigger pin-type-matrix error |
| **#4** Reverse-polarity battery wiring (battery `+` to circuit GND) | **construct** — `ShortCircuitError` *(via two drivers on one net; this is topologically correct but the framework has no polarity-aware predicate that would surface the defect as a polarity error)* | never *(pending)* — KiCad treats both as nets; no polarity predicate | never — `+` lives on GND net but no specific catch |
| **#5** Missing current-limit resistor on an LED | **scope** — the README is explicit: wirebench doesn't model continuous current | scope *(pending)* — no current model in schematic ERC | scope — no current model |

### Wasted bench sessions

Defects that prevent the design from working but don't damage anything.

| Defect | wirebench | KiCad ERC | SKiDL ERC |
|---|---|---|---|
| **#6** Floating chip OUT pin (no internal driver, no `cells=[]` entry) | **construct** — `PartConfigurationError: BrokenInverter declares pin 'y' (pin 2) as Direction.OUT but no behavioural cell drives its internal face` | scope *(pending)* — symbols don't have "internal cells" | scope — no model of chip internals |
| **#7** Unconnected MCU RESET pin (no driver, no pull-up) | **erc** — `BreadboardIncompatibleError: Chips have floating reset pins ... wire each pin below either to a driver or through a pull-up resistor to the + rail` | erc *(pending)* — generic *"Pin not connected"* warning on RESET | erc — `ERC WARNING: Unconnected pin: BIDIRECTIONAL pin 1/~{RESET}/PC6 of ATmega328P-P/U1` *(generic, not RESET-specific)* |
| **#8** Floating analog reference (AREF / VREF) | **erc** — `BreadboardIncompatibleError: Chips have undriven reference pins ... wire each pin below to a Rail, a regulator output, or a divider tap` | erc *(pending)* — generic *"Pin not connected"* warning | erc — generic unconnected-pin warning |
| **#9** Missing CLOCK_IN driver on a chip without internal oscillator | **erc** — `BreadboardIncompatibleError: Chips have unwired clock-input pins ... wire each pin below to an oscillator / clock-output source, or set INTERNAL_OSCILLATOR = True on the chip class` | erc *(pending)* — generic *"Pin not connected"* warning | erc — generic unconnected-pin warning |
| **#10** Forgotten supply pin (VCC unwired on a chip) | **erc** — `BreadboardIncompatibleError: Chips have unwired supply pins ... wire each pin below to its rail` | erc *(pending)* — *"Input power pin is not driven"* | erc — `Only one pin (POWER-IN pin 7/GND of 74HC04/U1) attached to net GND` |
| **#11** Unmated receptacle with no plug-side part | **construct** — `UnmateableError: ScrewTerminalBlock has no in-model mate (MATES_WITH is None — user-facing receptacle)` | scope *(pending)* — no mating-pair model | scope — no mating-pair model |

### Hours of fault-tracing

Defects that produce intermittent / erratic behaviour.

| Defect | wirebench | KiCad ERC | SKiDL ERC |
|---|---|---|---|
| **#12** Open-drain output without a pull-up resistor | **erc** — `BreadboardIncompatibleError: Chips have open-drain / open-collector pins without a pull-up resistor to the + rail` | scope *(pending)* — no OD-specific predicate | scope — OD pin type exists but no pull-up requirement check |
| **#13** Forbidden runtime state on SR latch (S=1, R=1) | **runtime** — `ForbiddenStateError: Invalid: S and R both active` *(raised by `NORLatch.evaluate()` — caught when the circuit is simulated, not at design time)* | scope *(pending)* — KiCad has no runtime simulator | scope — SKiDL has no runtime simulator |
| **#14** Ground-domain crossing without an isolator | **construct** — `DomainCrossingError: Cannot wire ports across ground domains: 'a' (electrical), 'b' (SECONDARY)` | scope *(pending)* — no ground-domain model | scope — no ground-domain model |
| **#15** Chip declares OUT pin but no behavioural cell drives it | **construct** — `PartConfigurationError: PartiallyDriven declares pin 'y_2' (pin 3) as Direction.OUT but no behavioural cell drives its internal face` *(sister to #6 — same invariant, different geometry)* | scope *(pending)* — same as #6 | scope — same as #6 |
| **#16** I²C peripheral SCL pull-up missing | **never** — SCL on most peripherals is `Direction.IN`; no drive-type predicate fires *(SDA pull-up IS caught via the OPEN_DRAIN predicate — see #12)* | scope *(pending)* — no I²C-aware predicate | scope — no I²C-aware predicate |

### Wrong-part purchases

Defects in BOM / connector specifications that show up when the wrong
parts arrive.

| Defect | wirebench | KiCad ERC | SKiDL ERC |
|---|---|---|---|
| **#17** Connector pair mismatch (male header mated to JST cable) | **construct** — `IncompatibleMateError: Header1xNMale mates with Header1xNFemale, not JSTPHCableHousing` | scope *(pending)* — no physical-mate predicate | scope — no mating-pair model |
| **#18** Connector pin-count mismatch (1×4 male to 1×6 female) | **construct** — `PinCountMismatchError: Pin count mismatch: Header1xNMale has 4, Header1xNFemale has 6` | scope *(pending)* — no mate-time pin-count check | scope — no mating-pair model |
| **#19** Connector pitch mismatch (2.54 mm vs 1.27 mm) | **construct** — `PitchMismatchError: Pitch mismatch: Header1xNMale is 2.54 mm, Header1xNFemale is 1.27 mm` | scope *(pending)* — no pitch model at schematic level | scope — no pitch model |
| **#20** Receptacle declared with no matching plug class registered | **construct** — `UnmateableError: WeirdEdgeConnector has no in-model mate (MATES_WITH is None — user-facing receptacle)` | scope *(pending)* — no mating-pair model | scope — no mating-pair model |

## What wirebench doesn't yet catch

The benchmark surfaced these defects where wirebench under-catches
relative to a documented competitor or to the bench reality. Each one
becomes a candidate Phase 2 / Phase 6 work item.

### Gap A — runtime-only conflicts on BIDIR ports (defect #3)
Two MCU GPIOs both configured as output by firmware show up as
"two BIDIR ports on a net" — which wirebench correctly allows at
design time, because both *could* be inputs. The defect only exists
once firmware assigns directions. KiCad and SKiDL also fail to catch
this cleanly (their BIDIRECTIONAL pin type behaves the same way).
**Work item:** model per-GPIO firmware configuration as a separate
construct-time annotation (`Chip.PIN_DIRECTIONS_AT_RUNTIME`) and
re-check the OUT/OUT conflict against that map.

### Gap B — reverse-polarity battery wiring (defect #4)
Wirebench raises `ShortCircuitError` — but only because both terminals
happen to be `Direction.OUT`, not because the framework recognised that
the battery's `+` was tied to the system ground. **Work item:** add an
`IS_POLARISED` class attribute on polarised parts (Cell, electrolytic
cap, LED, rectifier diode) and a polarity-aware check that flags `+`
terminals connecting to known-ground nets, raising a new
`PolarityError` (to be reintroduced alongside its raise site, as one
coherent change).

### Gap C — missing I²C SCL pull-up (defect #16)
Wirebench catches missing SDA pull-ups via the OPEN_DRAIN predicate,
but SCL is modelled as `Direction.IN` on peripherals — no drive-type
predicate fires. **Work item (Phase 6.1):** add an I²C-bus check
that, on any chip whose `PIN_DRIVE_TYPES` includes SDA as OPEN_DRAIN,
also requires SCL to have a path to a pull-up.

### Gap D — runtime-only defects need a separate execution path (defect #13)
The SR-latch S=R=1 catch only fires when the latch's `evaluate()` is
called. There's no static analyser that flags "the user's circuit
would trip this latch's forbidden state under any input." This is
real — but it's a simulation-coverage gap, not a missing check.
**Work item:** none (this is acceptable; wirebench is honest that
runtime defects need runtime exercise).

## What only wirebench catches

The wedge made specific. Each row is a defect wirebench catches at
`construct` while the other two tools catch it later or not at all.

- **#6 / #15 — Floating chip OUT pin (Chip declares an OUT pin but
  nothing internally drives it).** Caught at `Chip.__init__` with
  `PartConfigurationError`. Neither KiCad nor SKiDL has a "chip
  internal cell" concept; both can only ask whether the *external*
  pin is wired, not whether the *internal* silicon drives it. The
  bench equivalent is: a `74HC04` whose datasheet promises six
  inverters but whose silicon ships dead. KiCad / SKiDL would let you
  build the whole assembly and only discover the dead pin at first
  power-on.

- **#11 — Unmated receptacle with no plug-side part / #17 — Connector
  pair mismatch / #18 — Pin-count mismatch / #19 — Pitch mismatch.**
  All four caught at `mate()` time as
  `UnmateableError` / `IncompatibleMateError` / `PinCountMismatchError`
  / `PitchMismatchError`. The bench equivalent is the user discovering
  that the 2.54 mm header they bought doesn't fit the 1.27 mm socket
  on the dev-board they're connecting to — *after* the order arrives.
  KiCad and SKiDL netlists treat connectors as collections of pins
  with no mating semantics; the same wrong-pitch wiring passes ERC.

- **#14 — Ground-domain crossing without an isolator.** Caught at
  `wire()` with `DomainCrossingError`. KiCad and SKiDL have no
  GroundDomain model — they treat every net as part of one electrical
  system. The bench equivalent is wiring a mains-side ground directly
  to a USB-side ground through an "isolated" optocoupler that wasn't.

- **#7 / #8 / #9 / #10 / #12 — RESET / REFERENCE / CLOCK_IN / POWER /
  open-drain pin role checks.** Caught at `erc` (assembly-guide ERC)
  with messages that name the pin's *role* — "Chips have floating
  reset pins ... wire each pin below either to a driver or through a
  pull-up resistor to the + rail." KiCad and SKiDL surface the same
  pins, but only as generic "Pin not connected" warnings — the user
  has to know which pins are RESETs and which are signal pins. The
  bench equivalent is a printout that says "RESET pin — wire a
  pull-up" instead of "16 unconnected pins, good luck."

The lesson is consistent: wirebench's catches are *role-aware* and
*physical-mate-aware*. KiCad and SKiDL are *net-aware*. When the
defect lives in a layer above pure connectivity, wirebench has
purchase that the established tools don't.
