"""Per-component BOM CSV renderers.

Each renderer returns a single CSV line:
    Refdes,Value,Footprint,Quantity,Parent,Description

Renderers take `(component, ctx, parent_refdes)` — the extra parent
argument is BOM-specific (the spec adds a Parent column tying each row
to its enclosing board).
"""
from __future__ import annotations

import csv
import io

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
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.relays.spdt import Relay_SPDT


def _csv_row(*fields: str) -> str:
    """CSV-escape `fields` and return one line. Handles commas, quotes,
    newlines uniformly via the stdlib writer."""
    buf = io.StringIO()
    csv.writer(buf, lineterminator='').writerow(fields)
    return buf.getvalue()


def _footprint_of(comp: Part) -> str:
    fp = getattr(comp, 'FOOTPRINT', None)
    return fp if fp is not None else ''


@register_renderer(Resistor, format='bom')
def render_resistor(r: Resistor, ctx: ExporterContext, parent: str = '') -> str:
    value = f"{float(r.ohms):g}Ω"
    return _csv_row(r.refdes, value, _footprint_of(r), '1', parent, 'Resistor')


@register_renderer(Capacitor, format='bom')
def render_capacitor(c: Capacitor, ctx: ExporterContext, parent: str = '') -> str:
    value = f"{float(c.farads):g}F"
    return _csv_row(c.refdes, value, _footprint_of(c), '1', parent, 'Capacitor')


@register_renderer(Inductor, format='bom')
def render_inductor(l: Inductor, ctx: ExporterContext, parent: str = '') -> str:
    value = f"{float(l.henries):g}H"
    return _csv_row(l.refdes, value, _footprint_of(l), '1', parent, 'Inductor')


@register_renderer(Relay_SPDT, format='bom')
def render_relay_spdt(k: Relay_SPDT, ctx: ExporterContext, parent: str = '') -> str:
    value = f"SPDT @ {float(k.pickup_voltage):g}V"
    return _csv_row(k.refdes, value, _footprint_of(k), '1', parent, 'Relay (SPDT)')


@register_renderer(LED, format='bom')
def render_led(d: LED, ctx: ExporterContext, parent: str = '') -> str:
    value = f"{d.color} LED"
    return _csv_row(d.refdes, value, _footprint_of(d), '1', parent,
                    'Light-emitting diode')


@register_renderer(Chip, format='bom')
def render_chip(u: Chip, ctx: ExporterContext, parent: str = '') -> str:
    return _csv_row(u.refdes, type(u).__name__, _footprint_of(u), '1', parent,
                    type(u).__name__)


@register_renderer(Connector, format='bom')
def render_connector(j: Connector, ctx: ExporterContext, parent: str = '') -> str:
    # Connectors are real parts and belong on the BOM.
    value = type(j).__name__
    # Parameterised families: include pin_count for clarity.
    pin_count = getattr(j, 'pin_count', None)
    if pin_count is not None and 'Header' in value:
        value = f"{value}_{pin_count}"
    return _csv_row(j.refdes, value, _footprint_of(j), '1', parent,
                    type(j).__name__)


@register_renderer(Board, format='bom')
def render_board(b: Board, ctx: ExporterContext, parent: str = '') -> str:
    value = f"{b.name} Rev {b.revision}"
    return _csv_row(b.refdes, value, '', '1', parent, 'Printed circuit board')


@register_renderer(Rail, format='bom')
def render_rail(r: Rail, ctx: ExporterContext, parent: str = '') -> str:
    # Rails are logical markers, not procurable parts — empty row.
    return ""


@register_renderer(Cell, format='bom')
def render_cell(bt: Cell, ctx: ExporterContext, parent: str = '') -> str:
    value = f"Li-Ion 1S @ {bt.state_of_charge * 100:.0f}% SoC"
    return _csv_row(bt.refdes, value, _footprint_of(bt), '1', parent,
                    'Battery cell')


@register_renderer(Transistor, format='bom')
def render_transistor(t: Transistor, ctx: ExporterContext, parent: str = '') -> str:
    cls = type(t).__name__
    return _csv_row(t.refdes, cls, _footprint_of(t), '1', parent, cls)


@register_renderer(Diode, format='bom')
def render_diode(d: Diode, ctx: ExporterContext, parent: str = '') -> str:
    cls = type(d).__name__
    return _csv_row(d.refdes, cls, _footprint_of(d), '1', parent, cls)


@register_renderer(Part, format='bom')
def render_part(fn: Part, ctx: ExporterContext, parent: str = '') -> str:
    # Catch-all for concept cells / firmware-stand-in cells that are
    # registered for save/load but don't correspond to a placeable
    # part.  More-specific renderers above always win via MRO.
    return ""
