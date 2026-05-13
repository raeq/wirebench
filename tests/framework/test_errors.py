"""Exception-hierarchy tests.

Verifies the framework's domain-specific exception classes:

  - every leaf has the right MRO (family parent + built-in)
  - every leaf is importable from the public `wirebench` package
  - the actual raise sites in the source produce the expected leaves
    (not just the parent built-ins)
"""
from __future__ import annotations

import pytest

import components.chips     # noqa: F401 - registry triggers
import components.passives  # noqa: F401
import components.connectors  # noqa: F401

from framework import errors as E
from wirebench import (
    WirebenchError,
    CircuitError, WiringError, ShortCircuitError, FloatingNetError,
    UnconnectedPinError, NodeMergeError, EmptyWireError,
    SignalError, SignalTypeMismatchError, DomainCrossingError,
    PortContentionError,
    PolarityError,
    ForbiddenStateError,
    PartError, RefdesError, DuplicateRegistrationError, UnknownPartError,
    PartConfigurationError, PartParameterError,
    MatingError, IncompatibleMateError, UnmateableError,
    PinCountMismatchError, PitchMismatchError,
    FormatError, SaveError, LoadError, UnknownFormatError,
    RendererRegistryError, DuplicateRendererError, RendererNotFoundError,
    UsageError, WiredChipCallError, AmbiguousPinNameError,
    CompositeShapeError, UnknownPortError,
)


# ---------------------------------------------------------------- MRO

# Pair every leaf with the family classes / built-ins it must inherit
# from.  Each leaf is rooted at `WirebenchError`; this table records the
# specifically required ancestors beyond that.
MRO_TABLE: list[tuple[type, tuple[type, ...]]] = [
    # --- Wiring family ---
    (ShortCircuitError,   (WiringError, CircuitError, ValueError)),
    (FloatingNetError,    (WiringError, CircuitError, ValueError)),
    (UnconnectedPinError, (WiringError, CircuitError, ValueError)),
    (NodeMergeError,      (WiringError, CircuitError, ValueError)),
    (EmptyWireError,      (WiringError, CircuitError, ValueError)),
    # --- Signal family ---
    (SignalTypeMismatchError, (SignalError, CircuitError, TypeError)),
    (DomainCrossingError,     (SignalError, CircuitError, ValueError)),
    (PortContentionError,     (SignalError, CircuitError, ValueError)),
    # --- Polarity (sibling of Wiring; no leaves yet — class itself) ---
    (PolarityError,           (CircuitError, ValueError)),
    # --- ForbiddenState (no leaves yet — class itself) ---
    (ForbiddenStateError,     (CircuitError, ValueError)),
    # --- Part family ---
    (RefdesError,                 (PartError, CircuitError, ValueError)),
    (DuplicateRegistrationError,  (PartError, CircuitError, ValueError)),
    (UnknownPartError,            (PartError, CircuitError, KeyError)),
    (PartConfigurationError,      (PartError, CircuitError, TypeError)),
    (PartParameterError,          (PartError, CircuitError, ValueError)),
    # --- Mating family ---
    (IncompatibleMateError,   (MatingError, CircuitError, TypeError)),
    (UnmateableError,         (MatingError, CircuitError, TypeError)),
    (PinCountMismatchError,   (MatingError, CircuitError, ValueError)),
    (PitchMismatchError,      (MatingError, CircuitError, ValueError)),
    # --- Format family ---
    (SaveError,               (FormatError, ValueError)),
    (LoadError,               (FormatError, ValueError)),
    (UnknownFormatError,      (FormatError, ValueError)),
    (DuplicateRendererError,  (RendererRegistryError, FormatError, ValueError)),
    (RendererNotFoundError,   (RendererRegistryError, FormatError, KeyError)),
    # --- Usage family ---
    (WiredChipCallError,      (UsageError, RuntimeError)),
    (AmbiguousPinNameError,   (UsageError, KeyError)),
    (CompositeShapeError,     (UsageError, TypeError)),
    (UnknownPortError,        (UsageError, ValueError)),
]


