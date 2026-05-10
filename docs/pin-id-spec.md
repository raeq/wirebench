# Pin Identity (PinId) — Implementation Spec

## 1. Purpose

Give every physical pin on a chip package or connector housing both its **datasheet pin number** (what the silkscreen, schematic, and netlist reference — `pin 7`, `pin 14`) and its **functional name** (what the circuit author writes — `a_1`, `VBUS`, `GND`). Today the codebase only carries the name; this work adds the number alongside it, so that downstream tools (SPICE subcircuit invocation, KiCad netlist references, schematic capture, PCB layout) have the canonical identifier they need.

Both fields ride on a single `PinId` immutable value object. After this work, every `Pin` instance and every `Connector` PINOUT entry carries a `PinId`, and exporters can sort pins by number, look them up by number, and print either form to the user.

## 2. Scope

**In scope** — a `PinId` frozen dataclass; threading it through `Pin.__init__` (replacing the bare `name: str`); updating the `Connector.PINOUT` schema to use `PinId`; updating `_build_pinout()` synthesisers in parameterised connector families; assigning datasheet pin numbers to every existing chip's `Pin` constructions; the matching test suite.

**Out of scope** — pin numbers on passive components (`Resistor`, `LED` — their two terminals are conventionally numbered 1/2 but adding explicit `PinId`s is a separable refinement); adding VCC/GND pins to chips whose existing model omits them; netlist exporters that consume the new metadata; any rewrite of port routing or the wiring graph.

**Prerequisites** — none from the project's existing work packages (`refdes-spec.md` and `board-connector-spec.md`). This spec sits between them in dependency order: refdes is independent; board-connector currently uses bare-string PINOUTs and must be updated as a follow-on (see §11).

## 3. Constraints carried over from CLAUDE.md

- Physical fidelity is primary. `PinId` describes a real attribute of a physical pin (its number on the package, its functional name in the datasheet). It is honestly identified as data — an identifier — not as a fake physical thing.
- `__slots__` everywhere. `PinId` is `frozen=True, slots=True` so the dataclass produces a real slotted class.
- No setters. `PinId` is frozen; once built, the number and name are immutable. Once a part is moulded, pin 5 cannot become pin 6.
- Stdlib only. Use `dataclasses.dataclass`, not pydantic. Pydantic earns its keep at JSON / external-data boundaries; `PinId` is constructed in code and consumed in code, so the heavy machinery has no work to do here. (If pydantic enters the project later for the sidecar-JSON / serialisation work package, migrating `PinId` to `pydantic.dataclasses.dataclass` is a five-line change.)
- No new framework primitive when reusing data on an existing class will do. `PinId` is data on `Pin`; it is not a new node type in the graph.

## 4. The `PinId` dataclass

New code at the top of `src/framework/pin.py` (so it is co-located with the only class that owns it):

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PinId:
    """The identity of a pin on a physical package: its 1-indexed pin
    number (its position on the package, as stamped on silkscreen and
    called out in the datasheet) plus its functional name (what the
    schematic label says — 'VBUS', 'a_1', 'y_3', 'GND').

    Two pins on the same package may share a name (multiple GND pins on
    a USB-C receptacle, for example) but never a number. Numbering
    matches the manufacturer's datasheet exactly: a 14-pin DIP has pins
    1..14, a 24-pin USB-C receptacle has pins 1..24, etc. The framework
    does not invent numbers — it copies them from the datasheet.
    """

    number: int
    name: str

    def __post_init__(self) -> None:
        # bool is a subclass of int in Python; reject explicitly.
        if not isinstance(self.number, int) or isinstance(self.number, bool):
            raise TypeError(f"PinId.number must be an int; got {type(self.number).__name__}")
        if self.number < 1:
            raise ValueError(f"PinId.number must be ≥ 1; got {self.number}")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError(f"PinId.name must be a non-empty string; got {self.name!r}")

    def __str__(self) -> str:
        # Human-readable: "pin 7 (GND)". Used in error messages and reprs.
        return f"pin {self.number} ({self.name})"
