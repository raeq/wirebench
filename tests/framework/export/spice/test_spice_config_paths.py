"""Cover the configurable code paths in the SPICE adapter: net-name
style (qualified / short_hash / default), header-comment emission,
inline-model emission.  The default-config goldens don't exercise
these alternatives."""
from __future__ import annotations

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import framework.export.spice  # noqa: F401

from framework.circuit import Circuit
from framework.export import export_to_string
from framework.export.base import SpiceExportConfig
from water_alarm import WaterAlarm


def _wa() -> WaterAlarm:
    return WaterAlarm()


def test_qualified_net_name_style():
    cfg = SpiceExportConfig(net_name_style='qualified')
    out = export_to_string(_wa(), 'spice', config=cfg)
    # Qualified format is `<refdes>_<port>` for non-rail nets.
    lines = [l for l in out.splitlines() if l and not l.startswith(('.', '*'))]
    has_qualified = any('_' in tok for line in lines for tok in line.split())
    assert has_qualified


def test_short_hash_net_name_style():
    cfg = SpiceExportConfig(net_name_style='short_hash')
    out = export_to_string(_wa(), 'spice', config=cfg)
    # Hash format `nXXXX` (4 hex chars).
    import re
    assert re.search(r'\bn[0-9a-f]{4}\b', out)


def test_header_comment_emission():
    cfg = SpiceExportConfig(include_header_comment=True)
    out = export_to_string(_wa(), 'spice', config=cfg)
    assert out.startswith('* Exported from circuitry')


def test_inline_models_emission():
    cfg = SpiceExportConfig(emit_models_inline=True)
    out = export_to_string(_wa(), 'spice', config=cfg)
    # Inline mode embeds .SUBCKT / .MODEL blocks for every used model.
    assert '.SUBCKT' in out or '.MODEL' in out
    # And does NOT emit a .LIB directive.
    assert '.LIB' not in out