@pytest.mark.parametrize('cls,ancestors', MRO_TABLE,
                         ids=[cls.__name__ for cls, _ in MRO_TABLE])
def test_leaf_mro(cls: type, ancestors: tuple[type, ...]) -> None:
    """Every leaf inherits from its family parents + the appropriate
    Python built-in, *and* ultimately from WirebenchError."""
    for ancestor in ancestors:
        assert issubclass(cls, ancestor), (
            f"{cls.__name__} must inherit from {ancestor.__name__}; "
            f"MRO is {[c.__name__ for c in cls.__mro__]}"
        )
    assert issubclass(cls, WirebenchError), (
        f"{cls.__name__} must inherit from WirebenchError"
    )


# -------------------------------------------------------- catchability

def test_wirebench_error_catches_every_leaf() -> None:
    """Every leaf can be caught by the umbrella `WirebenchError`."""
    for cls, _ in MRO_TABLE:
        instance = cls('m')
        assert isinstance(instance, WirebenchError)


def test_family_classes_are_abstract_under_wirebench_error() -> None:
    """Family classes also inherit from WirebenchError (not just leaves)."""
    families = [
        CircuitError, WiringError, SignalError, PartError, MatingError,
        FormatError, UsageError, RendererRegistryError,
    ]
    for family in families:
        assert issubclass(family, WirebenchError)


# -------------------------------------------------- importability

def test_every_leaf_is_importable_from_wirebench_package() -> None:
    """Public re-export: `from wirebench import LeafError` works."""
    import wirebench
    for cls, _ in MRO_TABLE:
        assert getattr(wirebench, cls.__name__, None) is cls, (
            f"{cls.__name__} is not re-exported from `wirebench`"
        )


# ---------------------------------------------- integration with raises

def test_short_circuit_raises_short_circuit_error() -> None:
    """Two OUT ports on the same wire → ShortCircuitError, not bare
    ValueError."""
    from framework.ground import ELECTRICAL
    from framework.port import Direction, Port
    from framework.signals import Digital
    from framework.wire import wire

    out1 = Port('o1', Direction.OUT, ELECTRICAL, signal_type=Digital)
    out2 = Port('o2', Direction.OUT, ELECTRICAL, signal_type=Digital)
    with pytest.raises(ShortCircuitError):
        wire(out1, out2)


def test_domain_crossing_raises_domain_crossing_error() -> None:
    """Two ports in distinct GroundDomains → DomainCrossingError."""
    from framework.ground import ELECTRICAL, GroundDomain
    from framework.port import Direction, Port
    from framework.signals import Digital
    from framework.wire import wire

    iso = GroundDomain('test_iso_dom')
    a = Port('a', Direction.OUT, ELECTRICAL, signal_type=Digital)
    b = Port('b', Direction.IN, iso, signal_type=Digital)
    with pytest.raises(DomainCrossingError):
        wire(a, b)


