import pytest


@pytest.fixture
def supply():
    from backup_power import BackupPower
    return BackupPower()


def test_bom_present(supply):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in supply._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    # The three TI ICs.
    assert "TPS2660.U1" in parts
    assert "LM5002.U2"  in parts
    assert "LM5160.U3"  in parts
    # Boost-stage passives.
    assert "Inductor.L1"   in parts
    assert "D1N5817.D1"    in parts
    assert "Capacitor.C10" in parts


def test_cold_start_no_output(supply):
    """At t=0 with no input, the bus is at 0 V and FLT_B is LOW."""
    supply(vin_volts=0.0, advance_ms=0.0)
    assert supply.vout_v       == 0.0
    assert supply.primary_ok   is False
    assert supply.backup_active is False
    assert supply.bulk_v       == 0.0


def test_normal_operation_passes_vin_through(supply):
    """With VIN in the eFuse window, the TPS2660 conducts and the
    bus equals the input voltage (the buck regulator is idle)."""
    supply(vin_volts=24.0, advance_ms=0.0)
    assert supply.vout_v     == 24.0
    assert supply.primary_ok is True


def test_bulk_cap_charges_during_normal_operation(supply):
    """LM5002 boost charges C10 toward 48 V exponentially."""
    supply(vin_volts=24.0, advance_ms=0.0)
    initial = supply.bulk_v
    supply(vin_volts=24.0, advance_ms=200.0)
    assert supply.bulk_v > initial
    # Plenty of time -> saturate at the boost target.
    supply(vin_volts=24.0, advance_ms=2_000.0)
    assert supply.bulk_v == pytest.approx(48.0, abs=0.1)


def test_brownout_switches_to_backup_at_buck_reg_voltage(supply):
    """When VIN drops out of spec and the cap still has headroom,
    the buck takes over at 17 V."""
    supply(vin_volts=24.0, advance_ms=2_000.0)   # fully charge
    vout = supply(vin_volts=0.0, advance_ms=10.0)
    assert vout                 == 17.0
    assert supply.backup_active is True
    assert supply.primary_ok    is False


def test_backup_holds_for_quoted_120ms_at_7w(supply):
    """Per TIDUCC7, the design provides 120 ms of backup at 7 W with
    the bus still regulated to 17 V.  Walk that interval and confirm
    the bus never drops out of regulation."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    supply(vin_volts=0.0,  advance_ms=0.0)
    for _ in range(12):
        v = supply(vin_volts=0.0, advance_ms=10.0)
        assert v == 17.0, f"backup lost at bulk_v={supply.bulk_v:.2f} V"


def test_bus_collapses_when_cap_falls_below_uvlo(supply):
    """After enough time on backup the cap drops below the buck UVLO
    and the regulator can no longer source the 17 V bus."""
    supply(vin_volts=24.0, advance_ms=2_000.0)   # fully charge
    # Run the backup well past the spec until the cap is below 19 V.
    for _ in range(50):
        supply(vin_volts=0.0, advance_ms=20.0)
    assert supply.bulk_v < 19.0
    assert supply.vout_v == 0.0
    assert supply.backup_active is False


def test_input_restoration_returns_to_primary(supply):
    """After a brown-out, restoring VIN must put the bus back on the
    primary path with FLT_B asserted high again."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    supply(vin_volts=0.0,  advance_ms=50.0)
    assert supply.backup_active is True
    supply(vin_volts=24.0, advance_ms=5.0)
    assert supply.vout_v        == 24.0
    assert supply.primary_ok    is True
    assert supply.backup_active is False


def test_overvoltage_input_also_engages_backup(supply):
    """The eFuse window is two-sided: an overvoltage input is just as
    much a fault as a brown-out, and the buck should source the bus
    from the bulk cap rather than passing 32 V to the load."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    vout = supply(vin_volts=32.0, advance_ms=10.0)
    assert vout                 == 17.0
    assert supply.primary_ok    is False
    assert supply.backup_active is True


def test_brief_dip_within_charge_state_recovers(supply):
    """A 10 ms dip — the IEC 61000-4-29 spec window — should drain
    the cap only by a couple of volts and leave the system back on
    the primary path well above the buck UVLO once the input recovers."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    before = supply.bulk_v
    supply(vin_volts=0.0,  advance_ms=10.0)
    supply(vin_volts=24.0, advance_ms=5.0)
    # Net drop is ~1.3 V (10 ms of 7 W drain partially refilled);
    # nowhere near the buck UVLO at 19 V.
    assert supply.bulk_v > before - 2.0
    assert supply.bulk_v > supply.supervisor.v_buck_uvlo + 20.0
    assert supply.primary_ok is True


def test_negative_input_is_a_fault(supply):
    """Reverse-polarity protection: a negative input must be treated
    as out-of-spec (TPS2660 blocks reverse current)."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    supply(vin_volts=-12.0, advance_ms=5.0)
    assert supply.primary_ok is False


def test_repeated_idle_calls_stay_quiet(supply):
    """No spurious state changes when VIN is held at a normal value."""
    supply(vin_volts=24.0, advance_ms=2_000.0)
    for _ in range(10):
        supply(vin_volts=24.0, advance_ms=10.0)
        assert supply.primary_ok    is True
        assert supply.backup_active is False
        assert supply.vout_v        == 24.0
