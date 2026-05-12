"""Pack-side Li-Ion fuel gauge — based on TI Designs TIDA-00594.

Models the *physical pack topology* of a single-cell Li-Ion battery
pack with an integrated BQ27546-G1 fuel gauge: the Li-Ion cell sits
between PACK+ and the cell- node; a 10-mΩ sense resistor sits between
cell- and PACK- (where the gauge's SRP/SRN inputs straddle it); a
10-kΩ NTC thermistor sits between TS and ground; three bypass caps
decouple REGIN, VCC, and BAT; and a 4-pin host header exposes SDA /
SCL / HDQ / GND for an off-board MCU to read state-of-charge.

What this demo CAN'T model honestly is what makes the BQ27546-G1
actually interesting: Impedance Track™ integrates *current* across
the sense resistor over *time*, and the I²C / HDQ host interface
runs clocked, multi-byte transactions.  This framework's voltage-only
steady-state graph has neither current nor a clock.  The chip
gracefully degrades to its real power-on fallback: invert the
open-circuit-voltage curve to get a coarse SoC from the cell voltage
alone.  The SE (shutdown-enable) pin is a faithful digital output —
the gauge drives it LOW when SoC falls below the configurable
shutdown threshold (default 5 %).

Scope notes
-----------
* No protection IC.  TIDA-00594's simplified schematic shows it as a
  black box; the SE → CHG/DSG-FET path is a current concern the
  voltage-only simulator can't help with anyway.
* No host MCU.  J1 is a bare 4-pin header (SDA, SCL, HDQ, GND); a
  composed demo can plug in a real MCU board on that surface.
* Sense resistor and TS thermistor are modelled as plain `Resistor`
  parts (no-op under simulation).  Values are *cosmetic* in the
  steady-state graph but on the BOM they reflect what TIDA-00594
  specifies.

Run directly to walk the cell from 100 % to 0 % SoC and watch the
gauge's SE pin trip:

    python demos/li_ion_fuel_gauge.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from circuitry import (
    Board, Direction, ELECTRICAL, wire,
    BQ27546G1, Capacitor, Cell, Resistor,
    run_scenarios,
)
from components.connectors.headers import Header1xNFemale
from framework.registry import register


@register('BatteryPackBoard')
class BatteryPackBoard(Board):
    """Single-cell Li-Ion pack with integrated BQ27546-G1 fuel gauge.

    Connector surface
    -----------------
        J1 (Header1xNFemale, 4-pin) — host-side
            J1.p1 = SDA  (I²C data, slave-side)
            J1.p2 = SCL  (I²C clock, slave-side)
            J1.p3 = HDQ  (single-wire serial)
            J1.p4 = GND  (system ground reference)

    Pack terminals are not exposed as a connector — the cell is on the
    board, BT1 is its refdes, and PACK+ / PACK- are internal nodes
    that the cell + sense resistor straddle.  The `pack_voltage`
    property reports the open-circuit terminal voltage at the present
    SoC for tests and traces.

    Omits `__slots__` so `Board.__init__` auto-collects every part.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, *, refdes_number: int) -> None:
        # --- BOM ------------------------------------------------------
        self.u1 = BQ27546G1(refdes_number=1)
        self.bt1 = Cell(initial_state_of_charge=1.0, refdes_number=1)
        # Sense resistor — datasheet recommends 5-20 mΩ; 10 mΩ is the
        # mid-range value.  Voltage-only graph treats it as a no-op
        # short, but the value lives on the BOM.
        self.r_sns  = Resistor(0.010, refdes_number=1)
        # NTC thermistor — 103AT-type (10 kΩ @ 25 °C).
        self.r_ts   = Resistor(10_000, refdes_number=2)
        # I²C pull-ups (10 kΩ to VCC, per datasheet recommendation).
        self.r_sda  = Resistor(10_000, refdes_number=3)
        self.r_scl  = Resistor(10_000, refdes_number=4)
        # HDQ pull-up (typically 10 kΩ to VCC).
        self.r_hdq  = Resistor(10_000, refdes_number=5)
        # Bypass / decoupling capacitors — REGIN, VCC, BAT.
        self.c_regin = Capacitor(100e-9, refdes_number=1)
        self.c_vcc   = Capacitor( 1.0e-6, refdes_number=2)
        self.c_bat   = Capacitor(100e-9, refdes_number=3)

        # Host-side header.  All four pins in ELECTRICAL.  Connector
        # pins are Analog BIDIR (conductor wildcards) so the same
        # header carries the I²C / HDQ digital lines and the analog
        # ground reference without a type mismatch.
        self.j1 = Header1xNFemale(
            pin_count=4, pitch_mm=2.54,
            domain=ELECTRICAL, refdes_number=1,
        )

        # --- Wiring ---------------------------------------------------
        # Each `wire(...)` call defines one electrical net.  The
        # framework refuses to merge two existing nets in a second
        # call, so every participant of a net has to appear in the
        # same call.
        #
        # Net: PACK+ — cell positive terminal, gauge BAT and REGIN,
        # and the BAT-side and REGIN-side decoupling caps.
        # NB: CE (chip-enable) is a *digital* input pin; tying it to
        # the analog cell-positive rail trips the framework's signal-
        # type check.  Real designs land CE on a digital control line
        # from a protection IC; here CE is left unconnected and the
        # gauge's LDO comes up by default (the datasheet POR pulls it
        # HIGH internally with a weak pull-up).
        wire(
            self.bt1.ports['pos'],
            self.u1.ports['BAT'],
            self.u1.ports['REGIN'],
            self.c_bat.ports['t1'],
            self.c_regin.ports['t1'],
        )

        # Net: PACK- / system ground.  The cell's negative terminal
        # IS the pack ground in a 1S design with no protection FET
        # modelled.  Every "to ground" pin lands here.  The chip's
        # two VSS pads are exposed under disambiguated names because
        # they share a pin name.
        wire(
            self.bt1.ports['neg'],
            self.u1.ports['SRP'],          # sense-resistor cell side
            self.u1.ports['SRN'],          # sense-resistor pack side (collapsed: no current)
            self.u1.ports['VSS_1'],        # gauge ground pad C1
            self.u1.ports['VSS_2'],        # gauge ground pad C2
            self.r_sns.ports['t1'],
            self.r_sns.ports['t2'],
            self.c_bat.ports['t2'],
            self.c_regin.ports['t2'],
            self.c_vcc.ports['t2'],
            self.r_ts.ports['t2'],
            self.j1.pins[3].internal,
        )

        # Net: VCC — gauge's internal-LDO output, the decoupling cap,
        # and the three open-drain pull-ups for SDA / SCL / HDQ.
        wire(
            self.u1.ports['VCC'],
            self.c_vcc.ports['t1'],
            self.r_sda.ports['t2'],
            self.r_scl.ports['t2'],
            self.r_hdq.ports['t2'],
        )

        # Net: TS — thermistor between gauge TS pin and ground.
        wire(self.u1.ports['TS'], self.r_ts.ports['t1'])

        # Host-bus nets: each comm line is the gauge pin + one
        # pull-up + the header pin that exposes it off-board.
        wire(self.u1.ports['SDA'],
             self.r_sda.ports['t1'],
             self.j1.pins[0].internal)
        wire(self.u1.ports['SCL'],
             self.r_scl.ports['t1'],
             self.j1.pins[1].internal)
        wire(self.u1.ports['HDQ'],
             self.r_hdq.ports['t1'],
             self.j1.pins[2].internal)

        super().__init__(
            name='Li-Ion 1S Battery Pack',
            revision='A',
            refdes_number=refdes_number,
        )

    # ------------------------------------------------------------------
    # Composable read accessors
    # ------------------------------------------------------------------

    @property
    def pack_voltage(self) -> float:
        """Cell terminal voltage at the present SoC — what a multimeter
        on PACK+ / PACK- would read with no load."""
        return float(self.bt1.terminal_voltage)

    @property
    def state_of_charge(self) -> float:
        """Most-recent gauge SoC estimate — what a host reading the
        BQ27546-G1 over I²C / HDQ would see."""
        return self.u1.state_of_charge

    @property
    def shutdown_enable(self) -> bool | None:
        """SE pin level (J1's host can monitor this off-bus).  HIGH
        when the cell is healthy; LOW once SoC drops below the gauge's
        shutdown threshold."""
        return self.u1.ports['SE'].value

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, state_of_charge: float) -> dict[str, float | bool | None]:
        """Standalone-test surface: prescribe a new cell SoC (the
        framework can't discharge it on its own), evaluate, and read
        back the cell voltage, the gauge's SoC estimate, and the SE
        pin."""
        self._assert_no_inputs_wired()
        self.bt1.state_of_charge = state_of_charge
        self.evaluate()
        return {
            'pack_voltage':    self.pack_voltage,
            'state_of_charge': self.state_of_charge,
            'shutdown_enable': self.shutdown_enable,
        }