```

`frozen=True` means equality and hashing are by-value: `PinId(1, 'VBUS') == PinId(1, 'VBUS')` and both hash identically — useful when collecting pins into sets or using them as dict keys (handy for exporters).

`slots=True` (Python 3.10+) gives the dataclass a real `__slots__`, aligning with the project's `__slots__` discipline and making instances cheap.

## 5. Framework changes: `Pin`

`Pin.__init__` currently takes `name: str` as its first positional argument. After this work it takes `id_: PinId` as its first positional argument. The internal `Port` instances the pin owns continue to be string-named (`Port` itself is unchanged); the pin extracts `id_.name` to set those names.

Updated signature and body:

```python
class Pin(FactorNode):
    __slots__ = ('_id', '_role', '_external', '_internal')

    def __init__(
        self,
        id_: PinId,
        direction: Direction,
        domain: GroundDomain,
        *,
        mandatory: bool = True,
        signal_type: type,
    ) -> None:
        if not isinstance(id_, PinId):
            raise TypeError(f"Pin requires a PinId; got {type(id_).__name__}")
        if direction is Direction.BIDIR:
            # BIDIR support is added by the board-connector spec; this
            # spec leaves the existing behaviour unchanged.
            raise NotImplementedError("BIDIR pins are not yet supported")
        self._id   = id_
        self._role = direction
        if direction is Direction.IN:
            self._external = Port(
                id_.name, Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
        else:  # OUT
            self._external = Port(
                id_.name, Direction.OUT, domain,
                mandatory=False, signal_type=signal_type,
            )
            self._internal = Port(
                f'{id_.name}_inner', Direction.IN, domain,
                mandatory=mandatory, signal_type=signal_type,
            )

    @property
    def id(self) -> PinId:
        return self._id

    @property
    def number(self) -> int:
        return self._id.number

    @property
    def name(self) -> str:
        return self._id.name

    # `external`, `internal`, `ports`, `evaluate` unchanged.

    def __repr__(self) -> str:
        return f"Pin({self._id}, {self._role.value})"
```

Three convenience properties are added — `id`, `number`, `name` — to spare exporters a `pin.id.number` round-trip. `name` continues to be `Pin`'s human-readable identifier and matches what `Port.name` already returns.

## 6. Framework changes: `Connector` PINOUT

The board-connector spec defines `Connector.PINOUT` as a tuple of `(name: str, direction: Direction, signal_type: type)` entries. After this work the first element of each tuple is a `PinId`:

```python
PINOUT: ClassVar[tuple[tuple[PinId, Direction, type], ...] | None] = None
```

Concrete fixed-geometry connectors (USB-A, USB-C, RJ45, HDMI, etc.) declare PINOUTs with explicit numbers and names per the connector datasheet. Example for `USBAReceptacle`:

```python
PINOUT = (
    (PinId(1, 'VBUS'),  Direction.BIDIR, Analog),
    (PinId(2, 'D_neg'), Direction.BIDIR, Analog),
    (PinId(3, 'D_pos'), Direction.BIDIR, Analog),
    (PinId(4, 'GND'),   Direction.BIDIR, Analog),
)
```

Parameterised connector families' `_build_pinout()` synthesisers produce `PinId(i, f'p{i}')` per contact — number and name coincide, which is exactly right for a generic 0.1" header where there is no functional name beyond the position:

```python
def _build_pinout(self):
    return tuple(
        (PinId(i, f'p{i}'), Direction.BIDIR, Analog)
        for i in range(1, self._pin_count + 1)
    )
```

The board-connector spec's §6 (Connector base class), §7 (every connector subclass), and `Board`'s surface-port qualification (`f"{connector.refdes}.{pin_name}"`) all carry forward unchanged — `pin_name` continues to be a string drawn from `pin.id.name`. The only mechanical edit is the PINOUT tuple shape.

## 7. Pin number assignments for existing chips

Each existing chip class instantiates `Pin` objects with bare string names. After this work each `Pin(...)` call passes a `PinId(number, name)` whose number matches the manufacturer's datasheet for the assumed package. The package conventions are stated below; the spec assumes the standard DIP layout for each part because that is the form most readily reasoned about and exported.

**Note on omitted pins.** Several chip classes intentionally leave VCC/GND off the model (the docstrings explicitly say so). This spec does **not** add them — it only assigns numbers to the pins that already exist. Adding power pins is a separable work package. Where a model omits a pin, that pin number is simply absent from the chip's pin list.

**Note on synthesised / derived ports.** If a chip class exposes a port that does not correspond to a physical package pin (for example, if `CD4043` synthesises a `q_bar` output that the real part does not provide on the package), that port does **not** get a `PinId`. The implementer should flag any such discrepancy during the pin-number pass; the resolution is to either (a) drop the synthetic port from the chip's surface in this work package, or (b) document it as a known divergence to be cleaned up by a follow-on. Do not invent a fake pin number for it.

### 7.1 SN74HC04 — hex inverter, 14-pin DIP

Per Texas Instruments SN74HC04 datasheet (DIP/SOIC pinout):

| Pin | Functional name | Codebase port name | In model |
|----:|-----------------|--------------------|---------|
|  1  | 1A              | `a_1`              | yes     |
|  2  | 1Y              | `y_1`              | yes     |
|  3  | 2A              | `a_2`              | yes     |
|  4  | 2Y              | `y_2`              | yes     |
|  5  | 3A              | `a_3`              | yes     |
|  6  | 3Y              | `y_3`              | yes     |
|  7  | GND             | —                  | no (omitted) |
|  8  | 4Y              | `y_4`              | yes     |
|  9  | 4A              | `a_4`              | yes     |
| 10  | 5Y              | `y_5`              | yes     |
| 11  | 5A              | `a_5`              | yes     |
| 12  | 6Y              | `y_6`              | yes     |
| 13  | 6A              | `a_6`              | yes     |
| 14  | VCC             | —                  | no (omitted) |

### 7.2 CD4069UB — hex inverter, 14-pin DIP

Per onsemi/TI CD4069UB datasheet:

| Pin | Functional name | Codebase port name | In model |
|----:|-----------------|--------------------|---------|
|  1  | A1 (input 1)    | `a_1`              | yes     |
|  2  | B1 (output 1)   | `y_1`              | yes     |
|  3  | A2              | `a_2`              | yes     |
|  4  | B2              | `y_2`              | yes     |
|  5  | A3              | `a_3`              | yes     |
|  6  | B3              | `y_3`              | yes     |
|  7  | VSS (GND)       | —                  | no      |
|  8  | B4              | `y_4`              | yes     |
|  9  | A4              | `a_4`              | yes     |
| 10  | B5              | `y_5`              | yes     |
| 11  | A5              | `a_5`              | yes     |
| 12  | B6              | `y_6`              | yes     |
| 13  | A6              | `a_6`              | yes     |
| 14  | VDD (VCC)       | —                  | no      |

(Same pin-number layout as SN74HC04 because both are 14-pin DIP hex inverters with the conventional CMOS inverter pinout. The CD4069 datasheet labels the in/out pairs A/B; the codebase normalises to `a_*`/`y_*` across both chips.)

### 7.3 LM393 — dual comparator, 8-pin DIP

Per Texas Instruments LM393 datasheet:

| Pin | Functional name | Codebase port name | In model |
|----:|-----------------|--------------------|---------|
|  1  | 1OUT            | `out_1`            | yes     |
|  2  | 1IN−            | `in_minus_1`       | yes     |
|  3  | 1IN+            | `in_plus_1`        | yes     |
|  4  | GND             | —                  | no      |
|  5  | 2IN+            | `in_plus_2`        | yes     |
|  6  | 2IN−            | `in_minus_2`       | yes     |
|  7  | 2OUT            | `out_2`            | yes     |
|  8  | VCC             | —                  | no      |

Implementer: confirm the exact codebase port names for the comparator inputs (`in_plus_*` vs `v_plus_*` etc.) and reconcile if different — substitute the actual names while keeping the pin numbers as listed.

### 7.4 CD4043B — quad NOR R/S latch with tri-state outputs, 16-pin DIP

Per TI/onsemi CD4043B datasheet:

| Pin | Functional name | Codebase port name | In model |
|----:|-----------------|--------------------|---------|
|  1  | Q1              | `q_1`              | yes     |
|  2  | R1              | `r_1`              | yes     |
|  3  | S1              | `s_1`              | yes     |
|  4  | Q2              | `q_2`              | yes     |
|  5  | S2              | `s_2`              | yes     |
|  6  | R2              | `r_2`              | yes     |
|  7  | OE              | `oe`               | yes     |
|  8  | VSS (GND)       | —                  | no      |
|  9  | R3              | `r_3`              | yes     |
| 10  | S3              | `s_3`              | yes     |
| 11  | Q3              | `q_3`              | yes     |
| 12  | S4              | `s_4`              | yes     |
| 13  | R4              | `r_4`              | yes     |
| 14  | Q4              | `q_4`              | yes     |
| 15  | NC              | —                  | no      |
| 16  | VDD             | —                  | no      |

### 7.5 ULN2003A — 7-channel Darlington array, 16-pin DIP

Per Texas Instruments ULN2003A datasheet:

| Pin | Functional name | Codebase port name | In model |
|----:|-----------------|--------------------|---------|
|  1  | 1B (channel 1 input)  | `in_1`        | yes     |
|  2  | 2B                    | `in_2`        | yes     |
|  3  | 3B                    | `in_3`        | yes     |
|  4  | 4B                    | `in_4`        | yes     |
|  5  | 5B                    | `in_5`        | yes     |
|  6  | 6B                    | `in_6`        | yes     |
|  7  | 7B                    | `in_7`        | yes     |
|  8  | GND                   | —             | no      |
|  9  | COM (suppression diode common) | —    | no      |
| 10  | 7C (channel 7 output) | `out_7`       | yes     |
| 11  | 6C                    | `out_6`       | yes     |
| 12  | 5C                    | `out_5`       | yes     |
| 13  | 4C                    | `out_4`       | yes     |
| 14  | 3C                    | `out_3`       | yes     |
| 15  | 2C                    | `out_2`       | yes     |
| 16  | 1C                    | `out_1`       | yes     |

Note the ULN2003A's outputs are pin-numbered in *reverse* channel order (channel 7 at pin 10, channel 1 at pin 16) — that's how the package is laid out for routing convenience. The codebase model does not need to know this; it just declares each `Pin(PinId(10, 'out_7'), ...)` per the table.

## 8. Pin number assignments for the day-1 connector library

The board-connector spec's day-1 connector library (its §7) is updated to use `PinId`-based PINOUTs. Three patterns:

**Fixed-geometry, named pins.** USB, HDMI, RJ45, audio jacks, barrel jacks, SD/microSD slots — explicit `PinId(n, 'role')` per the connector datasheet. Reference pinouts:

- `USBAReceptacle` — pins 1..4 = `VBUS`, `D_neg`, `D_pos`, `GND`.
- `USBBReceptacle` — pins 1..4 = `VBUS`, `D_neg`, `D_pos`, `GND`.
- `USBMicroBReceptacle` — pins 1..5 = `VBUS`, `D_neg`, `D_pos`, `ID`, `GND`.
- `USBCReceptacle` — pins 1..24 per the USB-C standard (A1..A12, B1..B12 in two rows; the spec uses pins 1..24 as a flat sequence with names `A1`..`A12`, `B1`..`B12`, or a more readable role-name where unambiguous — implementer's choice, but the *numbers* must match the standard).
- `RJ45Jack` — pins 1..8 with T568B-convention names (`pair2_white_orange`, `pair2_orange`, `pair3_white_green`, `pair1_blue`, `pair1_white_blue`, `pair3_green`, `pair4_white_brown`, `pair4_brown`).
- `HDMITypeAReceptacle` — pins 1..19 per the HDMI 1.4/2.0 standard.
- `Audio3p5mmTRSJack` — pins 1..3 = `tip`, `ring`, `sleeve`.
- `Audio3p5mmTRRSJack` — pins 1..4 = `tip`, `ring1`, `ring2`, `sleeve`.
- `BarrelJack5p5x2p1` and `BarrelJack5p5x2p5` — pins 1..2 = `tip`, `sleeve`.
- `MicroSDCardSlot` and `MicroSDCard` — pins 1..8 per SD spec (`dat2`, `dat3`, `cmd`, `vdd`, `clk`, `vss`, `dat0`, `dat1`).
- `SDCardSlot` and `SDCard` — pins 1..9 per SD spec (eight SD-bus pins above plus `cd` on pin 9).

Their plug-side counterparts use the same numbers and names so positional mating wires equivalently-named pins together (VBUS-to-VBUS, etc.).

**Parameterised, generic pins.** Snap-apart headers, IDC headers, JST families — `_build_pinout()` synthesises `PinId(i, f'p{i}')` per contact. Number and name coincide because the part has no functional names beyond position.

**Fixed-geometry with parameter-sized pin sets.** None in the day-1 library; reserved for future parts.

## 9. File-by-file change list

Modified files:

- `src/framework/pin.py` — add `PinId` dataclass at the top of the file; refactor `Pin.__init__` per §5; add `id` / `number` / `name` read-only properties.
- `src/framework/connector.py` — update the type annotation of `PINOUT` to use `PinId` (per §6); the parameterised `_build_pinout()` examples in the docstring/spec switch to `PinId(i, f'p{i}')`.
- `src/components/chips/sn74hc04.py` — every `Pin(name, ...)` becomes `Pin(PinId(number, name), ...)` per §7.1.
- `src/components/chips/cd4069.py` — same per §7.2.
- `src/components/chips/lm393.py` — same per §7.3.
- `src/components/chips/cd4043.py` — same per §7.4.
- `src/components/chips/uln2003a.py` — same per §7.5.

The board-connector spec's connector files (`headers.py`, `usb.py`, `network.py`, `video.py`, `audio.py`, `barrel.py`, `jst_*.py`, `screw_terminal.py`, `sd.py`, `idc.py`) all use the new PINOUT format from inception — they do not exist yet, so there is no migration to perform. The board-connector spec is updated in lockstep (see §11).

Unmodified:

- `src/framework/port.py` — `Port` continues to be string-keyed; `PinId` is a `Pin`-level concept.
- `src/framework/factor.py`, `circuit.py`, `chip.py`, `wire.py`, `node.py`, `ground.py`, `signals.py`, `units.py` — untouched.
- `src/components/passives/resistor.py`, `led.py`, `rail.py` — untouched. Passives' two-terminal naming convention (`t1`, `t2`, `anode`, `cathode`) is sufficient for now; explicit `PinId`s on passive terminals are deferred (§13).
- `src/components/chips/concepts/*.py` — cell-internal classes; their ports are not package pins and do not need `PinId`s.
- `src/applications/water_alarm.py` — driven by the chip pin-number changes only at the call sites of the chips' constructors, which do not change. The wiring that uses `chip.ports['name']` continues to work because port names are unchanged.

## 10. Test plan

New test module `tests/framework/test_pin_id.py`:

1. **Constructs with valid number and name.** `PinId(1, 'VBUS').number == 1; .name == 'VBUS'`.
2. **Equality and hashing by value.** `PinId(1, 'X') == PinId(1, 'X')`; both hash identically. `PinId(1, 'X') != PinId(2, 'X')`. `PinId(1, 'X') != PinId(1, 'Y')`.
3. **Frozen.** `pid = PinId(1, 'X'); pid.number = 2` raises `FrozenInstanceError` (or `AttributeError` per dataclass behaviour).
4. **Number must be a positive int.** `PinId(0, 'X')`, `PinId(-1, 'X')`, `PinId(1.0, 'X')`, `PinId(True, 'X')`, `PinId('1', 'X')` all raise.
5. **Name must be a non-empty string.** `PinId(1, '')`, `PinId(1, None)`, `PinId(1, 7)` all raise.
6. **`__str__` format.** `str(PinId(7, 'GND')) == 'pin 7 (GND)'`.
7. **`__slots__` is set.** `PinId.__slots__` is non-empty (the `slots=True` decorator argument took effect).

Modified test module `tests/framework/test_pin.py` (existing tests; also add new ones):

8. **Pin requires PinId, not bare string.** `Pin('a_1', Direction.IN, ELECTRICAL, signal_type=Digital)` raises `TypeError` mentioning `PinId`.
9. **Pin exposes id, number, name.** `pin = Pin(PinId(7, 'GND'), Direction.IN, ELECTRICAL, signal_type=Digital)`; `pin.id == PinId(7, 'GND')`, `pin.number == 7`, `pin.name == 'GND'`.
10. **Underlying Port carries the name.** `pin.external.name == 'GND'`; `pin.internal.name == 'GND_inner'`. (Behaviour unchanged from before; the port-name surface is preserved for existing wiring code.)
11. **`__repr__` includes the PinId.** `'pin 7 (GND)'` appears in `repr(pin)`.

Modified chip test modules (`tests/components/test_sn74hc04.py`, `test_cd4069.py`, `test_lm393.py`, `test_cd4043.py`, `test_uln2003a.py`):

12. **Each chip's pins carry the datasheet pin numbers.** For each chip, walk `chip._factor_nodes` (or whatever the pin-traversal API ends up being), filter to `Pin` instances, and assert that the set of `pin.number` values matches the §7.x table for that chip. Verify `pin.name` matches the table for each.
13. **Pin numbers are unique per chip.** Within a chip, no two pins share a number.

Existing functional tests (`test_water_alarm.py`, the per-chip behavioural tests) must continue to pass without modification — wiring uses port names, which are unchanged.

## 11. Cascade into the board-connector spec

After this spec lands, the board-connector spec (`docs/board-connector-spec.md`) requires a small editorial follow-up:

- §6: the type annotation `PINOUT: ClassVar[tuple[tuple[str, Direction, type], ...] | None]` becomes `tuple[tuple[PinId, Direction, type], ...] | None`. The phrase "tuple of (name, direction, signal_type)" becomes "(PinId, direction, signal_type)".
- §7.1's `_build_pinout()` example becomes:

  ```python
  def _build_pinout(self):
      return tuple(
          (PinId(i, f'p{i}'), Direction.BIDIR, Analog)
          for i in range(1, self._pin_count + 1)
      )
  ```

- §7.3, §7.4, §7.5, §7.6, §7.7, §7.8, §7.9 connector class definitions adopt the explicit `PinId(n, 'role')` PINOUTs from §8 of this spec.
- §15's "Pin numbers on chip pins" out-of-scope item is deleted.

These edits are mechanical and can be done as a single follow-on pass once this spec is implemented.

## 12. Acceptance criteria

The work is done when:

1. `python -m pytest` passes including the new `test_pin_id.py` and the updated chip tests.
2. `PinId` exists in `src/framework/pin.py`, is frozen and slotted, and rejects invalid numbers/names per §4.
3. `Pin.__init__` accepts a `PinId` as its first argument and rejects bare strings.
4. `Pin` exposes read-only `id`, `number`, `name` properties.
5. Every `Pin(...)` call in every existing chip class passes a `PinId` whose number matches the §7.x table for that chip.
6. The water-alarm tests continue to pass.
7. No setters added anywhere; no new mutator methods; `__slots__` declared on `PinId` and on the (already-slotted) `Pin`.

## 13. Out of scope (for follow-up work packages)

- **Pin numbers on passive terminals.** `Resistor.t1` / `t2`, `LED.anode` / `cathode` are conventionally pins 1 and 2; explicit `PinId`s would let exporters reference them by number. Defer until an exporter actually needs it.
- **VCC / GND pins on chips.** The existing chip models intentionally omit power pins. Adding them as `Pin(PinId(7, 'GND'), ...)` etc. is straightforward but is a separable refinement — adding them at the same time as the pin-number pass would conflate two changes.
- **Pin number assignments for SOIC, QFN, QFP, BGA package variants.** Today the models assume the DIP layout per chip. If the same logical part is used in a different package, its pin numbering changes — that's a per-package class (`SN74HC04SOIC` vs `SN74HC04DIP`) and a substantial library expansion.
- **Migrating `PinId` to pydantic.** If the sidecar-JSON / serialisation work package adopts pydantic project-wide, `PinId` migrates with it via a five-line swap to `pydantic.dataclasses.dataclass`. No work required now.
- **Netlist exporters.** SPICE, KiCad, EDIF emitters that consume `pin.number` are tracked separately.
