"""Exception hierarchy for the circuitry framework.

Every framework-raised error inherits from `CircuitryError`.  The
hierarchy mirrors the real-world classes of mistakes a breadboarder
actually makes, so callers can `except WiringError` or
`except ForbiddenStateError` without scraping message text.

The three top-level families under `CircuitryError`:

    CircuitError   — something is wrong with the circuit you described
    FormatError    — something is wrong with saving / loading / rendering
    UsageError     — the framework's API was called incorrectly

Each concrete leaf multi-inherits from its family **and** the built-in
exception type it semantically replaces (`ValueError` or `TypeError`),
so existing `pytest.raises(ValueError, …)` checks keep working without
modification.  The family classes themselves inherit from `Exception`
only — they're abstract groupings.
"""
from __future__ import annotations


# ----------------------------------------------------------------- root

class CircuitryError(Exception):
    """Root of every framework-raised exception."""


# ============================================================ Circuit ===
# Something is wrong with the circuit you described.

class CircuitError(CircuitryError):
    """Anything wrong with the circuit being modelled — its topology,
    its signals, its parts, its connectors, or its allowed states."""


# ----------------------------------------------------------- Wiring ---

class WiringError(CircuitError):
    """Topology / connectivity error.  The wires themselves are
    wrong — too many drivers, no drivers, the same node touched twice,
    a mandatory pin left floating."""


class ShortCircuitError(WiringError, ValueError):
    """Multiple drivers on a single logical net — two outputs tied
    together, or an output and a rail tied to the same node."""


class FloatingNetError(WiringError, ValueError):
    """A net touched only by passive BIDIR ports with no driver
    anywhere.  Nothing can determine the net's value."""


class UnconnectedPinError(WiringError, ValueError):
    """A pin declared `mandatory=True` was not connected to any wire
    inside the enclosing circuit."""


class NodeMergeError(WiringError, ValueError):
    """`wire()` was asked to join ports already on two distinct
    existing nodes — the framework refuses to merge them."""


class EmptyWireError(WiringError, ValueError):
    """`wire()` was called with no ports (or with a single port —
    which couldn't connect anything to anything)."""


# ----------------------------------------------------------- Signal ---

class SignalError(CircuitError):
    """Signal-type / direction / ground-domain mismatch — the wires
    are joined, but the signals they carry don't fit together."""


class SignalTypeMismatchError(SignalError, TypeError):
    """An Analog signal landed on a Digital port, or vice versa."""


class DomainCrossingError(SignalError, ValueError):
    """A `wire()` or `Port↔Node` attachment crosses a `GroundDomain`
    boundary.  Only `IsolatedChannel`-style cells with ports in
    different domains may bridge."""


class PortContentionError(SignalError, ValueError):
    """A BIDIR pin's external and internal faces hold conflicting
    values during evaluation — two simultaneous drivers on the bond
    wire, one from outside the chip and one from inside."""


# --------------------------------------------------- Polarity ---

class PolarityError(CircuitError, ValueError):
    """A polarised component has its terminals reversed: electrolytic
    capacitor with + and − swapped, LED with anode and cathode
    swapped, rectifier diode pointing the wrong way, battery or cell
    inserted backwards.

    No current raise site detects this — the framework's voltage-only
    graph can't solve steady-state currents, and the wire list alone
    can't tell whether `led.anode` is intended to land on the supply
    rail or the ground rail.  The class exists so a future polarity-
    detection pass (or a component-level evaluate-time check, e.g.
    a `Cell` whose `pos` and `neg` voltages contradict its declared
    state of charge) has the right place to land.
    """


# -------------------------------------------------- ForbiddenState ---

class ForbiddenStateError(CircuitError, ValueError):
    """The circuit is in a logical state the real silicon forbids:
    SR latch with S=R=1, three-phase Hall pattern (0,0,0) or (1,1,1),
    shoot-through on a half-bridge, CMOS latch-up.  These are valid
    *wirings* whose evaluation produces an undefined or destructive
    real-world result."""


# ------------------------------------------------------------ Part ---

class PartError(CircuitError):
    """Anything wrong with a part itself — its refdes, its parameters,
    its registration, its configuration."""


class RefdesError(PartError, ValueError):
    """Reference-designator format violation: unknown prefix,
    non-positive number, duplicate refdes in a circuit, duplicate
    surface-port name."""


class DuplicateRegistrationError(PartError, ValueError):
    """The component registry rejected a `@register(name)` because
    another class is already registered under that name."""


class UnknownPartError(PartError, KeyError):
    """The component registry was asked for a class name that hasn't
    been registered — typically when a saved `.circuitry` file
    references a class whose module hasn't been imported."""


