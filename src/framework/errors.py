"""Exception hierarchy for the wirebench framework.

Every framework-raised error inherits from `WirebenchError`.  The
hierarchy mirrors the real-world classes of mistakes a breadboarder
actually makes, so callers can `except WiringError` or
`except ForbiddenStateError` without scraping message text.

The three top-level families under `WirebenchError`:

    CircuitError   — something is wrong with the circuit you described
    FormatError    — something is wrong with saving / loading / rendering
    UsageError     — the framework's API was called incorrectly

Each concrete leaf multi-inherits from its family **and** the built-in
exception type it semantically replaces (`ValueError` or `TypeError`),
so existing `pytest.raises(ValueError, …)` checks keep working without
modification.  The family classes themselves inherit from `Exception`
only — they're abstract groupings.

Every class carries a `PHYSICAL_JUSTIFICATION` ClassVar — one or two
short sentences anchored to a physical-world referent that explain
*why this rule exists*.  The justification renders as a `Why:` line
after the base message whenever the exception is stringified, turning
the diagnostic from *"tells you what's wrong"* into *"teaches you why
the rule exists."*  When the framework knows which `wire()` call(s)
introduced the defect, those source locations render as an additional
`Wired at:` line.  Both additions are append-only — existing
`pytest.raises(..., match='...')` patterns continue to find the head of
the original message.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar


# ----------------------------------------------------------------- root

class WirebenchError(Exception):
    """Root of every framework-raised exception."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Real breadboards punish topology mistakes at runtime — overheated "
        "outputs, undefined logic levels, parts that won't seat. "
        "wirebench catches them at construction time instead."
    )

    def __init__(
        self,
        *args: Any,
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args)
        self._source_locations: tuple[tuple[str, int], ...] = (
            tuple(source_locations) if source_locations else ()
        )

    @property
    def source_locations(self) -> tuple[tuple[str, int], ...]:
        """File-and-line of each `wire()` call that contributed to the
        defect, in attachment order.  Empty when the framework couldn't
        attribute the error to a specific call site (e.g. errors raised
        outside the `wire()` path)."""
        return self._source_locations

    def suggested_remediation(self) -> str | None:
        """Return a high-confidence remediation hint, or `None` if the
        defect's resolution depends on design intent the framework
        can't infer.

        Subclasses override to provide per-defect-class suggestions.
        Default returns `None`, the *silent when confidence is low*
        posture: the framework names the defect and explains why
        without pretending to know which fix the designer intended.

        Remediation strings are *teaching-toned* — they explain what
        to do and offer the alternative when more than one fix is
        valid, rather than imperative "do X now."  They never suggest
        bypassing a framework check or silencing the validation.
        """
        return None

    def __str__(self) -> str:
        base = super().__str__()
        parts = [base]
        justification = type(self).PHYSICAL_JUSTIFICATION
        if justification:
            parts.append(f"  Why: {justification}")
        if self._source_locations:
            locs = ", ".join(
                f"{filename}:{lineno}"
                for filename, lineno in self._source_locations
            )
            parts.append(f"  Wired at: {locs}")
        remediation = self.suggested_remediation()
        if remediation:
            parts.append(f"  Try: {remediation}")
        return "\n".join(parts)


# ============================================================ Circuit ===
# Something is wrong with the circuit you described.

class CircuitError(WirebenchError):
    """Anything wrong with the circuit being modelled — its topology,
    its signals, its parts, its connectors, or its allowed states."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The circuit as described has a real-world defect: wires routed "
        "wrong, signals that can't share copper, parts in impossible "
        "configurations, or connectors that don't physically fit."
    )


# ----------------------------------------------------------- Wiring ---

class WiringError(CircuitError):
    """Topology / connectivity error.  The wires themselves are
    wrong — too many drivers, no drivers, the same node touched twice,
    a mandatory pin left floating."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Copper traces only carry one signal at one potential at a time; "
        "wiring defects break that physical assumption."
    )


