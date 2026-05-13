"""5 V breadboard rail power supply — from a 3× CR2032 coin-cell stack.

A small, no-soldering, reusable "hat" for delivering a regulated 5 V
rail to a breadboard from cheap, ubiquitous coin cells. Intended as
one of the first projects a beginner can build, with the green LED
itself serving as the test:

    Build the circuit. Install the cells. Plug in the switch jumper.
    If D3 lights green, the supply works. If not, troubleshoot —
    one of the links in the chain is broken.

That's the whole verification surface. D3 exercises every step of the
supply: cells must be present and oriented correctly, the
reverse-protection diode must point the right way, the regulator must
be alive, and the output must be in range. If any link fails, D3
stays dark.

User interface — affordance and feedback
----------------------------------------
The design is also a complete UI loop, applying standard interaction
principles to a hardware module:

* **Affordance** comes from SW1, a 1x2 header sticking visibly out of
  the breadboard. The builder *sees* there's an interactable element
  — somewhere to plug a jumper — without needing to read the
  schematic. The header invites interaction by its physical shape.
* **Feedback** comes from D3, the green power-good LED. Install the
  jumper across SW1 → D3 lights green → the supply is up. Pull the
  jumper → D3 goes dark → the supply is off and safe to handle.

Switch as input, LED as output. The two together form the closed
interaction loop every well-designed control surface has —
discoverable input plus immediate visible output. The builder always
knows the state of the supply at a glance, and changing that state is
a single deliberate physical action.

Design intent — fail-safe by construction
-----------------------------------------
The supply is built to fail in exactly two ways:

    1. Deliver a regulated 5 V to the breadboard's + rail, or
    2. Deliver no output at all (D3 dark).

It is **never** designed to deliver wrong-polarity power, over-voltage,
or out-of-range bad power that could damage downstream parts. The
fail-mode analysis:

* **Reverse polarity** on the battery stack is blocked by D1, a Schottky
  diode in series with the input. If a cell is inserted backwards (or
  the holder is mis-wired), D1 refuses to conduct. The regulator never
  powers up. D3 stays dark — and a dark LED tells the builder to check
  battery orientation before anything bad happens.

* **Regulator failure (short)** is clamped by D2, a 5.1 V Zener
  crowbar across the output. The classic 78-series failure mode passes
  the input straight through to the output, which would normally put
  the unregulated 8-9 V stack voltage on downstream parts rated for
  5 V. D2 conducts heavily at any voltage above ~5.1 V, holding the
  output rail down until either D2 or the battery stack gives up.
  Downstream parts see at most 5.1 V regardless.

* **Cells discharged** is handled by the regulator's natural dropout
  behaviour: as the stack voltage falls below ~7.3 V, U1 can no longer
  maintain 5 V output, and the rail sags. D3 dims visibly before
  going dark altogether. This isn't damaging (most TTL/CMOS parts
  tolerate 3.3-5 V supply), and the dimming LED is the builder's cue
  to swap the cells.

* **Output short-circuit** is current-limited by the CR2032 chemistry
  itself. Three coin cells in series can deliver at most ~10 mA peak
  before the voltage collapses; sustained shorts heat the cells (which
  is a real but limited hazard — see GOTCHAS on the CR2032Stack class)
  and exhaust them, but nothing downstream is damaged by the supply.

BOM
---
    BT1   3× CR2032 stack    Lithium primary, 3 V each, in series (9 V nominal)
    SW1   1x2 pin header     Power on/off — jumper across pins to close
    D1    1N5817 Schottky    Input reverse-polarity protection (0.3 V Vf)
    C1    100 nF ceramic     Input decoupling at the regulator
    U1    LM7805 (TO-220)    +5 V fixed positive linear regulator
    C2    10 µF electrolytic Output bulk capacitance / stability
    D2    1N4733A (Zener)    5.1 V crowbar across the output
    R1    470 Ω              D3 current limit (6 mA @ 5 V supply)
    D3    Green LED          Power-good indicator — *the test surface*

Eight signal-path parts plus three coin cells in their holder. All
through-hole, all breadboard-friendly, all in any starter parts kit.

Topology
--------

::

    BT1.pos ── SW1 ── [D1 anode→cathode] ─┬─ [U1.IN]
                                          │
                                          C1
                                          │
                                          GND

                                              [U1.OUT] ─┬─ + 5 V rail (to breadboard)
                                                        │
                                              C2 ───────┤
                                                        │
                                                        ├─ [D2 cathode]       ← Zener crowbar:
                                                        │  [D2 anode] ── GND     reverse-biased,
                                                        │                        conducts at >5.1 V
                                                        │
                                                        └─ [R1] ── [D3 anode] ── [D3 cathode] ── GND

    BT1.neg ─────────────────────────────────────────────────────────────────── GND

C1 and C2 decouple the regulator at input and output respectively;
their second terminals tie to GND.

Current capability — honest limits
----------------------------------
CR2032 chemistry caps continuous current at about 3 mA per cell.
Three in series do **not** raise the current capability — they raise
the voltage. The rail can comfortably power:

* A 555 timer plus a handful of CMOS gates
* One or two low-current LEDs (10 mA each pushes the limit)
* A microcontroller running at low clock with peripherals off
* Static test rigs and probe wiring

It **cannot** power:

* An Arduino at full clock (~20-50 mA draw — too much for coin cells)
* A relay coil
* A motor (even a tiny one)
* A backlit LCD

For higher-current projects, swap BT1 for 4× AA cells in series
(6 V nominal feeding the LM7805's 7 V minimum input — works at full
charge but drops out earlier). The topology stays identical; only the
battery holder changes.

Run directly to see a discharge trace from fresh cells to dead:

    python demos/5v_rail_power/five_volt_rail_power.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, ClassVar

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import Field, validate_call

from circuitry import (
    Circuit, FactorNode,
    Direction, Port,
    GroundDomain, ELECTRICAL,
    RefdesNumber, validate_refdes,
    Analog, wire,
    Resistor, LED, Capacitor,
    LM7805,
    D1N5817, D1N4733A,
    run_scenarios,
)
from components.chips.concepts.series_rectifier import SeriesRectifier
from components.connectors.headers import Header1xNMale
from framework.errors import PartParameterError
from framework.registry import register


# ---------------------------------------------------------------------------
# CR2032 discharge curve
# ---------------------------------------------------------------------------

# Lithium-MnO2 primary chemistry has a flat plateau at ~3.0 V for most
# of its useful life, then a sharp knee near depletion. Five anchor
# points approximate the curve well enough for status-trace purposes.
# Voltages are typical at light load (≤ 1 mA), at room temperature.
_CR2032_OCV_CURVE: tuple[tuple[float, float], ...] = (
    (0.00, 2.00),   # exhausted — well past useful life
    (0.05, 2.40),   # last-gasp knee
    (0.20, 2.70),
    (0.80, 2.95),   # plateau across the bulk of the discharge
    (1.00, 3.00),   # fresh out of the package
)


def _cr2032_ocv_from_soc(soc: float) -> float:
    """Open-circuit voltage of a single CR2032 cell at the given SoC.

    Linearly interpolates between the five anchor points of the
    discharge curve. SoC is clamped to [0, 1] — a real cell can't be
    fuller than full or emptier than empty.
    """
    soc = max(0.0, min(1.0, soc))
    for (soc_lo, v_lo), (soc_hi, v_hi) in zip(_CR2032_OCV_CURVE,
                                              _CR2032_OCV_CURVE[1:]):
        if soc <= soc_hi:
            span = soc_hi - soc_lo
            if span == 0.0:
                return v_lo
            fraction = (soc - soc_lo) / span
            return v_lo + fraction * (v_hi - v_lo)
    return _CR2032_OCV_CURVE[-1][1]


# ---------------------------------------------------------------------------
# CR2032 stack as a single FactorNode
# ---------------------------------------------------------------------------

@register('CR2032Stack')
class CR2032Stack(FactorNode):
    """A stack of three CR2032 lithium coin cells in series.

    Modelled as a single FactorNode rather than three independent
    `Cell` instances. The framework's voltage-only ports treat each
    Cell's `neg` terminal as driven-to-0 V — naively stacking three
    Cells in series produces three drivers all claiming 0 V on
    different absolute potentials, which the framework would
    (correctly) flag as a short circuit. Representing the stack as
    one component matches the physical BOM (one battery holder with
    three cells in series is one product) and gives the framework a
    single, consistent driver pair.

    Ports
    -----
        pos   Analog OUT — top of the stack. Driven to 3 × OCV(SoC).
        neg   Analog OUT — bottom of the stack. Driven to 0 V.

    Python state
    ------------
        state_of_charge   0.0..1.0; settable so scenarios can walk
                          the stack from fresh to exhausted.
    """

    __slots__ = ('_ports', '_state_of_charge', '_refdes_number')

    REFDES_PREFIX: ClassVar[str] = 'BT'
    FOOTPRINT: ClassVar[str | None] = (
        # Three Keystone 3001 single-CR2032 holders in series.
        # A KiCad netlist consumer should expand this to three real
        # footprints; we declare the through-hole holder so KiCad's
        # ERC accepts the part. The assembly guide will document the
        # three-cell physical arrangement.
        "Battery:BatteryHolder_Keystone_3001_1x12mm"
    )
    PIN_NUMBERS: ClassVar[dict[str, int]] = {'pos': 1, 'neg': 2}

    CELL_COUNT: ClassVar[int] = 3
    NOMINAL_V_PER_CELL: ClassVar[float] = 3.0

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Three coin cells stacked in series carry 9 V at hundreds of "
        "milliamps short-circuit current.** A dropped paperclip across the "
        "stack will weld itself to the cells, ignite, and start a fire. "
        "Install the batteries last, after the rest of the circuit is "
        "built and the switch jumper is *not* installed.",
        "**CR2032 cells are non-rechargeable.** Don't try to charge them — "
        "they vent and can rupture. If a cell gets warm during use, "
        "remove it immediately and dispose of it at a battery-recycling "
        "drop-off (most hardware stores have one).",
        "**Polarity is counter-intuitive on coin cells.** The flat side "
        "with the engraved markings (`CR2032`, `+`, manufacturer logo) is "
        "the **positive** terminal. The smooth metal cup on the back is "
        "**negative**. Most coin-cell holders are marked with `+` on the "
        "contact that touches the flat marked face. Always verify with a "
        "multimeter on a known-good cell before powering up.",
        "**Series cells need to match.** Use three fresh cells from the "
        "same package. Mixing a fresh cell with two depleted ones makes "
        "the depleted ones charge in reverse, which is unsafe for primary "
        "cells.",
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        initial_state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._state_of_charge: float = float(initial_state_of_charge)
        self._ports = {
            'pos': Port('pos', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
            'neg': Port('neg', Direction.OUT, domain,
                        mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def state_of_charge(self) -> float:
        return self._state_of_charge

    @state_of_charge.setter
    def state_of_charge(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise PartParameterError(
                f"state_of_charge must be in [0, 1]; got {value!r}"
            )
        self._state_of_charge = float(value)

    @property
    def cell_voltage(self) -> float:
        """OCV of a single cell at the current state of charge."""
        return _cr2032_ocv_from_soc(self._state_of_charge)

    @property
    def stack_voltage(self) -> float:
        """OCV of the full stack — CELL_COUNT × single-cell voltage."""
        return self.CELL_COUNT * self.cell_voltage

    def evaluate(self) -> None:
        self._ports['pos'].drive(self.stack_voltage)
        self._ports['neg'].drive(0.0)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)] | None = None,
    ) -> float:
        """Standalone-test invocation: optionally set a new SoC,
        evaluate, and return the resulting stack voltage."""
        self._assert_no_inputs_wired()
        if state_of_charge is not None:
            self.state_of_charge = state_of_charge
        self.evaluate()
        return self.stack_voltage

    def __repr__(self) -> str:
        return (f"CR2032Stack(cells={self.CELL_COUNT}, "
                f"soc={self._state_of_charge:.2f}, "
                f"V={self.stack_voltage:.2f}, "
                f"refdes={self.refdes!r})")


# ---------------------------------------------------------------------------
# The supply circuit itself
# ---------------------------------------------------------------------------

class FiveVoltRailPower(Circuit):
    """5 V breadboard rail supply from a 3× CR2032 stack.

    The green LED D3 is the test surface. If D3 lights, every link
    in the supply chain is intact. See the module docstring for the
    fail-mode analysis.

    Output: U1.OUTPUT (= node also driving D3, R1, C2.t1, D2.cathode).
    Wire this to your breadboard's `+` rail and U1.GND to its `-` rail.
    """

    # LM7805 conservative dropout — the datasheet quotes 2.0 V at the
    # rated 1 A current. At the very low currents this supply runs
    # (~10 mA), real dropout is closer to 1.5 V; we use 2.0 V as a
    # design margin so the simulator's predictions match the worst
    # case the user will actually see.
    _LM7805_DROPOUT_V: ClassVar[float] = 2.0

    # 1N5817 Schottky forward drop at < 100 mA load.
    _SCHOTTKY_VF: ClassVar[float] = 0.3

    # D3 green LED forward drop (typical at 5-10 mA).
    _LED_VF: ClassVar[float] = 2.0

    # R1 current-limit resistor value.
    _R1_OHMS: ClassVar[float] = 470.0

    def __init__(self) -> None:
        # --- Battery stack ------------------------------------------------
        self.bt1 = CR2032Stack(refdes_number=1)

        # --- Power switch (1x2 header; user installs a jumper to close) --
        # The user plugs a jumper across pins 1 and 2 to close the switch.
        # In the framework topology we model the jumper as a wire across
        # the externals — the assumed normal operating state. Removing
        # the physical jumper turns the supply off; the framework doesn't
        # simulate that, but the assembly guide explains how to use it.
        self.sw1 = Header1xNMale(pin_count=2, pitch_mm=2.54, refdes_number=1)

        # --- Reverse-polarity protection ---------------------------------
        # The physical 1N5817 sits in series between the switch and
        # the regulator input — it appears on the BOM, the netlist,
        # and the assembly guide.  The diode itself is Category A
        # passive: its directional behaviour is a property of the
        # role it plays in this circuit, not of the part.  The `SeriesRectifier`
        # cell models that role — it drives the cathode-side net
        # from the anode side minus 0.3 V (the Schottky forward
        # drop) so the framework's ERC walker sees a real driver on
        # the regulator-input net.
        self.d1 = D1N5817(refdes_number=1)
        self.d1_rectifier = SeriesRectifier(v_f=0.3)

        # --- Regulator and decoupling ------------------------------------
        self.c1 = Capacitor(100e-9, refdes_number=1)   # 100 nF input decoupling
        self.u1 = LM7805(refdes_number=1)
        self.c2 = Capacitor(10e-6, refdes_number=2)    # 10 µF output bulk

        # --- Output crowbar Zener ----------------------------------------
        self.d2 = D1N4733A(refdes_number=2)            # 5.1 V Zener clamp

        # --- The test surface: power-good LED ----------------------------
        self.r1 = Resistor(self._R1_OHMS, refdes_number=1)
        self.d3 = LED('green', refdes_number=3)

        # ---- Wiring ------------------------------------------------------
        # Switch jumper (assumed installed = closed):
        wire(self.sw1.pins[0].external, self.sw1.pins[1].external)

        # Battery → switch → reverse diode → regulator input.
        # The SeriesRectifier cell joins the same two nets the
        # passive diode joins — input on the anode side, output on
        # the cathode side — so ERC sees a driver propagating the
        # battery voltage through to the regulator input net.
        wire(self.bt1.pos, self.sw1.pins[0].internal)
        wire(self.sw1.pins[1].internal,
             self.d1.anode,
             self.d1_rectifier.ports['input'])
        wire(self.d1.cathode,
             self.d1_rectifier.ports['output'],
             self.c1.t1,
             self.u1.INPUT)

        # Ground (battery negative, both cap negatives, regulator GND,
        # Zener anode, LED cathode all tied to a single GND net)
        wire(self.bt1.neg,
             self.c1.t2,
             self.u1.GND,
             self.c2.t2,
             self.d2.anode,
             self.d3.cathode)

        # Regulator output → output cap → crowbar Zener cathode (clamps
        # at 5.1 V if regulator fails short) → LED branch
        wire(self.u1.OUTPUT,
             self.c2.t1,
             self.d2.cathode,        # reverse-biased; conducts only above ~5.1 V
             self.r1.t1)
        wire(self.r1.t2, self.d3.anode)

        # No external surface ports — this circuit IS the supply.
        # Consumers tap onto the +5 V rail via a jumper from u1.OUTPUT to
        # the breadboard's `+` rail, and from u1.GND to the breadboard's
        # `-` rail. Modelling those jumpers in the framework would make
        # the supply specific to one downstream consumer; leaving them
        # out keeps the hat reusable.
        super().__init__()

    # --- Behavioural model (Python-side; not framework-evaluated) ----------

    @property
    def stack_voltage(self) -> float:
        """The battery stack's OCV at the current state of charge."""
        return self.bt1.stack_voltage

    @property
    def regulator_input_voltage(self) -> float:
        """Voltage at U1.INPUT — stack voltage minus the Schottky drop."""
        return max(0.0, self.stack_voltage - self._SCHOTTKY_VF)

    @property
    def rail_voltage(self) -> float:
        """The 5 V rail voltage, given the current battery state of charge.

        Models the LM7805's dropout behaviour:
          - Input ≥ 7.0 V: output clamped at 5.0 V (regulated).
          - Input below dropout: output tracks input minus dropout.
          - Input below ~2.0 V: output effectively 0.
        """
        v_in = self.regulator_input_voltage
        v_out_unclamped = v_in - self._LM7805_DROPOUT_V
        return max(0.0, min(5.0, v_out_unclamped))

    @property
    def led_current_ma(self) -> float:
        """Predicted current through D3 (and therefore its brightness)."""
        v_across_r1 = max(0.0, self.rail_voltage - self._LED_VF)
        return (v_across_r1 / self._R1_OHMS) * 1000.0  # to mA

    @property
    def led_state(self) -> str:
        """A human-readable state of D3 — what the builder sees at the
        bench. The whole TDD framing of the design rests on this:
        `'on'` means the supply works; `'off'` means it doesn't."""
        i_ma = self.led_current_ma
        if i_ma < 0.5:
            return 'off'
        elif i_ma < 2.0:
            return 'dim'
        else:
            return 'on'

    # --- Test surface ------------------------------------------------------

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)],
    ) -> float:
        """Set the battery stack's state of charge and return the
        resulting 5 V rail voltage. The LED state is observable via
        `circuit.led_state`."""
        self.bt1.state_of_charge = state_of_charge
        return self.rail_voltage

    def __repr__(self) -> str:
        return (f"FiveVoltRailPower("
                f"soc={self.bt1.state_of_charge:.0%}, "
                f"V_stack={self.stack_voltage:.2f}, "
                f"V_rail={self.rail_voltage:.2f}, "
                f"D3={self.led_state})")


