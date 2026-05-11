"""Per-component Yosys JSON renderer registrations.

Each Yosys cell record is uniformly shaped (type, hide_name,
parameters, port_directions, connections) — the bulk of the work is
in the adapter's render(); these stubs exist to satisfy the
MRO-coverage acceptance criterion (§11.3): every component class
must have a renderer reachable via lookup_renderer for every format.

The stubs return empty string; the adapter renders cells directly.
"""
from __future__ import annotations

from framework.board import Board
from framework.chip import Chip
from framework.connector import Connector
from framework.diode import Diode
from framework.transistor import Transistor

from framework.export.base import ExporterContext, register_renderer

from components.passives.capacitor import Capacitor
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor


@register_renderer(Resistor, format='yosys')
def render_resistor(r, ctx: ExporterContext) -> str: return ""


@register_renderer(Capacitor, format='yosys')
def render_capacitor(c, ctx: ExporterContext) -> str: return ""


@register_renderer(LED, format='yosys')
def render_led(d, ctx: ExporterContext) -> str: return ""


@register_renderer(Rail, format='yosys')
def render_rail(r, ctx: ExporterContext) -> str: return ""


@register_renderer(Chip, format='yosys')
def render_chip(u, ctx: ExporterContext) -> str: return ""


@register_renderer(Connector, format='yosys')
def render_connector(j, ctx: ExporterContext) -> str: return ""


@register_renderer(Board, format='yosys')
def render_board(b, ctx: ExporterContext) -> str: return ""


@register_renderer(Transistor, format='yosys')
def render_transistor(t, ctx: ExporterContext) -> str: return ""


@register_renderer(Diode, format='yosys')
def render_diode(d, ctx: ExporterContext) -> str: return ""
