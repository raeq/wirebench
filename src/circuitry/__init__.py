"""Flat import surface for the circuitry framework.

A convenience module that re-exports the most commonly used names so
demos and scripts can avoid the deep `framework.x.y` / `components.x.y`
paths.  Every name here is also available under its canonical path,
which exporters and tooling still use.

    from circuitry import Circuit, wire, LED, Rail, Resistor
    from circuitry import ATmega328P, NE555, CD4017
    from circuitry import D1N4148, Q2N3904
    from circuitry import run_scenarios

Concept cells (internal chip-implementation primitives) are
deliberately not re-exported — reach for them under
`components.chips.concepts.<name>` when you actually need to peek
past the chip boundary.  Connectors are also kept under their full
path because the library is large and their use is less common in
hand-coded demos.
"""
# Framework primitives.
from framework.board import Board
from framework.chip import Chip
from framework.circuit import Circuit
from framework.connector import Connector, declare_mating_pair
from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.mate import mate
from framework.pin import Pin, PinId
from framework.port import Port, Direction
from framework.refdes import RefdesBearing, RefdesNumber, validate_refdes
from framework.signals import Analog, Digital
from framework.wire import wire

# Every component category re-exported here so users can write
# `from circuitry import LED, Resistor, ATmega328P, NE555` without
# remembering which subpackage the part lives in.
from components.chips       import *     # noqa: F401, F403
from components.diodes      import *     # noqa: F401, F403
from components.passives    import *     # noqa: F401, F403
from components.relays      import *     # noqa: F401, F403
from components.transistors import *     # noqa: F401, F403

# Scenario runner — shared boilerplate for the demos' `_main()`.
from .scenarios import run_scenarios, print_bom

# Re-export name lists so downstream tooling can introspect what
# `from circuitry import *` covers.  We don't union the sub-package
# __all__ explicitly because importing them already populates this
# module's namespace; spell out only the framework-level public names
# plus the scenario helpers.
__all__ = [
    'Analog', 'Digital',
    'Board', 'Chip', 'Circuit', 'Connector', 'FactorNode', 'Pin', 'PinId',
    'Port', 'Direction',
    'GroundDomain', 'ELECTRICAL',
    'RefdesBearing', 'RefdesNumber', 'validate_refdes',
    'declare_mating_pair', 'mate', 'wire',
    'print_bom', 'run_scenarios',
]