def test_node_merge_raises_node_merge_error() -> None:
    """Two ports already on distinct nets → NodeMergeError.  Use BIDIR
    bridge ports so the second wire() call has a passive driver and
    proceeds to the merge check."""
    from framework.ground import ELECTRICAL
    from framework.port import Direction, Port
    from framework.signals import Digital
    from framework.wire import wire

    a_out = Port('ao', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    a_bid = Port('ab', Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    b_out = Port('bo', Direction.OUT,   ELECTRICAL, signal_type=Digital)
    b_bid = Port('bb', Direction.BIDIR, ELECTRICAL, signal_type=Digital)
    wire(a_out, a_bid)
    wire(b_out, b_bid)
    with pytest.raises(NodeMergeError):
        wire(a_bid, b_bid)


def test_refdes_error_for_unknown_prefix() -> None:
    from framework.refdes import validate_refdes
    with pytest.raises(RefdesError):
        validate_refdes('ZZ', 1)


def test_refdes_error_for_non_positive_number() -> None:
    from framework.refdes import validate_refdes
    with pytest.raises(RefdesError):
        validate_refdes('R', 0)


def test_duplicate_registration_error() -> None:
    from framework.part import Part
    from framework.registry import register

    class _A(Part):
        @property
        def ports(self): return {}
        def evaluate(self): pass

    class _B(Part):
        @property
        def ports(self): return {}
        def evaluate(self): pass

    register('_DupRegTest_unique')(_A)
    with pytest.raises(DuplicateRegistrationError):
        register('_DupRegTest_unique')(_B)


def test_unknown_part_error() -> None:
    from framework.registry import lookup
    with pytest.raises(UnknownPartError):
        lookup('NoSuchPart_xyzzy')


def test_forbidden_state_for_sr_both_active() -> None:
    """NORLatch evaluated with S=R=1 → ForbiddenStateError."""
    from components.chips.concepts.nor_latch import NORLatch
    latch = NORLatch()
    latch.ports['s'].drive(True)
    latch.ports['r'].drive(True)
    with pytest.raises(ForbiddenStateError):
        latch.evaluate()


def test_incompatible_mate_error() -> None:
    """USB-A receptacle ↔ TRRS jack (or any wrong family) →
    IncompatibleMateError."""
    from components.connectors.usb   import USBAReceptacle, USBAPlug
    from components.connectors.audio import Audio3p5mmTRSJack
    from framework.mate import mate

    a = USBAReceptacle(refdes_number=1)
    # USBAReceptacle.MATES_WITH is USBAPlug; a TRSJack is the wrong family.
    trs = Audio3p5mmTRSJack(refdes_number=2)
    with pytest.raises(IncompatibleMateError):
        mate(a, trs)


def test_pin_count_mismatch_error() -> None:
    """Two parametric headers with mismatched pin counts → leaf class."""
    from components.connectors.headers import Header1xNFemale, Header1xNMale
    from framework.mate import mate

    j = Header1xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    p = Header1xNMale  (pin_count=5, pitch_mm=2.54, refdes_number=2)
    with pytest.raises(PinCountMismatchError):
        mate(j, p)


def test_pitch_mismatch_error() -> None:
    from components.connectors.headers import Header1xNFemale, Header1xNMale
    from framework.mate import mate

    j = Header1xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    p = Header1xNMale  (pin_count=4, pitch_mm=1.27, refdes_number=2)
    with pytest.raises(PitchMismatchError):
        mate(j, p)


def test_part_parameter_error_for_out_of_range_soc() -> None:
    from components.passives.cell import Cell
    cell = Cell(refdes_number=1)
    with pytest.raises(PartParameterError):
        cell.state_of_charge = 1.5


def test_part_configuration_error_for_same_isolation_domain() -> None:
    """IsolatedChannel needs two distinct ground domains."""
    from components.chips.concepts.isolated_channel import IsolatedChannel
    from framework.ground import ELECTRICAL
    with pytest.raises(PartConfigurationError):
        IsolatedChannel(input_domain=ELECTRICAL, output_domain=ELECTRICAL)


def test_unknown_format_error() -> None:
    """`export_to_string` with a typo'd format name raises the leaf,
    not a bare ValueError."""
    from framework.export import export_to_string
    from water_alarm import WaterAlarm
    with pytest.raises(UnknownFormatError, match='spcie'):
        export_to_string(WaterAlarm(), 'spcie')   # typo of 'spice'


def test_wired_chip_call_error() -> None:
    """Calling a wired chip's standalone `__call__` raises
    WiredChipCallError."""
    from components.chips.concepts.nor_latch import NORLatch
    from components.passives.rail import Rail
    from framework.wire import wire

    latch = NORLatch()
    s_drv = Rail(False)
    wire(s_drv.ports['out'], latch.ports['s'])
    with pytest.raises(WiredChipCallError):
        latch(True, False)
