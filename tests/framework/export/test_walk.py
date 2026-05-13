"""Tests for the hierarchical-walk helpers used by exporters that need
to bracket Assembly / Board / Chip composites in their output.
"""
from __future__ import annotations

import components.chips     # noqa: F401  (registers SN74HC04)
import components.passives  # noqa: F401

from framework.circuit import Circuit
from framework.export.walk import Path, iter_composites, walk_hierarchy


# ----- Path value object ---------------------------------------------

def test_path_empty():
    p = Path.empty()
    assert p.segments == ()
    assert p.qualified_refdes() == ''


def test_path_with_child_extends():
    p = Path.empty().with_child('A1').with_child('U1')
    assert p.segments == ('A1', 'U1')
    assert p.qualified_refdes() == 'A1.U1'


def test_path_str_returns_root_marker_when_empty():
    assert str(Path.empty()) == '<root>'


def test_path_str_returns_qualified_when_non_empty():
    assert str(Path.empty().with_child('A1')) == 'A1'
    assert str(Path.empty().with_child('A1').with_child('U2')) == 'A1.U2'


# ----- walk_hierarchy --------------------------------------------------

def test_walk_visits_root_with_empty_path():
    """A single-component circuit: visitor sees the root Circuit with
    Path.empty() and no descendants beyond the leaf component."""
    from components.chips.sn74hc04 import SN74HC04
    ic = SN74HC04(refdes_number=1)
    root = Circuit(parts=[ic], ports={})

    seen: list[tuple[type, str]] = []
    walk_hierarchy(root, lambda c, p: seen.append((type(c), p.qualified_refdes())))

    # Root composite plus the chip (also a Circuit subclass).
    assert seen[0] == (Circuit, '')
    types_seen = {t for t, _ in seen}
    assert Circuit in types_seen


def test_walk_descends_into_chip_composites():
    """SN74HC04 is itself a Circuit; the walker recurses into it."""
    from components.chips.sn74hc04 import SN74HC04
    ic = SN74HC04(refdes_number=1)
    root = Circuit(parts=[ic], ports={})

    paths: list[str] = []
    walk_hierarchy(root, lambda c, p: paths.append(p.qualified_refdes()))

    # Chip carries a refdes ('U1'); after descending, the path
    # qualified-refdes is 'U1'.
    assert '' in paths   # root
    assert 'U1' in paths  # chip itself


def test_iter_composites_yields_same_set_as_walk_hierarchy():
    from components.chips.sn74hc04 import SN74HC04
    ic = SN74HC04(refdes_number=1)
    root = Circuit(parts=[ic], ports={})

    walked: list[tuple[int, str]] = []
    walk_hierarchy(root, lambda c, p: walked.append((id(c), p.qualified_refdes())))
    via_iter = [(id(c), p.qualified_refdes()) for c, p in iter_composites(root)]

    assert walked == via_iter