class ShortCircuitError(WiringError, ValueError):
    """Multiple drivers on a single logical net — two outputs tied
    together, or an output and a rail tied to the same node."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two OUT-direction ports on one net fight each other on the "
        "copper — current sinks through the losing output stage until "
        "the FETs overheat; one driver per shared conductor."
    )

    def __init__(
        self,
        *args: Any,
        drivers: Sequence[str] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        self.drivers: tuple[str, ...] = tuple(drivers)

    def suggested_remediation(self) -> str | None:
        # High confidence only for the two-driver canonical case;
        # three-or-more shorts could be unintended fan-out, a missing
        # tri-state enable, or a deliberate wired-OR that should have
        # been built differently — no single fix dominates.
        if len(self.drivers) == 2:
            a, b = self.drivers
            return (
                f"Remove one of the two wire() calls connecting "
                f"{a} and {b}, OR insert a series element (resistor, "
                f"diode) between them to break the direct conflict."
            )
        return None


class FloatingNetError(WiringError, ValueError):
    """A net touched only by passive BIDIR ports with no driver
    anywhere.  Nothing can determine the net's value."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A net with no driver has no defined voltage — CMOS inputs in "
        "particular drift to mid-rail and oscillate, picking up nearby "
        "switching noise as if the trace were an antenna."
    )

    def __init__(
        self,
        *args: Any,
        kind: str = '',
        port_refs: Sequence[str] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # `kind`:
        #   'multi_bidir'  — net has only passive BIDIRs, validate-time
        #   'all_in'       — wire-time refusal when every port is IN
        # Suggestions diverge between the two: the multi-BIDIR case has
        # a high-confidence pair of fixes; the all-IN case typically
        # means the user forgot a driver entirely, which is design-
        # intent territory.
        self.kind: str = kind
        self.port_refs: tuple[str, ...] = tuple(port_refs)

    def suggested_remediation(self) -> str | None:
        if self.kind == 'multi_bidir':
            return (
                "Wire one port to a Rail (or to an OUT-direction port) so "
                "something defines the net's value, OR pass "
                "`dynamically_driven=True` to `wire()` if this is an "
                "analog feedback node driven through the surrounding "
                "loop (op-amp bias divider, RC timing network)."
            )
        return None


class UnconnectedPinError(WiringError, ValueError):
    """A pin declared `mandatory=True` was not connected to any wire
    inside the enclosing circuit."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A mandatory pin (regulator IN, op-amp V+, MCU VDD) left in air "
        "leaves the silicon stage tied to nothing — the part either "
        "doesn't power up or behaves unpredictably."
    )

    def __init__(
        self,
        *args: Any,
        port_refs: Sequence[str] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        self.port_refs: tuple[str, ...] = tuple(port_refs)

    def suggested_remediation(self) -> str | None:
        if len(self.port_refs) == 1:
            ref = self.port_refs[0]
            return (
                f"Wire {ref} to the supply or signal source it "
                f"requires — every mandatory pin must be driven inside "
                f"the enclosing circuit."
            )
        return None


class NodeMergeError(WiringError, ValueError):
    """`wire()` was asked to join ports already on two distinct
    existing nodes — the framework refuses to merge them."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two distinct existing nets fused at construction time would "
        "silently combine independent design intent; the framework "
        "requires the join to be made explicit."
    )


class EmptyWireError(WiringError, ValueError):
    """`wire()` was called with no ports (or with a single port —
    which couldn't connect anything to anything)."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A wire with no endpoints connects nothing to nothing — it has "
        "no physical analogue on a real breadboard."
    )


# ----------------------------------------------------------- Signal ---

class SignalError(CircuitError):
    """Signal-type / direction / ground-domain mismatch — the wires
    are joined, but the signals they carry don't fit together."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A piece of copper carries one kind of signal at one reference; "
        "mismatched signal-types or ground domains can't coexist on the "
        "same conductor without an isolator or level-shifter."
    )


