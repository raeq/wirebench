# circuitbench

A Python framework for modelling real electronic circuits with **physical
fidelity**. Every class corresponds to a physical thing — a resistor, an LED,
a chip — and the code respects the constraints of the physical world. If you
couldn't do it with a soldering iron, you can't do it in code.

## Why

Most circuit simulators are built around mathematics first and pin layouts
second. This project goes the other way: a `CD4043` exposes exactly its 16
package pins, internally composes the four NOR latches and eight tri-state
buffers that real silicon contains, and the OE pin really is one wire fanned
out to all eight buffer enables. The model lies as little as possible.

## Architecture

The framework is built around three primitives:

- **`Port`** — a typed connection point on a component. Every port carries a
  direction (IN/OUT/BIDIR), a signal type (`Digital` or `Analog` subtype), and
  a ground-domain reference.
- **`Pin`** — a chip pin, modelled as a bonded-wire relay between an external
  face (what consumers wire to) and an internal face (what cells inside the
  chip wire to). Provides total encapsulation: a chip's port surface is
  exactly its package pins.
- **`Circuit`** / **`Chip`** — composite factor nodes whose evaluation order
  is derived from the topological sort of the internal wire graph.

A real chip is a `Chip` subclass that composes private cells (`NORLatch`,
`TriStateBuffer`, `Comparator`, `Inverter`, `DarlingtonChannel`) routed
through `Pin` objects. Consumers see only the package pins; the silicon
inside is private.

```
Resistor, LED, Rail, …  ←── passives (real things you'd buy)
CD4043, LM393, …        ←── chips    (real ICs you'd buy)
NORLatch, Comparator, … ←── concepts (silicon cells inside chips; private)
```

## Usage

```python
from components import CD4043, LED, Rail
from framework.wire import wire

latch = CD4043()
red   = LED('red')
vcc   = Rail(True)

wire(vcc.ports['out'], latch.ports['oe'])     # OE must be tied — no pull-up
wire(latch.ports['q_1'], red.ports['anode'])

latch(s_1=True, r_1=False, oe=True)           # set
assert red.lit is True
```

A complete worked example — a water-level alarm composed from a ULN2003A,
SN74HC04, CD4043, two LEDs, and Vcc/GND rails — lives in
`src/applications/water_alarm.py`.

## Design principles

The full design rationale lives in `docs/modelling-architecture.md`. The
short version:

- **Components are functors.** Every component is callable; `__call__` is its
  signal interface. There are no setters, no mutator methods, and no public
  attributes that can change state from outside.
- **Encapsulation is total.** A chip's external surface is its pins. Internal
  cells are not part of the API and live under
  `components.chips.concepts/`, which doesn't re-export anything.
- **Invalid hardware states raise.** S=R=1 on an SR latch raises
  `ValueError`; you can't paper it over.
- **Wired or called, not both.** A chip with a wired input pin refuses
  `__call__` (would silently overwrite the parent's signal). Cells inside
  chips are likewise guarded.
- **No magic conveniences.** If real silicon doesn't have an integrated
  pull-up, the model doesn't either — tie the pin explicitly.

## Install

Requires Python 3.10+. Install with `uv` (recommended) or `pip`:

```bash
uv venv && uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Licensing

This project is released under the [PolyForm Noncommercial License
1.0.0](LICENSE) — free for non-commercial use, including personal study,
hobby projects, academic research, and use by educational, charitable, or
public institutions.

**Commercial use requires a separate paid license.** Contact the project
maintainer to obtain commercial-use rights.
