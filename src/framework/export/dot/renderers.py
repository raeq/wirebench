"""Per-component DOT node-declaration renderers.

Each renderer returns the `<refdes> [label="..."];` declaration.
Edges are emitted at the net-walker level (see dot/__init__.py).
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


@register_renderer(Photoresistor, format='dot')
def render_photoresistor(p: Photoresistor, ctx: ExporterContext) -> str:
    label = f"{p.refdes}\\nLDR"
    return f'{p.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Speaker, format='dot')
def render_speaker(s: Speaker, ctx: ExporterContext) -> str:
    label = f"{s.refdes}\\n{float(s.impedance_ohms):g}Ω"
    return f'{s.refdes} [label="{_dot_label(label)}"];'


@register_renderer(CrystalEarpiece, format='dot')
def render_crystal_earpiece(e: CrystalEarpiece, ctx: ExporterContext) -> str:
    label = f"{e.refdes}\\ncrystal"
    return f'{e.refdes} [label="{_dot_label(label)}"];'


@register_renderer(VariableCapacitor, format='dot')
def render_variable_capacitor(vc: VariableCapacitor, ctx: ExporterContext) -> str:
    label = f"{vc.refdes}\\n{float(vc.min_farads):g}–{float(vc.max_farads):g}F"
    return f'{vc.refdes} [label="{_dot_label(label)}"];'


@register_renderer(FerriteAerial, format='dot')
def render_ferrite_aerial(fa: FerriteAerial, ctx: ExporterContext) -> str:
    label = f"{fa.refdes}\\n{float(fa.henries):g}H aerial"
    return f'{fa.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Antenna, format='dot')
def render_antenna(a: Antenna, ctx: ExporterContext) -> str:
    label = f"{a.refdes}\\nAntenna"
    return f'{a.refdes} [label="{_dot_label(label)}"];'


@register_renderer(Earth, format='dot')
def render_earth(e: Earth, ctx: ExporterContext) -> str:
    label = f"{e.refdes}\\nEarth"
    return f'{e.refdes} [label="{_dot_label(label)}"];'


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


@register_renderer(Cell, format='dot')
def render_cell(bt: Cell, ctx: ExporterContext) -> str:
    label = f"{bt.refdes}\\nLi-Ion 1S"
    return f'{bt.refdes} [label="{_dot_label(label)}"];'


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


@register_renderer(Part, format='dot')
def render_part(fn: Part, ctx: ExporterContext) -> str:
    return ""   # concept / firmware-stand-in cells; not graph nodes
