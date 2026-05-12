import pytest

from components.chips.concepts.backup_supervisor import BackupSupervisor


def _sup(**overrides):
    defaults = dict(
        bulk_capacitance_uf=1200.0,
        v_boost_target=48.0,
        v_buck_reg=17.0,
        v_buck_uvlo=19.0,
        v_uv_threshold=18.0,
        v_ov_threshold=30.0,
        charge_time_constant_ms=80.0,
        load_w_normal=25.0,
        load_w_backup=7.0,
        buck_efficiency=0.9,
    )
    defaults.update(overrides)
    return BackupSupervisor(**defaults)


def test_vin_in_spec_window():
    s = _sup()
    assert s.vin_in_spec(24.0) is True
    assert s.vin_in_spec(18.0) is True       # at UV threshold
    assert s.vin_in_spec(30.0) is True       # at OV threshold
    assert s.vin_in_spec(17.9) is False
    assert s.vin_in_spec(30.1) is False
    assert s.vin_in_spec(0.0)  is False
    assert s.vin_in_spec(-5.0) is False      # reverse polarity


def test_starts_with_bulk_cap_empty():
    assert _sup().bulk_v == 0.0


def test_normal_vin_makes_vout_equal_vin_with_flt_high():
    s = _sup()
    vout = s(vin_v=24.0)
    assert vout == 24.0
    assert s.ports['flt_b'].value is True
    assert s.ports['backup_active'].value is False


def test_out_of_spec_vin_with_empty_cap_collapses_vout():
    s = _sup()
    assert s(vin_v=0.0) == 0.0
    assert s.ports['flt_b'].value is False
    assert s.ports['backup_active'].value is False


def test_brown_out_with_full_cap_engages_buck_at_reg_voltage():
    s = _sup()
    s._bulk_v = 48.0
    assert s(vin_v=0.0) == 17.0          # at v_buck_reg
    assert s.ports['flt_b'].value         is False
    assert s.ports['backup_active'].value is True


def test_brown_out_with_cap_below_uvlo_drops_vout():
    s = _sup()
    s._bulk_v = 18.0                      # below v_buck_uvlo (19 V)
    assert s(vin_v=0.0) == 0.0
    assert s.ports['backup_active'].value is False


def test_overvoltage_input_also_trips_fault():
    s = _sup()
    s._bulk_v = 48.0
    assert s(vin_v=32.0) == 17.0          # backup, not 32 V on the bus
    assert s.ports['flt_b'].value is False


def test_charge_bulk_approaches_target_first_order():
    s = _sup(charge_time_constant_ms=100.0)
    s.charge_bulk(100.0)                  # one τ → ~63 % of target
    assert 28 < s.bulk_v < 32
    s.charge_bulk(900.0)                  # plenty of time → saturate
    assert s.bulk_v == pytest.approx(48.0, abs=0.1)


def test_charge_bulk_clamps_at_target():
    s = _sup()
    s._bulk_v = 48.0
    s.charge_bulk(10_000)                 # huge step, must not overshoot
    assert s.bulk_v == 48.0


def test_discharge_bulk_drains_proportional_to_load():
    """Energy: ½·C·ΔV² ≈ P/η · Δt for small steps.  A 7 W load
    on a 1200 µF cap at 48 V for 10 ms loses I·Δt = (7/0.9)/48 · 10ms
    of charge → ΔV = Q/C ≈ 1.35 V (explicit-Euler approximation)."""
    s = _sup()
    s._bulk_v = 48.0
    s.discharge_bulk(10.0)
    assert 46.5 < s.bulk_v < 47.0


def test_discharge_bulk_does_not_go_negative():
    s = _sup()
    s._bulk_v = 0.1
    s.discharge_bulk(10_000)              # absurd drain
    assert s.bulk_v == 0.0


def test_discharge_then_recharge_recovers_target():
    s = _sup(charge_time_constant_ms=80.0)
    s._bulk_v = 48.0
    s.discharge_bulk(200.0)               # bleed for 200 ms
    drained = s.bulk_v
    assert drained < 48.0
    s.charge_bulk(2_000)                  # plenty of charging time
    assert s.bulk_v == pytest.approx(48.0, abs=0.1)


def test_ports_have_correct_directions():
    from framework.port import Direction
    s = _sup()
    assert s.ports['vin_v'        ].direction is Direction.IN
    assert s.ports['flt_b'        ].direction is Direction.OUT
    assert s.ports['vout_v'       ].direction is Direction.OUT
    assert s.ports['bulk_v'       ].direction is Direction.OUT
    assert s.ports['backup_active'].direction is Direction.OUT


def test_rejects_zero_capacitance():
    with pytest.raises(Exception):
        BackupSupervisor(bulk_capacitance_uf=0)


def test_rejects_efficiency_outside_bounds():
    with pytest.raises(Exception):
        BackupSupervisor(buck_efficiency=0)
    with pytest.raises(Exception):
        BackupSupervisor(buck_efficiency=1.1)
