"""Topology cross-reference for the SPICE exporter.

For each application: walk the live model to build the expected
mapping `{(refdes, port_name): net_name}`, then parse the rendered
deck to recover the actual mapping, and assert they match.

A renderer bug that scrambled chip pin order — i.e. emitted the right
nets in the wrong slots — would slip past every existing structural
test but fail this one, because the per-port mapping is reconstructed
from each chip class's datasheet pin order.
"""
from __future__ import annotations

import functools
import re
import warnings

import pytest

# Trigger renderer + component registration.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.spice  # noqa: F401

from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector
from framework.export.base import ExportConfig, ExporterContext
from framework.export.spice import render as spice_render
from framework.registry import lookup


def _registered_class(name: str):
    """Return the class registered under `name`, or None."""
    try:
        return lookup(name)
    except KeyError:
        return None

from components.passives.rail import Rail

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


@functools.lru_cache(maxsize=None)
def _chip_pin_order(model_name: str) -> tuple[str, ...]:
    """Port names of a chip class, in datasheet pin-number order.

    The deck's X-instance lists nets in this same order, so zipping
    recovers the port→net mapping a renderer was supposed to emit.
    """
    cls = lookup(model_name)
    instance = cls(refdes_number=1)
    return tuple(p.name for p in sorted(instance.pins, key=lambda x: x.id.number))


def _parse_topology(deck: str) -> dict[tuple[str, str], str]:
    """Parse a SPICE deck into {(qualified_refdes, port_name): net_name}.

    Recognises:
      Rn  t1 t2 <ohms>           → (Rn, t1), (Rn, t2)
      Dn  anode cathode <model>  → (Dn, anode), (Dn, cathode)
      <Un> nets... <CHIP_MODEL>  → ports by chip's datasheet pin order
    Skips V_* sources (Rail synthetic id), board X-instances (the
    `_SUBCKT` body's chip lines carry the same nets with port names).
    Tracks enclosing `.SUBCKT <refdes>_SUBCKT` to qualify chips by
    board (`A1.U1`, `A2.U1`), so chip-refdes collisions across boards
    don't merge.
    """
    out: dict[tuple[str, str], str] = {}
    enclosing: str | None = None

    def qualify(refdes: str) -> str:
        return f"{enclosing}.{refdes}" if enclosing else refdes

    for raw in deck.splitlines():
        line = raw.strip()
        if not line or line.startswith('*'):
            continue
        if line.upper().startswith('.SUBCKT'):
            name = line.split()[1]
            if name.endswith('_SUBCKT'):
                enclosing = name[:-len('_SUBCKT')]
            continue
        if line.upper().startswith('.ENDS'):
            enclosing = None
            continue
        if line.startswith('.'):
            continue

        tokens = line.split()
        first = tokens[0]
        if first.startswith('V_') or first == 'V':
            continue
        if first.startswith('X') and tokens[-1].endswith('_SUBCKT'):
            continue   # board instance — redundant with body
        model_cls = _registered_class(tokens[-1])
        if model_cls is not None and issubclass(model_cls, Chip):
            nets = tokens[1:-1]
            for port_name, net in zip(_chip_pin_order(tokens[-1]), nets):
                out[(qualify(first), port_name)] = net
            continue
        if first.startswith('R') and len(tokens) >= 4:
            out[(qualify(first), 't1')] = tokens[1]
            out[(qualify(first), 't2')] = tokens[2]
            continue
        if first.startswith('D') and len(tokens) >= 4:
            out[(qualify(first), 'anode')] = tokens[1]
            out[(qualify(first), 'cathode')] = tokens[2]
            continue
    return out


def _build_expected(design, ctx: ExporterContext) -> dict[tuple[str, str], str]:
    """Walk the design via the same ctx used to render the deck,
    recording `(qualified_refdes, port_name) -> net_name` for every
    refdes-bearing chip/passive. Connectors and Rails emit nothing in
    SPICE so we skip them; cells inside chips are private."""
    expected: dict[tuple[str, str], str] = {}

    def visit(node, prefix: str) -> None:
        if isinstance(node, (Connector, Rail)):
            return
        if isinstance(node, Chip):
            qualified = f"{prefix}.{node.refdes}" if prefix else node.refdes
            for name, port in node.ports.items():
                expected[(qualified, name)] = ctx.net_name(port)
            return
        if isinstance(node, Circuit):
            new_prefix = prefix
            refdes = getattr(node, 'refdes', None)
            if refdes:
                new_prefix = f"{prefix}.{refdes}" if prefix else refdes
            for child in node._factor_nodes:
                visit(child, new_prefix)
            return
        # Leaf passive (Resistor / LED).
        refdes = getattr(node, 'refdes', None)
        if refdes:
            qualified = f"{prefix}.{refdes}" if prefix else refdes
            for name, port in node.ports.items():
                expected[(qualified, name)] = ctx.net_name(port)

    visit(design, "")
    return expected


def _diff(expected: dict, actual: dict) -> str:
    lines: list[str] = []
    for k in sorted(set(expected) | set(actual)):
        e, a = expected.get(k), actual.get(k)
        if e != a:
            lines.append(f"  {k}: expected={e!r}  actual={a!r}")
    return '\n'.join(lines)


@pytest.mark.parametrize("factory", [
    WaterAlarm, WaterAlarmAssembly,
], ids=["WaterAlarm", "WaterAlarmAssembly"])
def test_spice_topology_matches_model(factory):
    design = _silently(factory)
    # Same context for both passes so nc_X synthetic names line up.
    ctx = ExporterContext(design, 'spice',
                          config=ExportConfig(include_header_comment=False))
    deck = spice_render(design, ctx)
    expected = _build_expected(design, ctx)
    actual = _parse_topology(deck)
    assert expected == actual, (
        f"SPICE topology mismatch for {factory.__name__}:\n{_diff(expected, actual)}"
    )
