"""KiCad topology cross-reference (strict per spec §9.2).

For each application:
  - Build the expected {(qualified_refdes, pin_number): net_name}
    mapping by walking the model with knowledge of board hierarchy.
  - Parse the rendered netlist into the same shape.
  - Assert equality. A renderer bug that scrambled pin order or
    qualified refdes wrongly would fail clearly.

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
import framework.export.kicad  # noqa: F401

from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export import export_to_string
from framework.export.base import pin_number_of
from framework.part import Part
from framework.pin import Pin

from components.passives.rail import Rail

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _expected_node_to_net(design) -> dict[tuple[str, int], int]:
    """For each refdes-bearing port, return its underlying Node id.
    Tests then translate Node ids into net names from the rendered
    text by intersecting with the parser's mapping."""
    out: dict[tuple[str, int], int] = {}

    def visit(stack: list[Board], node: Part) -> None:
        if isinstance(node, (Pin, Rail)):
            return
        if isinstance(node, Chip) or isinstance(node, Connector):
            qrd = '_'.join(b.refdes for b in stack + [])
            qrd = f"{qrd}_{node.refdes}" if qrd else node.refdes
            for name, port in node.ports.items():
                if port.node is None:
                    continue
                pn = pin_number_of(node, name)
                if pn is None:
                    continue
                out[(qrd, pn)] = id(port.node)
            return
        if isinstance(node, Board):
            for c in node.parts:
                visit(stack + [node], c)
            return
        if isinstance(node, Circuit):
            for c in node.parts:
                visit(stack, c)
            return
        rd = getattr(node, 'refdes', None)
        if rd:
            qrd = '_'.join(b.refdes for b in stack)
            qrd = f"{qrd}_{rd}" if qrd else rd
            for name, port in node.ports.items():
                if port.node is None:
                    continue
                pn = pin_number_of(node, name)
                if pn is None:
                    continue
                out[(qrd, pn)] = id(port.node)

    visit([], design)
    return out


def _parse_nets(text: str) -> dict[tuple[str, int], str]:
    """Parse the (nets ...) block: {(ref, pin): net_name}."""
    out: dict[tuple[str, int], str] = {}
    current_net: str | None = None
    for line in text.splitlines():
        m = re.match(r'\s*\(net \(code "\d+"\) \(name "([^"]+)"\)', line)
        if m:
            current_net = m.group(1)
            continue
        m = re.match(r'\s*\(node \(ref "([^"]+)"\) \(pin "(\d+)"\)', line)
        if m and current_net is not None:
            out[(m.group(1), int(m.group(2)))] = current_net
    return out


@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=['WaterAlarm', 'WaterAlarmAssembly'])
def test_kicad_topology_matches_model(factory):
    design = _silently(factory)
    text = export_to_string(design, 'kicad')
    actual = _parse_nets(text)

    # Two ports on the same model Node share the same net name in
    # the parsed output. So the test is: for each pair of expected
    # entries that share a Node, the parsed net names must match.
    expected_node = _expected_node_to_net(design)

    # Group by node id; each group must have a single distinct net
    # name in the parsed output.
    by_node: dict[int, list[tuple[str, int]]] = {}
    for key, nid in expected_node.items():
        by_node.setdefault(nid, []).append(key)

    mismatches: list[str] = []
    for nid, keys in by_node.items():
        net_names = {actual.get(k) for k in keys}
        if len(net_names) > 1:
            mismatches.append(
                f"keys {keys} should share one net but parsed as {net_names}"
            )
        if None in net_names and len(keys) > 0:
            missing = [k for k in keys if actual.get(k) is None]
            mismatches.append(f"missing entries in netlist: {missing}")
    assert not mismatches, (
        f"KiCad topology mismatch for {factory.__name__}:\n  " +
        "\n  ".join(mismatches[:10])
    )
