# Board + Connector — Implementation Spec

## 1. Purpose

Add the physical concepts of **printed circuit boards** and **connectors** to the framework. A `Board` is a populated PCB — it has identity (name, revision), it carries components, and it can itself be a part within a stacked assembly. A `Connector` is the class of components whose contacts face outward off the board edge; mating two connectors physically joins two boards into a stacked assembly (the "HAT" pattern — Raspberry Pi shield, Arduino daughterboard, Eurorack module, etc.).

After this work package, the codebase can describe multi-board systems where boards mate via real, named connector parts, and the model preserves the per-board refdes scoping that real silkscreens have.

## 2. Scope

**In scope** — a `Board` class, a `Connector` abstract class, an initial set of concrete connector parts (the Raspberry Pi 40-pin GPIO pair as the canonical HAT case), a `mate()` function, BIDIR-pin support in the existing `Pin` primitive (a small generalisation needed by connectors), and a two-board demo that splits the existing `WaterAlarm` design across a sensor board and a controller board.

**Out of scope** — board mechanical/outline modelling (mounting holes, dimensions, board outline); pin numbering metadata for chips (separate work package — needed for SPICE/KiCad export but orthogonal to boards); cross-domain isolation (mating two boards on different `GroundDomain`s); cross-over / null-modem mating where pin order is permuted; sidecar JSON persistence of refdes; auto-annotation of refdes numbers; netlist exporters; the full library of real connector parts beyond the initial set in §7.

