"""Tests for `Circuit` auto-collection + Rule 1 / Rule 2.

Auto-collection scans `self.__dict__` for `FactorNode` attributes when
`factor_nodes` is omitted from `super().__init__()`.  Two rules guard
against silent failures:

  Rule 1 — empty auto-collect raises `CompositeShapeError`, teaching
            the canonical `self.<name> = …` pattern.

  Rule 2 — orphan-port detection raises `OrphanWireError` when a wire
            joins a known factor_node to a port whose owner isn't in
            `factor_nodes`.  Fires regardless of how `factor_nodes`
            was obtained.
"""
from __future__ import annotations

import pytest

import components.chips     # noqa: F401 — register
import components.passives  # noqa: F401

from framework.circuit import Circuit
from framework.errors import CompositeShapeError, OrphanWireError
from framework.wire import wire

from components.chips.concepts.inverter import Inverter
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor


# ----------------------------------------------------------- auto-collect

class _ThreeAttrs(Circuit):
    def __init__(self) -> None:
        self.r1 = Resistor(330, refdes_number=1)
        self.d1 = LED('red', refdes_number=1)
        self.vcc = Rail(True)
        wire(self.vcc.out, self.r1.t1)
        wire(self.r1.t2, self.d1.anode)
        # d1.cathode left floating — would normally floating-net fail,
        # but LED.cathode is mandatory=False so the validator is OK.
        super().__init__()


def test_attribute_auto_collection_picks_up_self_attrs() -> None:
    c = _ThreeAttrs()
    assert {id(fn) for fn in c._factor_nodes} == {
        id(c.r1), id(c.d1), id(c.vcc),
    }


def test_attribute_auto_collection_preserves_insertion_order() -> None:
    c = _ThreeAttrs()
    assert c._factor_nodes == [c.r1, c.d1, c.vcc]


class _ListGates(Circuit):
    def __init__(self) -> None:
        self.gates = [Inverter() for _ in range(3)]
        self.rail = Rail(False)
        for g in self.gates:
            wire(self.rail.out, g.ports['a'])
        super().__init__()


def test_list_attribute_collection() -> None:
    c = _ListGates()
    inverters = [fn for fn in c._factor_nodes if isinstance(fn, Inverter)]
    assert len(inverters) == 3


class _TupleGates(Circuit):
    def __init__(self) -> None:
        self.gates = tuple(Inverter() for _ in range(2))
        self.rail = Rail(False)
        for g in self.gates:
            wire(self.rail.out, g.ports['a'])
        super().__init__()


def test_tuple_attribute_collection() -> None:
    c = _TupleGates()
    assert sum(1 for fn in c._factor_nodes if isinstance(fn, Inverter)) == 2


class _MixedAttrs(Circuit):
    def __init__(self) -> None:
        self.r = Resistor(100, refdes_number=1)
        self.gates = [Inverter(), Inverter()]
        self.rail = Rail(True)
        wire(self.rail.out, self.r.t1)
        for g in self.gates:
            wire(self.rail.out, g.ports['a'])
        super().__init__()


def test_mixed_scalar_and_list_attributes() -> None:
    c = _MixedAttrs()
    types = [type(fn).__name__ for fn in c._factor_nodes]
    assert types.count('Resistor') == 1
    assert types.count('Inverter') == 2
    assert types.count('Rail') == 1


class _WithJunk(Circuit):
    def __init__(self) -> None:
        self.config = {'foo': 'bar'}     # not a FactorNode
        self.threshold = 5.0
        self.r = Resistor(100, refdes_number=1)
        self.rail = Rail(True)
        wire(self.rail.out, self.r.t1)
        super().__init__()


def test_non_factornode_attributes_are_skipped() -> None:
    c = _WithJunk()
    types = {type(fn).__name__ for fn in c._factor_nodes}
    assert types == {'Resistor', 'Rail'}


def test_manual_override_preserved() -> None:
    """Explicit factor_nodes=[…] overrides auto-collect, even when
    self.x attributes are set."""

    class _ExplicitOverride(Circuit):
        def __init__(self) -> None:
            self.r = Resistor(100, refdes_number=1)
            self.unused_d = LED('red', refdes_number=2)  # not in explicit list
            self.rail = Rail(True)
            wire(self.rail.out, self.r.t1)
            super().__init__(factor_nodes=[self.r, self.rail])

    c = _ExplicitOverride()
    assert c._factor_nodes == [c.r, c.rail]


def test_empty_circuit_explicit_succeeds() -> None:
    """`super().__init__(factor_nodes=[])` is a legitimate opt-out."""

    class _Empty(Circuit):
        def __init__(self) -> None:
            super().__init__(factor_nodes=[])

    c = _Empty()
    assert c._factor_nodes == []


# ----------------------------------------------------------------- Rule 1

