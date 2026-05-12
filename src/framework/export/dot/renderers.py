"""Per-component DOT node-declaration renderers.

Each renderer returns the `<refdes> [label="..."];` declaration.
Edges are emitted at the net-walker level (see dot/__init__.py).
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.connector import Connector
from framework.diode import Diode
from framework.transistor import Transistor

from framework.export.base import ExporterContext, register_renderer

from components.passives.capacitor import Capacitor
from components.passives.inductor import Inductor
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.relays.spdt import Relay_SPDT


def _dot_label(text: str) -> str:
    """Escape backslashes and quotes for a DOT label string."""
    return text.replace('\\', '\\\\').replace('"', '\\"')


@register_renderer(Resistor, format='dot')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str:
    label = f"{r.refdes}\\n{float(r.ohms):g}Ω"
    return f'{r.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Capacitor, format='dot')
def render_capacitor(c: Capacitor, ctx: ExporterContext) -> str:
    label = f"{c.refdes}\\n{float(c.farads):g}F"
    return f'{c.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Inductor, format='dot')
def render_inductor(l: Inductor, ctx: ExporterContext) -> str:
    label = f"{l.refdes}\\n{float(l.henries):g}H"
    return f'{l.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Relay_SPDT, format='dot')
def render_relay_spdt(k: Relay_SPDT, ctx: ExporterContext) -> str:
    label = f"{k.refdes}\\nRelay_SPDT"
    return f'{k.refdes} [label="{_dot_label(label)}"];'


@register_renderer(LED, format='dot')
def render_led(d: LED, ctx: ExporterContext) -> str:
    label = f"{d.refdes}\\n{d.color} LED"
    return f'{d.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Chip, format='dot')
def render_chip(u: Chip, ctx: ExporterContext) -> str:
    label = f"{u.refdes}\\n{type(u).__name__}"
    return f'{u.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Rail, format='dot')
def render_rail(r: Rail, ctx: ExporterContext) -> str:
    return ""   # rails inlined into vcc/gnd net names


@register_renderer(Board, format='dot')
def render_board(b: Board, ctx: ExporterContext) -> str:
    # Boards become subgraph clusters at the adapter's top level
    # (see dot/__init__.py). No node declaration here.
    return ""


@register_renderer(Connector, format='dot')
def render_connector(j: Connector, ctx: ExporterContext) -> str:
    cls = type(j).__name__
    pin_count = getattr(j, 'pin_count', None)
    if pin_count is not None:
        label = f"{j.refdes}\\n{cls} ({pin_count}p)"
    else:
        label = f"{j.refdes}\\n{cls}"
    return f'{j.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Transistor, format='dot')
def render_transistor(t: Transistor, ctx: ExporterContext) -> str:
    label = f"{t.refdes}\\n{type(t).__name__}"
    return f'{t.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Diode, format='dot')
def render_diode(d: Diode, ctx: ExporterContext) -> str:
    label = f"{d.refdes}\\n{type(d).__name__}"
    return f'{d.refdes} [label="{_dot_label(label)}"];'
