"""Off-board flying-lead LAYOUT regression — Phase 3.1a remediation.

Three catalogue parts mounted off-board (panel-mounted, with flying
leads to the breadboard) share a `LAYOUT.kind == 'off_board_flying_lead'`
marker so the breadboard renderer (once it dispatches on this kind)
can draw external-callout boxes rather than on-board footprints.  The
test asserts every such part declares a `Connector:` or
`Connector_Audio:` footprint — those footprints model the
*breadboard-side* connection, since the part itself lives off-board.
"""
from __future__ import annotations

import pytest

from components.passives.ferrite_aerial     import FerriteAerial
from components.passives.variable_capacitor import VariableCapacitor
from components.transducers.crystal_earpiece import CrystalEarpiece


_OFF_BOARD_PARTS = (
    ('VariableCapacitor', VariableCapacitor),
    ('FerriteAerial',     FerriteAerial),
    ('CrystalEarpiece',   CrystalEarpiece),
)


@pytest.mark.parametrize('name,cls', _OFF_BOARD_PARTS, ids=[n for n, _ in _OFF_BOARD_PARTS])
def test_off_board_layout_kind(name, cls):
    """Each off-board part declares `LAYOUT.kind == 'off_board_flying_lead'`."""
    assert cls.LAYOUT.get('kind') == 'off_board_flying_lead', (
        f"{name}: LAYOUT.kind is {cls.LAYOUT.get('kind')!r}; expected "
        f"'off_board_flying_lead' — the part is panel-mounted with "
        f"flying leads to the breadboard, not soldered on-board."
    )


@pytest.mark.parametrize('name,cls', _OFF_BOARD_PARTS, ids=[n for n, _ in _OFF_BOARD_PARTS])
def test_off_board_footprint_is_connector(name, cls):
    """The footprint models the *breadboard-side* connection, so it's
    a Connector:* family entry (header pair or audio jack) — not a
    radial-inductor or polarised-electrolytic footprint for a part
    that doesn't actually sit on the board."""
    fp = cls.FOOTPRINT
    assert fp is not None
    assert fp.startswith(('Connector:', 'Connector_Audio:')), (
        f"{name}: FOOTPRINT {fp!r} is not a Connector:* family — the "
        f"breadboard-side connection of an off-board part must be a "
        f"header pair or audio jack, since the part itself isn't on "
        f"the PCB."
    )


@pytest.mark.parametrize('name,cls', _OFF_BOARD_PARTS, ids=[n for n, _ in _OFF_BOARD_PARTS])
def test_off_board_layout_carries_description(name, cls):
    """The LAYOUT carries a free-text description naming what the
    actual off-board part is — useful for the assembly guide."""
    assert isinstance(cls.LAYOUT.get('description'), str)
    assert len(cls.LAYOUT['description']) > 20
