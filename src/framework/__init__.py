"""wirebench framework — the engine that models real circuits.

This module is the framework's curated public surface.  Component
libraries (`src/components/`) and demos (`demos/`) should reach into
the framework via the names listed in `__all__` below.  The leaf
modules (`port.py`, `chip.py`, `format.py`, …) remain importable
directly — code that does so is signalling "I'm reaching past the
curated surface, on purpose."

The `wirebench` top-level package re-exports the names below plus
the component catalogue for end-user convenience.

`framework.export` is a separate subpackage — each export format
(KiCad netlist, SPICE deck, BOM, …) is a tangible artifact the
framework emits, so it earns its own directory.  The non-physical
categories (signal-flow primitives, pin classification, file
persistence) stay flat at this level because grouping them into
subpackages would be a software-organisation abstraction without a
real-world referent — see `feedback_physical_fidelity_primary`
in memory.
"""
# Base classes — the abstract component hierarchy.
from framework.board       import Board
from framework.chip        import Chip
from framework.circuit     import Circuit
from framework.connector   import Connector, declare_mating_pair
from framework.diode       import Diode
from framework.part        import Part
from framework.pin         import Pin, PinId
from framework.transistor  import BJT, MOSFET, Transistor

# Netlist-graph primitives — signals, ports, nodes, grounds.
from framework.ground   import GroundDomain, ELECTRICAL
from framework.node     import Node
from framework.port     import Port, Direction
from framework.port_map import PortMap
from framework.signals  import Analog, Digital

# The verbs that build the graph.
from framework.mate import mate
from framework.wire import wire

# Pin classification metadata.
from framework.drive_type   import DriveType
from framework.pin_function import PinFunction, infer_pin_function

# Component registry (chip-type lookup used by save/load and dynamic
# discovery).
from framework.registry import register, lookup, registered_names, is_registered

# Save / load .wirebench files.
from framework.format           import save_wirebench, load_wirebench
from framework.format_extension import serialize_kwargs, deserialize_kwargs

# Identity / refdes.
from framework.refdes import RefdesBearing, RefdesNumber, validate_refdes

# Exception hierarchy.
from framework.errors import (
    WirebenchError,
    CircuitError,
    WiringError, ShortCircuitError, FloatingNetError, UnconnectedPinError,
    NodeMergeError, EmptyWireError,
    SignalError, SignalTypeMismatchError, DomainCrossingError,
    PortContentionError,
    ForbiddenStateError,
    PartError, RefdesError, DuplicateRegistrationError, UnknownPartError,
    PartConfigurationError, PartParameterError,
    MatingError, IncompatibleMateError, UnmateableError,
    PinCountMismatchError, PitchMismatchError,
    FormatError, SaveError, LoadError, UnknownFormatError,
    BreadboardIncompatibleError,
    RendererRegistryError, DuplicateRendererError, RendererNotFoundError,
    UsageError, WiredChipCallError, AmbiguousPinNameError,
    CompositeShapeError, UnknownPortError, OrphanWireError,
)

__all__ = [
    # Base classes
    'Board', 'Chip', 'Circuit', 'Connector', 'Diode', 'Part',
    'Pin', 'PinId', 'BJT', 'MOSFET', 'Transistor',
    'declare_mating_pair',

    # Netlist-graph primitives
    'Analog', 'Digital',
    'Direction', 'Port', 'PortMap',
    'Node',
    'GroundDomain', 'ELECTRICAL',
    'wire', 'mate',

    # Pin classification
    'PinFunction', 'infer_pin_function',
    'DriveType',

    # Registry
    'register', 'lookup', 'registered_names', 'is_registered',

    # File persistence
    'save_wirebench', 'load_wirebench',
    'serialize_kwargs', 'deserialize_kwargs',

    # Identity
    'RefdesBearing', 'RefdesNumber', 'validate_refdes',

    # Exception hierarchy
    'WirebenchError',
    'CircuitError',
    'WiringError', 'ShortCircuitError', 'FloatingNetError',
    'UnconnectedPinError', 'NodeMergeError', 'EmptyWireError',
    'SignalError', 'SignalTypeMismatchError', 'DomainCrossingError',
    'PortContentionError',
    'ForbiddenStateError',
    'PartError', 'RefdesError', 'DuplicateRegistrationError',
    'UnknownPartError', 'PartConfigurationError', 'PartParameterError',
    'MatingError', 'IncompatibleMateError', 'UnmateableError',
    'PinCountMismatchError', 'PitchMismatchError',
    'FormatError', 'SaveError', 'LoadError', 'UnknownFormatError',
    'BreadboardIncompatibleError',
    'RendererRegistryError', 'DuplicateRendererError', 'RendererNotFoundError',
    'UsageError', 'WiredChipCallError', 'AmbiguousPinNameError',
    'CompositeShapeError', 'UnknownPortError', 'OrphanWireError',
]
