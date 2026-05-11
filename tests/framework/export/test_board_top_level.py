"""Cover the dot / mermaid adapter paths that handle a Board as the
top-level export target (not wrapped in a Circuit).  The standard
`water_alarm_assembly` golden tests run an Assembly through every
adapter, but a bare Board doesn't appear in any golden."""
from __future__ import annotations

import warnings

import pytest

import components.chips      # noqa: F401
import components.passives   # noqa: F401
import components.connectors # noqa: F401
import framework.export.bom      # noqa: F401
import framework.export.dot      # noqa: F401
import framework.export.kicad    # noqa: F401
import framework.export.mermaid  # noqa: F401
import framework.export.spice    # noqa: F401
import framework.export.yosys    # noqa: F401

from framework.export import export_to_string

from water_alarm_split import SensorBoard


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@pytest.mark.parametrize('fmt', ['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys'])
def test_board_exports_at_top_level(fmt):
    board = _silently(SensorBoard, refdes_number=1)
    out = _silently(export_to_string, board, fmt)
    assert isinstance(out, str)
    assert len(out) > 0
