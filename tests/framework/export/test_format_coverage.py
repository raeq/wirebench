"""Cross-format MRO-coverage smoke test (spec §11.3).

For every (component class, format) pair, lookup_renderer must
succeed. The MRO dispatch means a renderer registered at Connector
covers every concrete connector subclass, etc.

If a test fails because a renderer is missing, the fix is to add
the renderer — not to skip the class.
"""
from __future__ import annotations

import pytest

# Trigger every adapter's registration.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.bom      # noqa: F401
import framework.export.dot      # noqa: F401
import framework.export.kicad    # noqa: F401
import framework.export.mermaid  # noqa: F401
import framework.export.spice    # noqa: F401
import framework.export.yosys    # noqa: F401

from framework.export import list_formats
from framework.export.base import lookup_renderer
from framework.registry import lookup, registered_names


@pytest.mark.parametrize("fmt", ['bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys'])
def test_every_class_has_renderer_for_format(fmt):
    missing: list[str] = []
    for name in registered_names():
        cls = lookup(name)
        try:
            lookup_renderer(cls, fmt)
        except KeyError:
            missing.append(name)
    assert not missing, f"Missing {fmt!r} renderers: {missing}"


def test_list_formats_returns_all_six():
    fmts = set(list_formats())
    assert {'bom', 'dot', 'kicad', 'mermaid', 'spice', 'yosys'} <= fmts
