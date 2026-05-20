"""Cross-family `V_F` / `V_BREAKDOWN_R` consistency for the Diode family.

`D_OA90` introduced the `V_F: ClassVar[float]` attribute (the
germanium-vs-silicon distinction is its whole reason for being in the
catalogue).  For downstream tooling to read forward voltage uniformly
across every Diode subclass, every concrete subclass must declare the
same ClassVar.

Similarly, Zener subclasses must declare `V_BREAKDOWN_R: ClassVar[float]`
(the reverse-breakdown voltage that's the Zener's operating point);
non-Zener subclasses declare it as `None`.

This module discovers every concrete `Diode` subclass via the registry
and asserts both ClassVars are present with sensible types.
"""
from __future__ import annotations

import inspect

import pytest

# Trigger every diode registration.
import components.diodes  # noqa: F401
from framework.diode import Diode
from framework.registry import _REGISTRY


def _concrete_diode_classes():
    out = []
    for name, cls in _REGISTRY.items():
        if not inspect.isclass(cls):
            continue
        if not issubclass(cls, Diode):
            continue
        if cls is Diode:
            continue
        out.append((name, cls))
    return sorted(out, key=lambda t: t[0])


_DIODE_CLASSES = _concrete_diode_classes()


@pytest.mark.parametrize('name,cls', _DIODE_CLASSES, ids=[n for n, _ in _DIODE_CLASSES])
def test_diode_declares_v_f(name, cls):
    """Every concrete Diode subclass declares `V_F: ClassVar[float]`
    so downstream tooling can read forward voltage uniformly."""
    assert hasattr(cls, 'V_F'), (
        f"{name} is missing V_F ClassVar.  Every concrete Diode "
        f"subclass must declare its typical forward voltage drop "
        f"so downstream tooling (SPICE picker, assembly guide, BOM "
        f"notes) can read it uniformly."
    )
    assert isinstance(cls.V_F, float), (
        f"{name}.V_F is {type(cls.V_F).__name__}; expected float."
    )
    # Sanity-bound: 0 < V_F < 2 V covers germanium (0.2), Schottky
    # (0.3), silicon (0.7), and the high end of red-LED-like junctions.
    assert 0 < cls.V_F < 2.0, (
        f"{name}.V_F = {cls.V_F!r} is outside [0, 2] V — unlikely for "
        f"any real diode."
    )


@pytest.mark.parametrize('name,cls', _DIODE_CLASSES, ids=[n for n, _ in _DIODE_CLASSES])
def test_diode_declares_v_breakdown_r(name, cls):
    """Every concrete Diode subclass declares `V_BREAKDOWN_R: float | None`.
    Zeners set the value to their reverse-breakdown voltage; everything
    else sets it to None."""
    assert hasattr(cls, 'V_BREAKDOWN_R'), (
        f"{name} is missing V_BREAKDOWN_R ClassVar.  Set to None for "
        f"non-Zener diodes; set to the V_Z value for Zeners."
    )
    v = cls.V_BREAKDOWN_R
    assert v is None or (isinstance(v, float) and v > 0), (
        f"{name}.V_BREAKDOWN_R = {v!r}; expected None or a positive float."
    )


def test_known_zeners_carry_breakdown_value():
    """The three Zener subclasses in the catalogue have known
    breakdown voltages; assert they're declared correctly."""
    from components.diodes.d1n4728a import D1N4728A
    from components.diodes.d1n4733a import D1N4733A
    from components.diodes.d1n4742a import D1N4742A
    assert D1N4728A.V_BREAKDOWN_R == pytest.approx(3.3)
    assert D1N4733A.V_BREAKDOWN_R == pytest.approx(5.1)
    assert D1N4742A.V_BREAKDOWN_R == pytest.approx(12.0)


def test_germanium_v_f_lower_than_silicon():
    """The whole reason `D_OA90` exists in the catalogue: its V_F
    (~0.2 V) is dramatically lower than silicon's (~0.7 V), and this
    is what makes a crystal-radio receiver detect microvolt RF
    signals.  Assert the inequality holds."""
    from components.diodes.oa90 import D_OA90
    from components.diodes.d1n4148 import D1N4148
    assert D_OA90.V_F < D1N4148.V_F
    assert D_OA90.V_F < 0.4
