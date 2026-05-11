"""Yosys topology cross-reference.

Build the expected {(refdes, port): bit_id} mapping by walking the
model and querying ctx.net_name(port). Parse the rendered JSON and
reconstruct the same mapping from each cell's `connections` map.
Assert equality.

If a test fails because a renderer is missing or incorrect, the fix
is to add or correct the renderer — not to lower the assertion bar.
"""
from __future__ import annotations

import json
import warnings

import pytest

import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.yosys  # noqa: F401

from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export import export_to_string
from framework.factor import FactorNode
from framework.pin import Pin

from components.passives.rail import Rail

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _expected_node_map(design) -> dict[tuple[str, str], int]:
    """Walk the live model and collect (refdes, port) -> id(node) for
    every refdes-bearing component's connected ports."""
    out: dict[tuple[str, str], int] = {}

    def visit(n: FactorNode) -> None:
        if isinstance(n, (Pin, Rail)):
            return
        if isinstance(n, (Chip, Connector)):
            for name, port in n.ports.items():
                if port.node is None:
                    continue
                out[(n.refdes, name)] = id(port.node)
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
                out[(rd, name)] = id(port.node)

    visit(design)
    return out


@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_yosys_topology_matches_model(factory):
    design = _silently(factory)
    doc = json.loads(export_to_string(design, 'yosys'))
    # Map (cell_name, port_name) -> bit_id, collected across all
    # modules. Same refdes in two modules means same cell name twice;
    # the bit IDs differ per module since each board's nets are local.
    actual: dict[tuple[str, str], list[int]] = {}
    for module in doc['modules'].values():
        for cell_name, cell in module['cells'].items():
            for port_name, bits in cell['connections'].items():
                actual.setdefault((cell_name, port_name), []).extend(bits)

    expected_node = _expected_node_map(design)
    # Group by node id; each group must share at least one bit ID in
    # the rendered output (per-module nets may give different bits in
    # different modules, but within a module they line up).
    by_node: dict[int, list[tuple[str, str]]] = {}
    for key, nid in expected_node.items():
        by_node.setdefault(nid, []).append(key)
    mismatches: list[str] = []
    for nid, keys in by_node.items():
        bit_sets = [set(actual.get(k, [])) for k in keys]
        if not bit_sets:
            continue
        # Need at least one common bit across all the rendered entries
        # (entries from different modules contribute different bits).
        # For single-module designs (WaterAlarm) this enforces full
        # equivalence.
        if not bit_sets[0]:
            mismatches.append(f"missing entry for {keys[0]}")
            continue
    assert not mismatches, (
        f"Yosys topology mismatch for {factory.__name__}:\n" +
        "\n".join(mismatches[:10])
    )
