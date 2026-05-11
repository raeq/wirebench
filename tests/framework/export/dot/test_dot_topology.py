"""DOT topology cross-reference (weak form per spec §9.2).

DOT edges aren't ordered, so we check that every (refdes, port, net)
triple from the live model appears *somewhere* in the rendered edges.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import re
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.dot  # noqa: F401

from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export.base import ExporterContext
from framework.export.dot import render as dot_render
from framework.factor import FactorNode
from framework.pin import Pin

from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _expected_triples(design, ctx: ExporterContext) -> set[tuple[str, str, str]]:
    """Walk model, return {(refdes, port_name, net_name)}. Skips
    conductors (Pin, Connector) and Rails."""
    out: set[tuple[str, str, str]] = set()

    def visit(n: FactorNode) -> None:
        if isinstance(n, (Pin, Connector, Rail)):
            return
        if isinstance(n, Chip):
            for name, port in n.ports.items():
                if port.node is None:
                    continue
                out.add((n.refdes, name, ctx.net_name(port)))
            return
        if isinstance(n, Circuit):
            for c in n._factor_nodes:
                visit(c)
            return
        rd = getattr(n, 'refdes', None)
        if rd:
            for name, port in n.ports.items():
                if port.node is None:
                    continue
                out.add((rd, name, ctx.net_name(port)))

    visit(design)
    return out


@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_dot_every_expected_triple_appears(factory):
    design = _silently(factory)
    ctx = ExporterContext(design, 'dot')
    text = dot_render(design, ctx)
    expected = _expected_triples(design, ctx)
    missing: list[tuple[str, str, str]] = []
    for rd, port, net in expected:
        # Look for `<refdes> -> <net> [taillabel="<port>"]`
        pattern = re.compile(
            rf'\b{re.escape(rd)} -> {re.escape(net)} \[taillabel="{re.escape(port)}"\];'
        )
        if not pattern.search(text):
            missing.append((rd, port, net))
    assert not missing, (
        f"DOT missing edges for {factory.__name__}:\n" +
        '\n'.join(f"  {t}" for t in missing[:10])
    )
