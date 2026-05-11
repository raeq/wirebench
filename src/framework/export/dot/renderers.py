"""Per-component DOT node-declaration renderers.

Each renderer returns the `<refdes> [label="..."];` declaration.
Edges are emitted at the net-walker level (see dot/__init__.py).
"""
from __future__ import annotations

from framework.chip import Chip
from framework.connector import Connector

from framework.export.base import ExporterContext, register_renderer

from components.passives.led import LED
from components.passives.resistor import Resistor


def _dot_label(text: str) -> str:
    """Escape backslashes and quotes for a DOT label string."""
    return text.replace('\\', '\\\\').replace('"', '\\"')


@register_renderer(Resistor, format='dot')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    label = f"{r.refdes}\\n{float(r.ohms):g}Ω"
    return f'{r.refdes} [label="{_dot_label(label)}"];'


@register_renderer(LED, format='dot')
def render_led(d: LED, ctx: ExporterContext) -> str:
    label = f"{d.refdes}\\n{d.color} LED"
    return f'{d.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Chip, format='dot')
def render_chip(u: Chip, ctx: ExporterContext) -> str:
    label = f"{u.refdes}\\n{type(u).__name__}"
    return f'{u.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Connector, format='dot')
def render_connector(j: Connector, ctx: ExporterContext) -> str:
    cls = type(j).__name__
    pin_count = getattr(j, 'pin_count', None)
    if pin_count is not None:
        label = f"{j.refdes}\\n{cls} ({pin_count}p)"
    else:
        label = f"{j.refdes}\\n{cls}"
    return f'{j.refdes} [label="{_dot_label(label)}"];'