class SignalTypeMismatchError(SignalError, TypeError):
    """An Analog signal landed on a Digital port, or vice versa."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "An Analog continuous voltage and a Digital logic-level on one "
        "net are incompatible — converting between them needs an "
        "explicit interface (comparator, ADC, level-shifter)."
    )

    def __init__(
        self,
        *args: Any,
        port_types: Sequence[tuple[str, str]] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # Pairs of (port_name, signal_type_class_name) — the framework
        # knows the participating types but not the designer's intent
        # for the interface; the suggestion lists the canonical
        # conversion elements without prescribing one.
        self.port_types: tuple[tuple[str, str], ...] = tuple(port_types)

    def suggested_remediation(self) -> str | None:
        if self.port_types:
            return (
                "Insert a comparator, ADC, or level-shifter between the "
                "Analog and Digital ports — they can't share copper "
                "directly because one carries a continuous voltage and "
                "the other a logic level."
            )
        return None


class DomainCrossingError(SignalError, ValueError):
    """A `wire()` or `Port↔Node` attachment crosses a `GroundDomain`
    boundary.  Only `IsolatedChannel`-style cells with ports in
    different domains may bridge."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two ground domains share a net only through an isolator "
        "(optocoupler, digital isolator, transformer); a direct wire "
        "would tie the references together and defeat the isolation."
    )

    def __init__(
        self,
        *args: Any,
        port_domains: Sequence[tuple[str, str]] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # Pairs of (port_name, domain_name) — at least two distinct
        # domains are present for the error to fire at all.
        self.port_domains: tuple[tuple[str, str], ...] = tuple(port_domains)

    def suggested_remediation(self) -> str | None:
        domains = {d for _, d in self.port_domains}
        if len(domains) >= 2:
            return (
                "Insert an isolator between the two ground domains — "
                "an Optocoupler for slow digital signals, an ADuM-class "
                "digital isolator for fast/SPI, or a transformer for "
                "AC power.  Direct wiring across domains would tie the "
                "references together and defeat the isolation."
            )
        return None


class PortContentionError(SignalError, ValueError):
    """A BIDIR pin's external and internal faces hold conflicting
    values during evaluation — two simultaneous drivers on the bond
    wire, one from outside the chip and one from inside."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A BIDIR pin is one piece of metal at one potential at a time — "
        "the external and internal faces can't simultaneously drive "
        "opposite values."
    )



# -------------------------------------------------- ForbiddenState ---

class ForbiddenStateError(CircuitError, ValueError):
    """The circuit is in a logical state the real silicon forbids:
    SR latch with S=R=1, three-phase Hall pattern (0,0,0) or (1,1,1),
    shoot-through on a half-bridge, CMOS latch-up.  These are valid
    *wirings* whose evaluation produces an undefined or destructive
    real-world result."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Some logical states real silicon refuses to enter — SR latch "
        "with S=R=1, half-bridge shoot-through, three-phase Hall "
        "(1,1,1); evaluation produces undefined or destructive output."
    )

    def __init__(
        self,
        *args: Any,
        state_signature: str = '',
        port_names: Sequence[str] = (),
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # `state_signature` identifies the canonical forbidden pattern
        # (e.g. 'sr_latch_both_active'); per-cell remediations key off
        # this so the suggestion can be specific without the base
        # class knowing every cell's forbidden taxonomy.
        self.state_signature: str = state_signature
        self.port_names: tuple[str, ...] = tuple(port_names)

    def suggested_remediation(self) -> str | None:
        if (self.state_signature == 'sr_latch_both_active'
                and len(self.port_names) == 2):
            s, r = self.port_names
            return (
                f"Drive {s} and {r} from mutually-exclusive sources "
                f"(e.g. invert one input from the other, or wire them "
                f"through a one-hot selector), OR use a different "
                f"latch type — a D-latch with enable, for instance, "
                f"has no forbidden state."
            )
        return None


# ------------------------------------------------------------ Part ---

class PartError(CircuitError):
    """Anything wrong with a part itself — its refdes, its parameters,
    its registration, its configuration."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A part on a real board has fixed properties — label, pinout, "
        "rated parameter ranges; a wirebench Part with broken "
        "properties describes something the parts catalogue can't sell."
    )


class RefdesError(PartError, ValueError):
    """Reference-designator format violation: unknown prefix,
    non-positive number, duplicate refdes in a circuit, duplicate
    surface-port name."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Every part on a real board needs one unique label so the "
        "schematic, the layout, the BOM, and the assembly drawing all "
        "refer to the same physical chip."
    )

    def __init__(
        self,
        *args: Any,
        kind: str = '',
        duplicate_refdes: str = '',
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # `kind` is one of '' (legacy / unknown), 'duplicate',
        # 'unknown_prefix', 'non_positive', 'duplicate_surface_port'.
        # Only the 'duplicate' case currently carries a high-confidence
        # fix; the others depend on which specific value the user
        # typed wrong.
        self.kind: str = kind
        self.duplicate_refdes: str = duplicate_refdes

    def suggested_remediation(self) -> str | None:
        if self.kind == 'duplicate' and self.duplicate_refdes:
            return (
                f"Change one part's `refdes_number=` argument so each "
                f"part in the circuit gets a unique {self.duplicate_refdes} "
                f"slot — the schematic, BOM, and assembly drawing all "
                f"key off the refdes."
            )
        return None


class DuplicateRegistrationError(PartError, ValueError):
    """The component registry rejected a `@register(name)` because
    another class is already registered under that name."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two classes claiming the same registered name would make "
        "`.wirebench` load ambiguous — the loader couldn't know which "
        "class to instantiate."
    )


class UnknownPartError(PartError, KeyError):
    """The component registry was asked for a class name that hasn't
    been registered — typically when a saved `.wirebench` file
    references a class whose module hasn't been imported."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The registry only knows classes whose module has been "
        "imported; a name with no entry refers to no part the "
        "framework can build."
    )


