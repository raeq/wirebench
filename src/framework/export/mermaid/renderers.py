"""Per-component Mermaid node-declaration renderers."""
from __future__ import annotations

from framework.chip import Chip
from framework.connector import Connector

from framework.export.base import ExporterContext, register_renderer

from components.passives.led import LED
from components.passives.resistor import Resistor


def _mm_label(text: str) -> str:
    """Mermaid labels: quote the entire string and escape `"`."""
    return text.replace('"', '&quot;')


@register_renderer(Resistor, format='mermaid')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    label = f"{r.refdes}<br/>{float(r.ohms):g}Ω"
    return f'{r.refdes}["{_mm_label(label)}"]'


@register_renderer(LED, format='mermaid')
def render_led(d: LED, ctx: ExporterContext) -> str:
    label = f"{d.refdes}<br/>{d.color} LED"
    return f'{d.refdes}["{_mm_label(label)}"]'


@register_renderer(Chip, format='mermaid')
def render_chip(u: Chip, ctx: ExporterContext) -> str:
    label = f"{u.refdes}<br/>{type(u).__name__}"
    return f'{u.refdes}["{_mm_label(label)}"]'


@register_renderer(Connector, format='mermaid')
def render_connector(j: Connector, ctx: ExporterContext) -> str:
    # Connectors are conductors and emit nothing in netlist-style
    # exports. Keep a stub for MRO coverage but return empty.
    return ""
