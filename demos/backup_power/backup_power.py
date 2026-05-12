"""Backup-power supply — composite-circuit demo.

Faithful recreation of TI Designs reference TIDA-03031 (Input
Protection and Backup Supply Reference Design for 25-W PLC Controller
Unit): https://www.ti.com/tool/TIDA-03031.

System architecture
-------------------
A 24-V industrial DC bus feeds a PLC controller through three stages:

    primary path :  VIN ──[ TPS2660 eFuse ]── VOUT  → system load
    charge path  :  VIN ──[ LM5002 boost ]── L2 ── D ──[ C10 bulk ]── 0
    backup path  :  C10 (48 V) ──[ LM5160 buck ]── VOUT  → system load

Under normal operation (19.2 V ≤ VIN ≤ 28.8 V) the TPS2660 conducts
straight through, the LM5002 boost trickle-charges the bulk hold-up
capacitor to ~48 V, and the LM5160 buck is idle because the bus is
already above its 17 V regulation target.  On a power-fail event the
TPS2660 deasserts FLT_B; the LM5002 shuts off; the LM5160 takes over
and regulates the bus to 17 V from the bulk capacitor for ~10 ms at
full 25 W load (per IEC 61000-4-29) plus an additional ~120 ms at the
project's quoted 7 W backup load.

Bill of materials (from TIDUCC7):
    U1  TPS2660    eFuse / input protection
    U2  LM5002     wide-Vin DCM boost (charges the bulk cap to 48 V)
    U3  LM5160     synchronous buck (17 V regulation during backup)
    D1  D1N5817    Schottky output diode of the boost stage
    L1  33 µH      boost inductor (L2 on the TI schematic)
    C10 1200 µF    bulk hold-up capacitor (Nichicon 50 V electrolytic)
    Plus the assorted bypass, feedback, and compensation R/C network.

Simulation notes
----------------
Switching-converter behaviour isn't tractable in a voltage-only
steady-state graph; the three TI ICs sit in the BOM as black-box
parts and a single `BackupSupervisor` cell models the system-level
behaviour: input-window detection, first-order bulk-cap charge, and
energy-conserving cap discharge during backup (½·C·V² → P/V·dt).  The
demo's `__call__(vin_volts, advance_ms)` advances the supervisor's
internal `_bulk_v` between calls — same Python-level escape hatch the
doorbell's `Monostable` uses for its remaining-time countdown.
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
    Circuit,
    Capacitor, Inductor, Rail, Resistor,
    D1N5817,
    LM5002, LM5160, TPS2660,
    run_scenarios,
)
from components.chips.concepts.backup_supervisor import BackupSupervisor


# --------------------------------------------------------------------------
# Composite circuit
# --------------------------------------------------------------------------

class BackupPower(Circuit):
    """24-V backup-power supply for a 25-W PLC controller unit.

    External-port surface (auto-exposed via the BackupSupervisor cell):
        vin_v          Analog IN  — primary supply, V.
        flt_b          Digital OUT — eFuse fault flag (HIGH = OK).
        vout_v         Analog OUT — system-bus voltage.
        bulk_v         Analog OUT — bulk-cap voltage trace.
        backup_active  Digital OUT — HIGH while running on hold-up.

    Composite call signature:
        protector(vin_volts: float, advance_ms: float = 0) -> float
        Returns the bus voltage.

    Auto-collect composite: parts are listed in dataflow order so the
    cycle-fallback evaluation visits the supervisor (which reads VIN
    and drives the outputs) after the rails that supply it.
    """

    # Design knobs from the TIDUCC7 design guide.
    BULK_CAPACITANCE_UF:    float = 1200.0
    BOOST_TARGET_V:         float = 48.0
    BUCK_REG_V:             float = 17.0
    BUCK_FALLING_UVLO_V:    float = 19.0
    INPUT_UV_THRESHOLD_V:   float = 18.0
    INPUT_OV_THRESHOLD_V:   float = 30.0
    CHARGE_TAU_MS:          float = 400.0 / 5.0   # ~5τ for the 0.4 s quoted full charge
    LOAD_NORMAL_W:          float = 25.0
    LOAD_BACKUP_W:          float = 7.0
    BUCK_EFFICIENCY:        float = 0.9

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # Rails.
        self.gnd = Rail(False)
        self.vcc = Rail(True)

        # The three TI ICs — black-box BOM parts.
        self.tps2660 = TPS2660(refdes_number=1)   # eFuse / input protection
        self.lm5002  = LM5002 (refdes_number=2)   # bulk-cap charge boost
        self.lm5160  = LM5160 (refdes_number=3)   # 17-V backup buck

        # Power-stage passives.
        self.l1  = Inductor (33e-6,  refdes_number=1)   # L2 on the TI schematic
        self.d1  = D1N5817(refdes_number=1)             # boost rectifier
        self.c10 = Capacitor(self.BULK_CAPACITANCE_UF * 1e-6, refdes_number=10)

        # A small subset of the bypass / feedback / compensation R-C
        # network — enough that the BOM lists the right population.
        self.c1  = Capacitor(0.01e-6, refdes_number=1)   # LM5002 RT cap
        self.c2  = Capacitor(1e-6,    refdes_number=2)   # input bypass
        self.c3  = Capacitor(1e-6,    refdes_number=3)
        self.c4  = Capacitor(3300e-12, refdes_number=4)  # boost compensation
        self.c5  = Capacitor(0.022e-6, refdes_number=5)  # boost slope
        self.c6  = Capacitor(1e-6,    refdes_number=6)
        self.c7  = Capacitor(0.1e-6,  refdes_number=7)
        self.c8  = Capacitor(1e-6,    refdes_number=8)   # buck input bypass
        self.c9  = Capacitor(0.1e-6,  refdes_number=9)
        self.c12 = Capacitor(1e-6,    refdes_number=12)  # buck bootstrap
        self.c13 = Capacitor(220e-6,  refdes_number=13)  # buck output cap
        self.c14 = Capacitor(1e-6,    refdes_number=14)
        self.c15 = Capacitor(2.2e-6,  refdes_number=15)

        self.r6  = Resistor(715_000, refdes_number=6)
        self.r7  = Resistor(226_000, refdes_number=7)
        self.r11 = Resistor(40_200,  refdes_number=11)
        self.r16 = Resistor(10_000,  refdes_number=16)

        # Behavioural system supervisor — models the input-protection
        # decisions, the bulk-cap charge trajectory, and the buck's
        # take-over during a brown-out.  All composite-level state
        # lives here.
        self.supervisor = BackupSupervisor(
            bulk_capacitance_uf=self.BULK_CAPACITANCE_UF,
            v_boost_target     =self.BOOST_TARGET_V,
            v_buck_reg         =self.BUCK_REG_V,
            v_buck_uvlo        =self.BUCK_FALLING_UVLO_V,
            v_uv_threshold     =self.INPUT_UV_THRESHOLD_V,
            v_ov_threshold     =self.INPUT_OV_THRESHOLD_V,
            charge_time_constant_ms=self.CHARGE_TAU_MS,
            load_w_normal      =self.LOAD_NORMAL_W,
            load_w_backup      =self.LOAD_BACKUP_W,
            buck_efficiency    =self.BUCK_EFFICIENCY,
        )

        # No top-level signal wires.  The three TI ICs are opaque in
        # the voltage-only graph, the L-C boost network is opaque too
        # (Capacitor / Inductor `.evaluate()` are no-ops), and any
        # wire between them and the supervisor's rails would either
        # short the rail or be flagged as a floating multi-BIDIR net.
        # The supervisor's outputs drive the composite's external
        # ports directly; the chips and passives ride on the BOM via
        # auto-collect for documentation and downstream export.

        super().__init__(
            ports={
                'vin_v':         self.supervisor.ports['vin_v'],
                'flt_b':         self.supervisor.ports['flt_b'],
                'vout_v':        self.supervisor.ports['vout_v'],
                'bulk_v':        self.supervisor.ports['bulk_v'],
                'backup_active': self.supervisor.ports['backup_active'],
            },
        )

    # ------------------------------------------------------------------
    # Read accessors
    # ------------------------------------------------------------------

    @property
    def vout_v(self) -> float:
        v = self.supervisor.ports['vout_v'].value
        return float(v if v is not None else 0.0)

    @property
    def bulk_v(self) -> float:
        return self.supervisor.bulk_v

    @property
    def primary_ok(self) -> bool:
        """True iff the TPS2660 eFuse is conducting (FLT_B HIGH)."""
        return self.supervisor.ports['flt_b'].value is True

    @property
    def backup_active(self) -> bool:
        return self.supervisor.ports['backup_active'].value is True

    # ------------------------------------------------------------------
    # Drive interface
    # ------------------------------------------------------------------

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, vin_volts: float, advance_ms: float = 0.0) -> float:
        """Advance `advance_ms` of simulated time at the given input
        voltage and return the resulting system-bus voltage.

        Time-stepping is done before the evaluate so that any change
        in `vin_volts` is observed against the just-updated bulk-cap
        state.  Charging happens while the eFuse window says VIN is
        in spec; otherwise the bulk cap is being drained by the buck
        regulator at the configured backup load.
        """
        elapsed = float(advance_ms)
        if self.supervisor.vin_in_spec(float(vin_volts)):
            self.supervisor.charge_bulk(elapsed)
        else:
            self.supervisor.discharge_bulk(elapsed)
        self._ports['vin_v'].drive(float(vin_volts))
        self.evaluate()
        return self.vout_v

    def __repr__(self) -> str:
        return (f"BackupPower(vout_v={self.vout_v:.2f}, "
                f"bulk_v={self.bulk_v:.2f}, "
                f"primary_ok={self.primary_ok}, "
                f"backup_active={self.backup_active})")


# --------------------------------------------------------------------------
# Scenario walk
# --------------------------------------------------------------------------

def _v(x: float) -> str:
    return f"{x:>6.2f}"


def _main() -> None:
    """Walk through cold-start → normal → brown-out → 120 ms hold-up
    → cap depletion → input restored."""
    run_scenarios(
        BackupPower(),
        scenarios=[
            # Cold start: VIN ramps up, cap begins charging.
            ("cold start, VIN = 0 V",              (0.0,  0.0)),
            ("VIN ramp to 24 V",                   (24.0, 50.0)),
            ("settle, cap charging",               (24.0, 200.0)),
            ("cap nearly charged",                 (24.0, 300.0)),
            ("steady-state normal operation",      (24.0, 500.0)),
            # Brief 10 ms dip — well inside the IEC 61000-4-29 window.
            ("brown-out: VIN → 0 V (10 ms)",       (0.0,  10.0)),
            ("100 ms into backup at 7 W",          (0.0,  90.0)),
            ("approaching backup end",             (0.0,  20.0)),
            # Past the spec window — cap will run down through the
            # buck UVLO and the bus drops.
            ("backup exhausted",                   (0.0,  60.0)),
            # Restore the input.
            ("VIN restored to 24 V",               (24.0, 5.0)),
            ("recharge for 150 ms",                (24.0, 150.0)),
            ("recharge for another 500 ms",        (24.0, 500.0)),
            # OV trip — input out of spec on the high side.
            ("input OV (32 V)",                    (32.0, 10.0)),
            ("OV brown-out continues",             (32.0, 50.0)),
        ],
        columns=[
            ("vin",    lambda c, a, k: _v(a[0])),
            ("dt_ms",  lambda c, a, k: f"{a[1]:>6.0f}"),
            ("vout",   lambda c, a, k: _v(c.vout_v)),
            ("bulk_v", lambda c, a, k: _v(c.bulk_v)),
            ("FLT_B",  lambda c, a, k: 'HI'   if c.primary_ok    else 'lo'),
            ("backup", lambda c, a, k: 'ON'   if c.backup_active else '—'),
        ],
    )


if __name__ == '__main__':
    _main()