class PartConfigurationError(PartError, TypeError):
    """A component's constructor was passed bad arguments or the
    class is missing required class-level configuration
    (PIN_COUNT, PITCH_MM, PINOUT, distinct ground domains, etc.)."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A component's class-level configuration (pin count, pinout, "
        "ground domains) is what makes it that specific part; missing "
        "or inconsistent values describe nothing real."
    )


class PartParameterError(PartError, ValueError):
    """A component's constructor accepted the kwarg by signature but
    rejected the *value* — out-of-range state of charge, trip-high
    below trip-low, duplicate diode-OR input names, etc."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Physical parameters (state of charge, trip levels, voltage "
        "ratings) live within ranges set by the underlying physics; "
        "values outside the range describe a part that can't exist."
    )


# ---------------------------------------------------------- Mating ---

class MatingError(CircuitError):
    """A connector pair can't physically mate the way the caller
    requested — wrong family, wrong dimensions, no in-model partner
    declared."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two connectors mate only when their shells, pin counts, and "
        "pitches match the same mechanical drawing; mismatches don't "
        "physically seat together."
    )


class IncompatibleMateError(MatingError, TypeError):
    """The two connectors are from fundamentally different families
    (e.g. a USB-A receptacle and a TRRS audio jack).  The partner
    class doesn't match what `MATES_WITH` declared."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Two connector families don't fit together physically — USB-A "
        "and TRRS audio have different shells, pin counts, and "
        "pitches; calling them mated is asserting a fact contradicted "
        "by the mechanical drawings."
    )

    def __init__(
        self,
        *args: Any,
        actual_class: str = '',
        expected_class: str = '',
        partner_class: str = '',
        source_locations: Sequence[tuple[str, int]] | None = None,
    ) -> None:
        super().__init__(*args, source_locations=source_locations)
        # `actual_class`: the connector class the user passed as `b`.
        # `expected_class`: type(a).MATES_WITH (the class b should
        # have been).  `partner_class`: type(a), so the suggestion can
        # name both sides.  All three present → high-confidence
        # one-line fix.
        self.actual_class: str = actual_class
        self.expected_class: str = expected_class
        self.partner_class: str = partner_class

    def suggested_remediation(self) -> str | None:
        if self.actual_class and self.expected_class and self.partner_class:
            return (
                f"Use `{self.expected_class}` to mate with "
                f"`{self.partner_class}` — the declared partner class "
                f"is unique to that family.  If the design really "
                f"calls for a `{self.actual_class}`, change the "
                f"partner side too so the families match."
            )
        return None