# ---------------------------------------------------------------------------
# Scenario walk
# ---------------------------------------------------------------------------

def _v(volts: float) -> str:
    return f"{volts:.2f}"


def _p(soc: float) -> str:
    return f"{soc * 100:.0f}%"


def _b(v: bool | None) -> str:
    if v is None:
        return '·'
    return 'H' if bool(v) else 'L'


def _main() -> None:
    print("=" * 72)
    print("Li-Ion 1S battery pack with BQ27546-G1 fuel gauge")
    print("(SoC stepped down to simulate discharge — Impedance Track is")
    print(" not simulable in a voltage-only graph; this is the OCV-curve")
    print(" fallback the real chip uses at power-on.)")
    print("=" * 72)
    run_scenarios(
        BatteryPackBoard(refdes_number=1),
        scenarios=[
            ("just unplugged from charger", (1.00,)),
            ("steady-state mid-discharge",  (0.80,)),
            ("half full",                   (0.50,)),
            ("low warning",                 (0.20,)),
            ("just above shutdown",         (0.07,)),
            ("shutdown threshold tripped",  (0.03,)),
            ("cell flat",                   (0.00,)),
        ],
        columns=[
            ("scenario_soc",  lambda c, a, k: _p(a[0])),
            ("v_cell",        lambda c, a, k: _v(c.pack_voltage)),
            ("gauge_soc",     lambda c, a, k: _p(c.state_of_charge)),
            ("SE",            lambda c, a, k: _b(c.shutdown_enable)),
        ],
    )


if __name__ == '__main__':
    _main()