class PartConfigurationError(PartError, TypeError):
    """A component's constructor was passed bad arguments or the
    class is missing required class-level configuration
    (PIN_COUNT, PITCH_MM, PINOUT, distinct ground domains, etc.)."""


class PartParameterError(PartError, ValueError):
    """A component's constructor accepted the kwarg by signature but
    rejected the *value* — out-of-range state of charge, trip-high
    below trip-low, duplicate diode-OR input names, etc."""


# ---------------------------------------------------------- Mating ---

class MatingError(CircuitError):
    """A connector pair can't physically mate the way the caller
    requested — wrong family, wrong dimensions, no in-model partner
    declared."""


class IncompatibleMateError(MatingError, TypeError):
    """The two connectors are from fundamentally different families
    (e.g. a USB-A receptacle and a TRRS audio jack).  The partner
    class doesn't match what `MATES_WITH` declared."""


class UnmateableError(MatingError, TypeError):
    """The connector has no in-model partner type declared
    (`MATES_WITH is None`) — typically a user-facing receptacle whose
    mating partner lives outside the design (a barrel jack, an audio
    plug, a USB cable end)."""


class PinCountMismatchError(MatingError, ValueError):
    """Two connectors of compatible families have different pin
    counts — a 4-pin plug into a 5-pin receptacle."""


class PitchMismatchError(MatingError, ValueError):
    """Two connectors of compatible families have different pitches —
    a 2.54 mm plug into a 2.00 mm receptacle."""


# ============================================================= Format ===
# Something is wrong with saving / loading / rendering a circuit.

class FormatError(CircuitryError):
    """Anything wrong with the file format / persistence / rendering
    layer.  The circuit itself may be fine; the I/O around it isn't."""


class SaveError(FormatError, ValueError):
    """`save_circuitry` couldn't serialise the design — a component
    has no refdes and no synthesised id, a kwarg's type isn't
    encodable, etc."""


class LoadError(FormatError, ValueError):
    """`load_circuitry` couldn't reconstruct a design from its
    serialised form — malformed port reference, unknown component id,
    duplicate id, unknown class, missing required field."""


class UnknownFormatError(FormatError, ValueError):
    """`export()` / `export_to_string()` was asked for a format name
    that doesn't correspond to a known adapter sub-package under
    `framework.export.`.  Typically a typo (`spcie` for `spice`)
    or a name the caller carried over from before the adapter was
    renamed."""


class RendererRegistryError(FormatError):
    """Anything wrong with the export-adapter renderer / net-namer
    registry.  Abstract; concrete subclasses pick the right built-in
    based on whether the operation was a duplicate registration
    (ValueError) or a missing lookup (KeyError)."""


class DuplicateRendererError(RendererRegistryError, ValueError):
    """A renderer or net-namer is already registered for the
    requested (class, format) pair — the export adapter tried to
    register a second one."""


class RendererNotFoundError(RendererRegistryError, KeyError):
    """No renderer (or net-namer) is registered for the requested
    (class, format) pair — typically because the adapter module
    wasn't imported before `export_to_string` was called."""


# ============================================================== Usage ===
# The framework's API was called incorrectly.  The circuit is fine;
# the caller's interaction with the framework is the problem.

class UsageError(CircuitryError):
    """The framework's API was called incorrectly."""


class WiredChipCallError(UsageError, RuntimeError):
    """A chip's standalone `__call__` was invoked while one or more
    of its ports were wired by an enclosing circuit.  Drive via the
    parent's `evaluate()` instead."""


class AmbiguousPinNameError(UsageError, KeyError):
    """`chip.ports['NAME']` was indexed by a name that resolves to
    more than one pin (typically because the chip has two VSS pads or
    similar).  Use the disambiguated name (`'VSS_1'`, `'VSS_2'`) or
    look up by pin number."""


class CompositeShapeError(UsageError, TypeError):
    """A composite `Circuit` subclass is missing the `__dict__` the
    auto-collect machinery needs (typically because it declared
    `__slots__`), or it constructed itself with an empty factor-node
    list."""


class UnknownPortError(UsageError, ValueError):
    """An internal API was given a port that doesn't belong to the
    object it was passed to — e.g. `pin.other_face(stranger_port)`
    where `stranger_port` is not one of this pin's two faces."""


class OrphanWireError(UsageError, ValueError):
    """A wire crosses the boundary of the enclosing circuit — joining
    one of the circuit's `factor_nodes` to a component that wasn't
    included.  The orphan is either a local variable (auto-collect
    couldn't see it because it wasn't stored as `self.<name>`) or an
    explicit `factor_nodes=[...]` list that omitted it.  The
    framework can validate or evaluate the orphan's contribution to
    the circuit, so it refuses to build the composite."""