# ---------------------------------------------------------------------------
# CLI: walk the battery stack from fresh to dead
# ---------------------------------------------------------------------------

def _main() -> None:
    """Walk BT1 from fresh (100% SoC) to exhausted (0% SoC) and print
    a per-state trace of every voltage and current the design depends
    on. The trace makes the fail-safe behaviour visible: the rail
    stays at 5.00 V across the bulk of the discharge, sags gracefully
    near end-of-life, and the LED dims-then-darkens to tell the
    builder when to swap the cells."""
    run_scenarios(
        FiveVoltRailPower(),
        scenarios=[
            (f"{soc*100:>3.0f}% remaining", (soc,))
            for soc in (1.00, 0.80, 0.50, 0.20, 0.10, 0.05, 0.02, 0.00)
        ],
        columns=[
            ('SoC',     lambda c, a, k: f"{a[0]*100:>4.0f} %"),
            ('V_cell',  lambda c, a, k: f"{c.bt1.cell_voltage:>5.2f} V"),
            ('V_stack', lambda c, a, k: f"{c.stack_voltage:>5.2f} V"),
            ('V_in',    lambda c, a, k: f"{c.regulator_input_voltage:>5.2f} V"),
            ('V_rail',  lambda c, a, k: f"{c.rail_voltage:>5.2f} V"),
            ('I_LED',   lambda c, a, k: f"{c.led_current_ma:>5.2f} mA"),
            ('D3',      lambda c, a, k: c.led_state),
        ],
    )


if __name__ == '__main__':
    _main()