class UnmateableError(MatingError, TypeError):
    """The connector has no in-model partner type declared
    (`MATES_WITH is None`) — typically a user-facing receptacle whose
    mating partner lives outside the design (a barrel jack, an audio
    plug, a USB cable end)."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Some user-facing receptacles (barrel jacks, audio sockets) "
        "mate with cables that live outside the design — there is no "
        "in-model partner to wire to."
    )


class PinCountMismatchError(MatingError, ValueError):
    """Two connectors of compatible families have different pin
    counts — a 4-pin plug into a 5-pin receptacle."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A 4-pin plug into a 5-pin receptacle leaves one pin unmated; "
        "the physical connection is incomplete."
    )


class PitchMismatchError(MatingError, ValueError):
    """Two connectors of compatible families have different pitches —
    a 2.54 mm plug into a 2.00 mm receptacle."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A 2.54 mm plug into a 2.00 mm receptacle won't seat — the "
        "pins land between contacts, not on them."
    )


# ============================================================= Format ===
# Something is wrong with saving / loading / rendering a circuit.

class FormatError(WirebenchError):
    """Anything wrong with the file format / persistence / rendering
    layer.  The circuit itself may be fine; the I/O around it isn't."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The serialised form of a design is the contract every "
        "downstream tool (SPICE, KiCad, schematic visualisers) reads; "
        "a broken format leaves no downstream tool able to consume it."
    )


class SaveError(FormatError, ValueError):
    """`save_wirebench` couldn't serialise the design — a component
    has no refdes and no synthesised id, a kwarg's type isn't
    encodable, etc."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A design's serialised form must round-trip back to an "
        "equivalent in-memory model; a save that loses information "
        "leaves the file unable to reconstruct what it describes."
    )


class LoadError(FormatError, ValueError):
    """`load_wirebench` couldn't reconstruct a design from its
    serialised form — malformed port reference, unknown component id,
    duplicate id, unknown class, missing required field."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A `.wirebench` file is a contract about which parts and wires "
        "the design contains; a file that can't be parsed into that "
        "contract isn't a wirebench design."
    )


class UnknownFormatError(FormatError, ValueError):
    """`export()` / `export_to_string()` was asked for a format name
    that doesn't correspond to a known adapter sub-package under
    `framework.export.`.  Typically a typo (`spcie` for `spice`)
    or a name the caller carried over from before the adapter was
    renamed."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Each export adapter (KiCad, SPICE, SVG) speaks a specific "
        "downstream tool's dialect; an unknown format name doesn't "
        "correspond to any real tool."
    )


class BreadboardIncompatibleError(FormatError, ValueError):
    """The `assembly_guide` export was asked to render a design that
    contains parts which can't be assembled on a standard 830-pin
    solderless breadboard — typically SMD chips, BGA packages, or
    SMD-only connectors (USB-C receptacles, microSD slots, etc.).

    Use a different export target (`kicad` for PCB layout) or rework
    the design with breadboard-friendly part variants (an ATmega328P
    DIP-28 instead of an ATmega2560 TQFP-100; a sensor breakout
    module instead of a bare BGA chip)."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Solderless breadboards accept only through-hole leads on "
        "0.1\" centres; SMD chips and BGA packages need a PCB to "
        "mount on."
    )


