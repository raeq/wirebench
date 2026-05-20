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
from framework.part import Part
from framework.transistor import Transistor

from framework.export.base import ExporterContext, register_renderer

from components.passives.capacitor import Capacitor
from components.passives.cell import Cell
from components.passives.inductor import Inductor
from components.passives.led import LED
from components.passives.ferrite_aerial import FerriteAerial
from components.passives.photoresistor import Photoresistor
from components.passives.variable_capacitor import VariableCapacitor
from components.transducers.antenna import Antenna
from components.transducers.crystal_earpiece import CrystalEarpiece
from components.transducers.earth import Earth
from components.transducers.speaker import Speaker
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.relays.spdt import Relay_SPDT


@register_renderer(Resistor, format='yosys')
def render_resistor(r: Resistor, ctx: ExporterContext) -> str: return ""


@register_renderer(Capacitor, format='yosys')
def render_capacitor(c: Capacitor, ctx: ExporterContext) -> str: return ""


@register_renderer(Inductor, format='yosys')
def render_inductor(l: Inductor, ctx: ExporterContext) -> str: return ""


@register_renderer(Photoresistor, format='yosys')
def render_photoresistor(p: Photoresistor, ctx: ExporterContext) -> str: return ""


@register_renderer(Speaker, format='yosys')
def render_speaker(s: Speaker, ctx: ExporterContext) -> str: return ""


@register_renderer(CrystalEarpiece, format='yosys')
def render_crystal_earpiece(e: CrystalEarpiece, ctx: ExporterContext) -> str: return ""


@register_renderer(VariableCapacitor, format='yosys')
def render_variable_capacitor(vc: VariableCapacitor, ctx: ExporterContext) -> str: return ""


@register_renderer(FerriteAerial, format='yosys')
def render_ferrite_aerial(fa: FerriteAerial, ctx: ExporterContext) -> str: return ""


@register_renderer(Antenna, format='yosys')
def render_antenna(a: Antenna, ctx: ExporterContext) -> str: return ""


@register_renderer(Earth, format='yosys')
def render_earth(e: Earth, ctx: ExporterContext) -> str: return ""


@register_renderer(Relay_SPDT, format='yosys')
def render_relay_spdt(k: Relay_SPDT, ctx: ExporterContext) -> str: return ""


@register_renderer(LED, format='yosys')
def render_led(d: LED, ctx: ExporterContext) -> str: return ""


@register_renderer(Rail, format='yosys')
def render_rail(r: Rail, ctx: ExporterContext) -> str: return ""


@register_renderer(Cell, format='yosys')
def render_cell(bt: Cell, ctx: ExporterContext) -> str: return ""


@register_renderer(Chip, format='yosys')
def render_chip(u: Chip, ctx: ExporterContext) -> str: return ""


@register_renderer(Connector, format='yosys')
def render_connector(j: Connector, ctx: ExporterContext) -> str: return ""


@register_renderer(Board, format='yosys')
def render_board(b: Board, ctx: ExporterContext) -> str: return ""


@register_renderer(Transistor, format='yosys')
def render_transistor(t: Transistor, ctx: ExporterContext) -> str: return ""


@register_renderer(Diode, format='yosys')
def render_diode(d: Diode, ctx: ExporterContext) -> str: return ""


@register_renderer(Part, format='yosys')
def render_part(fn: Part, ctx: ExporterContext) -> str: return ""
