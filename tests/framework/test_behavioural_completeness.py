"""Phase-10 regression test for the behavioural-cell audit.

Walks every class in the component registry and asserts each
constructs cleanly — without `FloatingNetError`,
`PartConfigurationError`, or any other `CircuitryError`.  The
primary defence (Phase 9's `Chip.__init__` invariant) refuses
defective chips at construction; this test exercises that path on
every registered class so a newly-added chip can't ship without
either a behavioural cell or the `BARE_FIRMWARE_DRIVEN` opt-out.

The construction helper mirrors the registry-sweep helper used by
`test_substrate_compatibility.test_substrate_audit_doc_matches_live_classes`
and `scripts/generate_substrate_audit.py` — kept in sync so the
audit doc and the regression test treat every class the same way.

Boards require a parent Assembly to construct legitimately; the
test skips them with a clear note rather than passing-by-omission.
NE555_Monostable needs a `duration_ms` constructor arg; same
treatment.  All other classes must construct via the standard
two-attempt fallback (no-args, then `refdes_number=1`).
"""
from __future__ import annotations

from typing import Any

import pytest

import components.chips        # noqa: F401 — registry side effects
import components.connectors   # noqa: F401
import components.diodes       # noqa: F401
import components.passives     # noqa: F401
import components.relays       # noqa: F401
import components.transistors  # noqa: F401
import framework.board         # noqa: F401

from framework.errors import CircuitryError
from framework.factor import FactorNode
from framework.registry import _REGISTRY


# Classes the test deliberately skips, with the reason.  Anything
# that genuinely can't construct in isolation goes here; anything
# absent from this set must construct cleanly via `_construct_any`.
_LEGITIMATE_SKIPS: dict[str, str] = {
    'Board': 'Board needs concrete parent design with components',
}


def _construct_any(cls: type[FactorNode]) -> FactorNode | None:
    """Best-effort registry-sweep instantiation."""
    from typing import cast
    factory = cast(Any, cls)
    try:
        if hasattr(cls, 'REFDES_PREFIX'):
            kwargs: dict[str, object] = {'refdes_number': 1}
            name = cls.__name__
            if name == 'Resistor':         kwargs['ohms']    = 330
            elif name == 'Capacitor':      kwargs['farads']  = 100e-9
            elif name == 'Inductor':       kwargs['henries'] = 100e-6
            elif name == 'LED':            kwargs['color']   = 'red'
            elif name == 'Cell':           kwargs['initial_state_of_charge'] = 1.0
            elif name == 'NE555_Monostable': kwargs['duration_ms']  = 1.0
            elif 'Header' in name and ('Female' in name or 'Male' in name):
                kwargs.update({'pin_count': 4, 'pitch_mm': 2.54})
            elif name in ('IDC2xNMale', 'IDC2xNSocket'):
                kwargs.update({'pin_count': 10, 'pitch_mm': 2.54})
            elif name == 'ScrewTerminalBlock':
                kwargs.update({'pin_count': 4, 'pitch_mm': 5.08})
            elif name.startswith('JST'):
                kwargs['pin_count'] = 4
            elif name == 'ISOW7841':
                from framework.ground import GroundDomain
                kwargs['iso_domain'] = GroundDomain('iso_audit')
            return cast(FactorNode, factory(**kwargs))
        if cls.__name__ == 'Rail':
            return cast(FactorNode, factory(level=True))
        if cls.__name__ == 'DiodeOR':
            return cast(FactorNode, factory(input_names=('a',)))
        if cls.__name__ == 'Monostable':
            return cast(FactorNode, factory(duration_ms=1.0))
        return cast(FactorNode, factory())
    except Exception:
        return None


@pytest.mark.parametrize(
    'name',
    sorted(n for n in _REGISTRY if n not in _LEGITIMATE_SKIPS),
)
def test_class_constructs_cleanly(name: str) -> None:
    """Every registered component class constructs without raising
    a `CircuitryError`.  If this fails the class is incomplete —
    either it lacks a behavioural cell (Phase 9's invariant fires)
    or its construction has some other defect that prevents real
    use in a design."""
    cls = _REGISTRY[name]
    try:
        instance = _construct_any(cls)
    except CircuitryError as e:
        pytest.fail(
            f"{name} raises {type(e).__name__} on minimal-topology "
            f"construction: {e}\n\n"
            f"Per docs/behavioural-cell-audit-spec.md §6.2, every "
            f"registered class must construct cleanly.  Likely fix: "
            f"add a behavioural cell that drives the class's declared "
            f"OUT pins; see §7.2 for the cell pattern."
        )
    if instance is None:
        pytest.fail(
            f"{name} couldn't be constructed by `_construct_any`. "
            f"Either add a per-class branch to the helper above, or "
            f"add `'{name}'` to `_LEGITIMATE_SKIPS` with a written "
            f"reason if the class genuinely can't construct in "
            f"isolation (e.g. a Board that needs a parent Assembly)."
        )


@pytest.mark.parametrize('name', sorted(_LEGITIMATE_SKIPS))
def test_legitimate_skip_still_registered(name: str) -> None:
    """Every class on the `_LEGITIMATE_SKIPS` list is still
    registered — if a class disappears from the registry, drop it
    from the skip list at the same time so dead names don't
    accumulate."""
    assert name in _REGISTRY, (
        f"{name} is on `_LEGITIMATE_SKIPS` but no longer registered; "
        f"remove it from the skip list."
    )


def test_registry_covers_a_reasonable_breadth() -> None:
    """Sanity floor: an accidentally cleared registry shouldn't make
    the parametrised test pass with zero iterations."""
    assert len(_REGISTRY) >= 100, (
        f"Component registry has only {len(_REGISTRY)} entries; "
        f"this looks broken (expected >= 100)."
    )