class RendererRegistryError(FormatError):
    """Anything wrong with the export-adapter renderer / net-namer
    registry.  Abstract; concrete subclasses pick the right built-in
    based on whether the operation was a duplicate registration
    (ValueError) or a missing lookup (KeyError)."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The export pipeline routes each component to a registered "
        "renderer; a broken registry leaves the pipeline with no way "
        "to translate the design into the downstream format."
    )


class DuplicateRendererError(RendererRegistryError, ValueError):
    """A renderer or net-namer is already registered for the
    requested (class, format) pair — the export adapter tried to
    register a second one."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Each (component class, export format) pair has one canonical "
        "renderer; two registered renderers would make the export "
        "order-dependent and non-deterministic."
    )


class RendererNotFoundError(RendererRegistryError, KeyError):
    """No renderer (or net-namer) is registered for the requested
    (class, format) pair — typically because the adapter module
    wasn't imported before `export_to_string` was called."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The export adapter registers renderers when its module is "
        "imported; a missing entry means the module wasn't loaded "
        "before export was attempted."
    )


# ============================================================== Usage ===
# The framework's API was called incorrectly.  The circuit is fine;
# the caller's interaction with the framework is the problem.

class UsageError(WirebenchError):
    """The framework's API was called incorrectly."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "The framework's API is the boundary between the designer's "
        "intent and the model; calling it incorrectly leaves the "
        "model unable to represent what the designer meant."
    )


class WiredChipCallError(UsageError, RuntimeError):
    """A chip's standalone `__call__` was invoked while one or more
    of its ports were wired by an enclosing circuit.  Drive via the
    parent's `evaluate()` instead."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A chip wired into an enclosing circuit must be driven by "
        "that circuit's `evaluate()`; calling its standalone "
        "`__call__` bypasses the wired ports and produces "
        "inconsistent output."
    )


class AmbiguousPinNameError(UsageError, KeyError):
    """`chip.ports['NAME']` was indexed by a name that resolves to
    more than one pin (typically because the chip has two VSS pads or
    similar).  Use the disambiguated name (`'VSS_1'`, `'VSS_2'`) or
    look up by pin number."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "Some chips have multiple pins sharing a common name (two VSS "
        "pads, paired power inputs); a bare lookup can't pick one — "
        "the disambiguated name (`VSS_1`, `VSS_2`) identifies the "
        "specific solder pad."
    )


class CompositeShapeError(UsageError, TypeError):
    """A composite `Circuit` subclass is missing the `__dict__` the
    auto-collect machinery needs (typically because it declared
    `__slots__`), or it constructed itself with an empty part
    list."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A Circuit composite needs parts and a way to find them — "
        "either auto-collection through `__dict__` or an explicit "
        "`parts=` list; an empty composite describes nothing real."
    )


class UnknownPortError(UsageError, ValueError):
    """An internal API was given a port that doesn't belong to the
    object it was passed to — e.g. `pin.other_face(stranger_port)`
    where `stranger_port` is not one of this pin's two faces."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "An internal API was handed a port that doesn't belong to the "
        "object it was passed to — the port reference is dangling and "
        "names nothing on the recipient."
    )


class OrphanWireError(UsageError, ValueError):
    """A wire crosses the boundary of the enclosing circuit — joining
    one of the circuit's `parts` to a component that wasn't
    included.  The orphan is either a local variable (auto-collect
    couldn't see it because it wasn't stored as `self.<name>`) or an
    explicit `parts=[...]` list that omitted it.  The
    framework can validate or evaluate the orphan's contribution to
    the circuit, so it refuses to build the composite."""

    PHYSICAL_JUSTIFICATION: ClassVar[str] = (
        "A wire whose endpoint isn't in the composite's `parts` list "
        "joins a phantom — a component the framework can't validate, "
        "evaluate, or serialise."
    )