def test_empty_circuit_implicit_raises() -> None:
    """Rule 1: auto-collect yielded nothing → teaching error."""

    class _ForgotSelf(Circuit):
        def __init__(self) -> None:
            r = Resistor(100, refdes_number=1)  # local, not self.
            super().__init__()

    with pytest.raises(CompositeShapeError) as excinfo:
        _ForgotSelf()
    msg = str(excinfo.value)
    assert '_ForgotSelf' in msg
    assert 'self.<name>' in msg
    assert 'factor_nodes=[]' in msg   # mentions the explicit escape hatch


def test_dunder_prefixed_attributes_skipped() -> None:
    """Python's name mangling turns `self.__x` into
    `self._ClassName__x` — these double-underscored attrs may appear
    in __dict__ but the framework still ignores non-FactorNode values
    (the type check is the filter).
    """

    class _WithMangledAttr(Circuit):
        def __init__(self) -> None:
            self.__dunder_thing = "string, not a FactorNode"  # noqa: F841
            self.r = Resistor(100, refdes_number=1)
            self.rail = Rail(True)
            wire(self.rail.out, self.r.t1)
            super().__init__()

    c = _WithMangledAttr()
    # Only the real FactorNode attrs are collected.
    assert all(not isinstance(fn, str) for fn in c._factor_nodes)
    types = {type(fn).__name__ for fn in c._factor_nodes}
    assert types == {'Resistor', 'Rail'}


def test_deduplication_when_component_stored_twice() -> None:
    """A FactorNode reachable through two attributes (a scalar attr
    and a list attr) appears exactly once in `_factor_nodes`."""

    class _Duplicated(Circuit):
        def __init__(self) -> None:
            self.r = Resistor(100, refdes_number=1)
            self.collection = [self.r]
            self.rail = Rail(True)
            wire(self.rail.out, self.r.t1)
            super().__init__()

    c = _Duplicated()
    resistor_refs = [fn for fn in c._factor_nodes if isinstance(fn, Resistor)]
    assert len(resistor_refs) == 1


def test_ports_defaults_to_empty() -> None:
    c = _ThreeAttrs()
    assert c._ports == {}


def test_ports_explicit_preserved() -> None:
    class _WithSurface(Circuit):
        def __init__(self) -> None:
            self.r = Resistor(100, refdes_number=1)
            self.rail = Rail(True)
            wire(self.rail.out, self.r.t1)
            super().__init__(ports={'tap': self.r.t2})

    c = _WithSurface()
    assert 'tap' in c._ports


# ----------------------------------------------------------------- Rule 2

def test_orphan_port_detected_under_auto_collect() -> None:
    """Rule 2: `self.r1` is collected, local `d1` isn't, but the wire
    is real → orphan detected."""

    class _PartiallyOops(Circuit):
        def __init__(self) -> None:
            self.r1 = Resistor(330, refdes_number=1)
            self.rail = Rail(True)
            d1 = LED('red', refdes_number=1)        # LOCAL — orphan
            wire(self.rail.out, self.r1.t1)
            wire(self.r1.t2, d1.anode)
            super().__init__()

    with pytest.raises(OrphanWireError) as excinfo:
        _PartiallyOops()
    msg = str(excinfo.value)
    assert 'anode' in msg
    assert 'R1' in msg
    assert 'self.<name>' in msg


def test_orphan_port_detected_under_explicit_factor_nodes() -> None:
    """Rule 2: even with an explicit factor_nodes list, an omitted
    orphan is still caught."""

    class _ExplicitButIncomplete(Circuit):
        def __init__(self) -> None:
            r1 = Resistor(100, refdes_number=1)
            r2 = Resistor(100, refdes_number=2)
            rail = Rail(True)
            wire(rail.out, r1.t1, r2.t1)   # both r1 and r2 share the same net
            super().__init__(factor_nodes=[r1, rail])   # r2 deliberately omitted

    with pytest.raises(OrphanWireError):
        _ExplicitButIncomplete()


def test_no_orphan_when_everything_is_known() -> None:
    """Rule 2 quiet under correct usage."""
    # _ThreeAttrs is fully wired internally and stores every component
    # as self.<name>.  Constructing it must not raise.
    _ThreeAttrs()


def test_empty_factor_nodes_with_wired_locals_is_a_quiet_corner() -> None:
    """`factor_nodes=[]` plus wired local-variable components is a
    degenerate corner: the framework's view of the design is empty
    by declaration, so there are no known ports for Rule 2 to walk
    from, and no error fires.

    The spec optimistically called for Rule 2 to catch this case;
    in practice it would require global wire-tracking machinery that
    doesn't exist today.  Documenting the corner so a later change
    that adds the machinery can flip this test from "no error" to
    "OrphanWireError"."""

    class _EmptyOptOutButWired(Circuit):
        def __init__(self) -> None:
            r = Resistor(100, refdes_number=1)
            rail = Rail(True)
            wire(rail.out, r.t1)
            super().__init__(factor_nodes=[])

    # No error.
    _EmptyOptOutButWired()