**Prerequisites** — the REFDES Instance Attributes work package (`docs/refdes-spec.md`) must be implemented first. This spec assumes `validate_refdes()`, `IEEE_315_PREFIXES`, `REFDES_PREFIX` class attributes, and the `refdes_number` constructor convention all exist. Refdes is the simple `<prefix><integer>` form throughout — section letters (`U3A`, `U3B`) are an exporter-side concern, not part of the model.

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

    __slots__ = ('_pins', '_refdes_number', '_pin_count', '_pitch_mm')

    REFDES_PREFIX:  ClassVar[str]                  # 'J' (female) or 'P' (male)
    GENDER:         ClassVar[str]                  # 'female' | 'male'
    MATES_WITH:     ClassVar[type['Connector'] | None] = None
                                                   # set via declare_mating_pair if the
                                                   # part has a board-to-board mate; left
                                                   # None for user-facing receptacles
                                                   # (USB, audio, microSD …) that have
                                                   # no in-model partner.

    # Subclasses set ONE of:
    #   - PIN_COUNT (ClassVar) and PITCH_MM (ClassVar) — fixed-geometry parts
    #     like USB-C or a JST-PH 4-pin housing.
    #   - Neither — the constructor must then receive pin_count and pitch_mm
    #     for parameterised families like 0.1" snap-apart headers.
    PIN_COUNT:      ClassVar[int]    | None = None
    PITCH_MM:       ClassVar[float]  | None = None

    # Subclasses provide a pinout in ONE of two ways:
    #   - PINOUT class attribute: a tuple of (name, direction, signal_type)
    #     for fixed-geometry parts where every contact has a known role
    #     (e.g. USB-A: VBUS / D- / D+ / GND).
    #   - Override `_build_pinout()` to synthesise it from pin_count
    #     (parameterised families: every contact is a generic BIDIR Analog
    #     wire labelled `p1`…`pN`).
    PINOUT:         ClassVar[tuple[tuple[str, Direction, type], ...] | None] = None

    def __init__(
        self,
        *,
        domain: GroundDomain = ELECTRICAL,
        refdes_number: int,
        pin_count: int | None = None,
        pitch_mm: float | None = None,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number

        # Resolve pin_count and pitch_mm: explicit constructor argument
        # wins; otherwise inherit from the class attribute. At least one
        # source must supply each, or the part is under-specified.
        self._pin_count = pin_count if pin_count is not None else self.PIN_COUNT
        self._pitch_mm  = pitch_mm  if pitch_mm  is not None else self.PITCH_MM
        if self._pin_count is None:
            raise TypeError(
                f"{type(self).__name__} requires pin_count "
                f"(neither constructor arg nor PIN_COUNT class attribute set)"
            )
        if self._pitch_mm is None:
            raise TypeError(
                f"{type(self).__name__} requires pitch_mm "
                f"(neither constructor arg nor PITCH_MM class attribute set)"
            )

        self._pins = tuple(
            Pin(name, direction, domain, mandatory=False, signal_type=sigtype)
            for name, direction, sigtype in self._build_pinout()
        )

    def _build_pinout(self) -> tuple[tuple[str, Direction, type], ...]:
        """Return ((name, direction, signal_type), …) for every contact.

        Default implementation reads the PINOUT class attribute (fixed-
        geometry parts). Parameterised families override to synthesise
        a generic BIDIR Analog pinout from pin_count.
        """
        if self.PINOUT is None:
            raise TypeError(
                f"{type(self).__name__} must either set PINOUT "
                f"or override _build_pinout()"
            )
        return self.PINOUT

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
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def pin_count(self) -> int:
        return self._pin_count

    @property
    def pitch_mm(self) -> float:
        return self._pitch_mm

    def evaluate(self) -> None:
        for pin in self._pins:
            pin.evaluate()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(refdes={self.refdes!r}, "
            f"pin_count={self._pin_count}, pitch_mm={self._pitch_mm})"
        )
```

Notes for the implementer:

- `Connector` is abstract by convention only (no `@abstractmethod`); the missing `ClassVar`s on the base will make any direct instantiation error out at attribute access. That's good enough — declaring `__init_subclass__` to enforce ClassVar presence is optional.

## 7. Day-1 concrete connector library

The day-1 library covers the connectors found ubiquitously in modern consumer, hobbyist, and embedded electronics. It is grouped into modules by family. Each module declares one or two classes (board-side and, where applicable, the mating cable/board-side partner) and ends with a `declare_mating_pair()` call when both halves are present.

A handful of categories — user-facing receptacles such as USB, audio jacks, microSD slots, HDMI, RJ45, DC barrel jacks — have no in-model mating partner because the other end is a physical cable / card / plug whose modelling adds nothing to the circuit graph. Their `MATES_WITH` is left as `None`; their external pins simply become board surface ports awaiting external traffic. Plug-side classes for these can be added as follow-up if a multi-board design needs to model the cable end explicitly.

`src/components/connectors/__init__.py` re-exports every public class for convenience.

### 7.1 Generic snap-apart pin headers (`headers.py`)

Single-row and dual-row 0.1" / 0.05" headers — the workhorse of breadboards, jumpers, mezzanine connections, dev boards, and anything Arduino-style. Pin count and pitch are constructor parameters because these are field-cut from strips:

```python
class Header1xNMale(Connector):
    """1×N pin header strip, snap-apart. Common pitches: 2.54 mm (0.1"),
    1.27 mm (0.05" — JTAG/SWD)."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'

    def _build_pinout(self):
        return tuple((f'p{i}', Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

class Header1xNFemale(Connector):
    """1×N socket header strip — female counterpart to Header1xNMale."""
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'

    def _build_pinout(self):
        return tuple((f'p{i}', Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

class Header2xNMale(Connector):
    """2×N dual-row pin header strip. `pin_count` here is the *total* pin
    count (= 2 × pins_per_row), matching how these are sold and labelled."""
    __slots__ = ()
    REFDES_PREFIX = 'P'
    GENDER        = 'male'

    def _build_pinout(self):
        return tuple((f'p{i}', Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

class Header2xNFemale(Connector):
    __slots__ = ()
    REFDES_PREFIX = 'J'
    GENDER        = 'female'

    def _build_pinout(self):
        return tuple((f'p{i}', Direction.BIDIR, Analog)
                     for i in range(1, self._pin_count + 1))

declare_mating_pair(Header1xNMale, Header1xNFemale)
declare_mating_pair(Header2xNMale, Header2xNFemale)
```

Use the constructor: `Header2xNMale(pin_count=40, pitch_mm=2.54, refdes_number=1)` for a Raspberry Pi 40-pin GPIO header; `Header2xNMale(pin_count=10, pitch_mm=1.27, refdes_number=1)` for a 2×5 SWD header.

### 7.2 IDC ribbon headers (`idc.py`)

Boxed / shrouded dual-row male headers for ribbon-cable connections (programming headers, internal computer cabling, modular synth power, custom panel-to-board ribbons):

- `IDC2xNMale(pin_count, pitch_mm=2.54)` — board-side shrouded header.
- `IDC2xNSocket(pin_count, pitch_mm=2.54)` — cable-side female IDC socket.

Mating pair declared symmetrically.

### 7.3 USB (`usb.py`)

Receptacles only on day 1; cable-side plug classes are a follow-up. Each receptacle has a fixed `PIN_COUNT` and `PITCH_MM` and a fixed PINOUT with named functional roles:

- `USBAReceptacle` — 4-pin (VBUS, D-, D+, GND); pitch nominally 2.5 mm internal contact spacing.
- `USBBReceptacle` — 4-pin printer-style square housing.
- `USBMicroBReceptacle` — 5-pin (VBUS, D-, D+, ID, GND).
- `USBCReceptacle` — 24-pin, full pinout (VBUS×4, GND×4, CC1, CC2, D+×2, D-×2, SBU1, SBU2, SuperSpeed TX/RX×2 each). Most board designs leave many pins unwired; the connector still exposes them all.

`MATES_WITH = None` on all four — the cable on the other end is the mating partner, and we don't currently model cables.

### 7.4 Network and video (`network.py`, `video.py`)

- `RJ45Jack` — 8-pin 8P8C Ethernet jack (`network.py`). PINOUT names follow T568B convention (`pair_1_white_orange`, `pair_1_orange`, `pair_2_white_green`, `pair_3_blue`, …); board designs usually only wire the four active pairs.
- `HDMITypeAReceptacle` — 19-pin full-size HDMI receptacle (`video.py`). PINOUT names follow the HDMI standard: TMDS data 0/1/2 (clock, shield, +, −), CEC, DDC clock/data, HEC, +5 V, GND, hot plug detect.

Both have `MATES_WITH = None`.

### 7.5 Audio (`audio.py`)

- `Audio3p5mmTRSJack` — 3-contact 3.5 mm stereo jack (tip = left, ring = right, sleeve = GND).
- `Audio3p5mmTRRSJack` — 4-contact 3.5 mm jack (tip = left, ring1 = right, ring2/sleeve = GND/MIC depending on CTIA vs OMTP wiring; document both options in the docstring).

Both have `MATES_WITH = None`.

### 7.6 DC power (`barrel.py`)

- `BarrelJack5p5x2p1` — 5.5 mm OD × 2.1 mm ID centre-positive DC jack. 3 contacts: `tip` (positive), `sleeve` (GND), `switch` (the disconnect contact tied to `sleeve` until a plug is inserted; useful for "external power present" detection).
- `BarrelJack5p5x2p5` — 5.5 mm OD × 2.5 mm ID. Same pinout, mechanically incompatible plug.

Both have `MATES_WITH = None`.

### 7.7 JST families (`jst_ph.py`, `jst_xh.py`, `jst_sh.py`, `jst_gh.py`)

Wire-to-board housings, ubiquitous in batteries (LiPo, 18650 packs), sensor breakouts, and modern small-format electronics. Each family has its own pitch (a class attribute on the module); pin count is a constructor parameter:

- `jst_ph.py` — 2.0 mm pitch JST PH series.
  - `JSTPHBoardSide(pin_count, refdes_number)` — male B*B-PH-K-S board header.
  - `JSTPHCableHousing(pin_count, refdes_number)` — female PHR-* crimp housing on the cable.
  - `declare_mating_pair(JSTPHBoardSide, JSTPHCableHousing)`.
- `jst_xh.py` — 2.5 mm pitch JST XH series. Common in LiPo balance leads (2-pin to 7-pin).
  - `JSTXHBoardSide`, `JSTXHCableHousing`, declared as a mating pair.
- `jst_sh.py` — 1.0 mm pitch JST SH series. Drone GPS, small modules.
  - `JSTSHBoardSide`, `JSTSHCableHousing`, declared as a mating pair.
- `jst_gh.py` — 1.25 mm pitch JST GH series. Drone flight controllers.
  - `JSTGHBoardSide`, `JSTGHCableHousing`, declared as a mating pair.

Each board-side class sets `PITCH_MM` as a class attribute (so the constructor doesn't need it); `pin_count` is supplied at construction. The pinout is generic BIDIR/Analog, synthesised via `_build_pinout()`.

### 7.8 Screw terminal blocks (`screw_terminal.py`)

- `ScrewTerminalBlock(pin_count, pitch_mm=5.08, refdes_number)` — fixed (non-pluggable) PCB-mount screw terminal. Common pitches in the docstring: 5.08 mm (industrial), 3.5 mm (compact), 2.54 mm (signal-level). `MATES_WITH = None` (the wire side isn't a connector).

### 7.9 Storage card slots (`sd.py`)

- `MicroSDCardSlot` — 8-contact microSD slot. PINOUT names: `dat2`, `dat3`, `cmd`, `vdd`, `clk`, `vss`, `dat0`, `dat1`.
- `SDCardSlot` — 9-contact full-size SD slot. Same SD-bus pin names plus the extra `cd` (card-detect) contact.

Both have `MATES_WITH = None` (the card isn't modelled as a connector).

### 7.10 Naming and packaging convention

Each connector family lives in its own module under `src/components/connectors/`. Module name = lowercase family identifier (`headers.py`, `usb.py`, `jst_ph.py`, `audio.py`, …). Class names follow PascalCase with the part identifier; gendered pairs both live in the same module and call `declare_mating_pair()` at module bottom.

Per CLAUDE.md, naming follows hardware terminology — `Header2xNMale` and `JSTPHBoardSide`, not `Generic40Pin` or `Connector[40]`. Pitch and pin count are physical data on the instance: a class attribute when fixed by the part's molded geometry (USB-C is always 24 pins at fixed pitch); a constructor argument when the part is field-configurable (snap-apart 0.1" headers, JST housings of variable pin count).

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
        '_refdes_number',
    )

    def __init__(
        self,
        *,
        name: str,
        revision: str,
        components: list[FactorNode],
        refdes_number: int,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        if not isinstance(name, str) or not name:
            raise ValueError("Board name must be a non-empty string")
        if not isinstance(revision, str) or not revision:
            raise ValueError("Board revision must be a non-empty string")

        self._name          = name
        self._revision      = revision
        self._refdes_number = refdes_number
        self._connectors    = tuple(c for c in components if isinstance(c, Connector))

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
        return f"{self.REFDES_PREFIX}{self._refdes_number}"
    @property
    def refdes_number(self) -> int:  return self._refdes_number

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

    Validates three layers of compatibility:
      1. Class-level — `b` is exactly `type(a).MATES_WITH` (the parts are
         physical mates of each other, not unrelated families).
      2. Instance-level — `pin_count` and `pitch_mm` agree (a 6-pin
         JST PH cannot mate with a 5-pin JST PH; a 0.05" header cannot
         mate with a 0.1" header even if both have the same pin count).
      3. Per-pin — delegated to wire(): same ground domain, same
         signal type, no driver conflicts.

    Raises:
        TypeError  — class-level mismatch or `MATES_WITH` is None (a
                     user-facing receptacle has no in-model mate).
        ValueError — instance-level mismatch (pin count, pitch) or any
                     wire()-level error per pin pair.
    """
    if type(a).MATES_WITH is None:
        raise TypeError(
            f"{type(a).__name__} has no in-model mate "
            f"(MATES_WITH is None — user-facing receptacle)"
        )
    if type(b) is not type(a).MATES_WITH:
        raise TypeError(
            f"{type(a).__name__} mates with {type(a).MATES_WITH.__name__}, "
            f"not {type(b).__name__}"
        )
    if a.pin_count != b.pin_count:
        raise ValueError(
            f"Pin count mismatch: {type(a).__name__} has {a.pin_count}, "
            f"{type(b).__name__} has {b.pin_count}"
        )
    if a.pitch_mm != b.pitch_mm:
        raise ValueError(
            f"Pitch mismatch: {type(a).__name__} is {a.pitch_mm} mm, "
            f"{type(b).__name__} is {b.pitch_mm} mm"
        )
    # len(a.pins) == a.pin_count by construction; the redundancy guard is
    # there only to catch a subclass that overrode _build_pinout incorrectly.
    if len(a.pins) != len(b.pins):
        raise ValueError(
            f"Pin count mismatch after pinout construction: "
            f"{type(a).__name__} produced {len(a.pins)}, "
            f"{type(b).__name__} produced {len(b.pins)}"
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
- `src/components/connectors/__init__.py` — re-exports every public class from the modules below.
- `src/components/connectors/headers.py` — `Header1xNMale` / `Header1xNFemale` / `Header2xNMale` / `Header2xNFemale` and the two mating-pair declarations (§7.1).
- `src/components/connectors/idc.py` — `IDC2xNMale` / `IDC2xNSocket` and mating-pair declaration (§7.2).
- `src/components/connectors/usb.py` — `USBAReceptacle`, `USBBReceptacle`, `USBMicroBReceptacle`, `USBCReceptacle` (§7.3).
- `src/components/connectors/network.py` — `RJ45Jack` (§7.4).
- `src/components/connectors/video.py` — `HDMITypeAReceptacle` (§7.4).
- `src/components/connectors/audio.py` — `Audio3p5mmTRSJack`, `Audio3p5mmTRRSJack` (§7.5).
- `src/components/connectors/barrel.py` — `BarrelJack5p5x2p1`, `BarrelJack5p5x2p5` (§7.6).
- `src/components/connectors/jst_ph.py` — `JSTPHBoardSide`, `JSTPHCableHousing`, mating-pair declaration (§7.7).
- `src/components/connectors/jst_xh.py` — `JSTXHBoardSide`, `JSTXHCableHousing`, mating-pair declaration (§7.7).
- `src/components/connectors/jst_sh.py` — `JSTSHBoardSide`, `JSTSHCableHousing`, mating-pair declaration (§7.7).
- `src/components/connectors/jst_gh.py` — `JSTGHBoardSide`, `JSTGHCableHousing`, mating-pair declaration (§7.7).
- `src/components/connectors/screw_terminal.py` — `ScrewTerminalBlock` (§7.8).
- `src/components/connectors/sd.py` — `MicroSDCardSlot`, `SDCardSlot` (§7.9).

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
- `Header2xNFemale(pin_count=40, pitch_mm=2.54)` (refdes `J1`) — only 6 of the 40 pins are used; the rest are unconnected.
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
- `Header2xNMale(pin_count=40, pitch_mm=2.54)` (refdes `P1`) — same 6 pins of interest as the sensor board, plus internal wiring through the SN74HC04 to the CD4043 latch and out to the LEDs.

**`WaterAlarmAssembly`** is a `Circuit` (not a `Board` — it's a stacked assembly, not a PCB) that holds:

- `SensorBoard(refdes_number=1)` → `A1`
- `ControllerBoard(refdes_number=2)` → `A2`
- A single `mate(sensor.connectors[0], controller.connectors[0])` call

and exposes the surface ports of `A1` for sensor drive (`A1.J1.p3`, `A1.J1.p4`) and observes the controller's LED state via component handles.

The demo is the test surface for the work package: it must produce identical end-to-end behaviour to the existing single-circuit `WaterAlarm` for the same probe-input sequences.

## 13. Test plan

New test module `tests/framework/test_board.py`:

1. **Empty board.** `Board(name='X', revision='A', components=[], refdes_number=1).refdes == 'A1'`. Surface ports dict is empty.
2. **Board with a connector exposes its externals.** Construct a board with one `Header2xNFemale(pin_count=40, pitch_mm=2.54, refdes_number=1)`. Assert `'J1.p1'` … `'J1.p40'` are in the board's `ports`.
3. **Multiple connectors on one board, no port name collision.** Construct a board with two female headers at `refdes_number=1` and `refdes_number=2`. Assert ports include both `'J1.p1'` and `'J2.p1'`.
4. **Two connectors with the same refdes is rejected.** Construct a board with two headers both `refdes_number=1`. Refdes-spec's `Circuit._validate` raises duplicate-refdes; verify the exception message names both.
5. **Board has refdes prefix `A`.** `Board(...).REFDES_PREFIX == 'A'`. `Board(refdes_number=3).refdes == 'A3'`.
6. **Board name and revision are required strings.** Empty / non-string values raise `ValueError`.
7. **Board name and revision are read-only.** No setter exists; assignment raises `AttributeError` on a property.

New test module `tests/framework/test_connector.py`:

8. **`Connector` is abstract by convention.** Direct instantiation of `Connector(refdes_number=1)` fails (missing `REFDES_PREFIX` and either `PINOUT` or an override of `_build_pinout()`).
9. **A fixed-geometry connector exposes its pins.** `USBCReceptacle(refdes_number=1).pins` is length 24; pin names match the named PINOUT.
10. **A parameterised connector synthesises its pinout.** `Header2xNFemale(pin_count=10, pitch_mm=2.54, refdes_number=1).pins` is length 10; names are `p1`..`p10`. Same class with `pin_count=40` produces `p1`..`p40`.
11. **External vs. all ports.** `external_ports` length == pin_count; `ports` length == 2 × pin_count (external + internal per pin).
12. **Refdes prefix is `J` for female, `P` for male.** Per the IEEE 315 convention. Verify on a representative sample (`Header2xNFemale`, `Header2xNMale`, `JSTPHBoardSide`, `JSTPHCableHousing`).
13. **Under-specified part rejects construction.** Calling `Header1xNMale(refdes_number=1)` (no `pin_count`, no class default) raises `TypeError`. Similarly omitting `pitch_mm`.
14. **BIDIR pin support.** `Pin('x', Direction.BIDIR, ELECTRICAL, signal_type=Digital)` constructs without error. Drive external → internal sees the value; drive internal → external sees the value; drive both with same value → no-op; drive both with different values → `ValueError("contention")`.
15. **User-facing receptacle has no mate.** `USBCReceptacle.MATES_WITH is None`; calling `mate(usb_c, anything)` raises `TypeError` mentioning the user-facing-receptacle constraint.
16. **Smoke test the whole library.** Iterate every public class re-exported from `components.connectors.__init__`; instantiate each with a representative `pin_count` (where required) and `refdes_number=1`; assert it produces a non-empty `external_ports` dict and a non-empty `pins` tuple. This catches forgotten ClassVars or missing `_build_pinout()` overrides without per-class boilerplate tests.

New test module `tests/framework/test_mate.py`:

17. **Successful mate.** `mate(female, male)` wires every external pin pair. After mating, driving `female.pins[0].external` results in `male.pins[0].external` reading the same value (after `evaluate()`).
18. **Class-level mismatch raises.** `mate(jst_ph_board, jst_xh_cable)` raises `TypeError` mentioning `MATES_WITH`.
19. **Pin-count mismatch raises.** `mate(JSTPHBoardSide(pin_count=4, ...), JSTPHCableHousing(pin_count=5, ...))` raises `ValueError` mentioning the counts.
20. **Pitch mismatch raises.** `mate(Header2xNMale(pin_count=10, pitch_mm=2.54, ...), Header2xNFemale(pin_count=10, pitch_mm=1.27, ...))` raises `ValueError` mentioning the pitches.
21. **Ground domain mismatch raises.** Construct two female headers in different domains, attempt to mate. Raises `ValueError` (delegated to `wire()`).
22. **A connector cannot be mated twice.** `mate(a, b); mate(a, c)` — second call raises (per `wire()`'s "would merge two existing nodes" guard).
23. **`declare_mating_pair` symmetry.** After declaration, `A.MATES_WITH is B and B.MATES_WITH is A`.

New test module `tests/applications/test_water_alarm_split.py`:

24. **End-to-end equivalence.** For the same sequence of `(low_probe, high_probe)` inputs, the split assembly's red/green LED states and the latch `q_1` value match the single-circuit `WaterAlarm`. Run a representative truth-table-ish exercise: `(0,0) → idle`, `(1,0) → set alarm`, `(1,1) → clear alarm`, `(0,1)` (impossible physically — high probe wet, low dry — verify the model behaves consistently, even if the result is implementation-defined).
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
