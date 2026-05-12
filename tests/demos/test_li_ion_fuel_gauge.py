import pytest


def _board():
    from li_ion_fuel_gauge import BatteryPackBoard
    return BatteryPackBoard(refdes_number=1)


@pytest.fixture
def board():
    return _board()


def test_bom_present(board):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in board._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    assert "BQ27546G1.U1"       in parts
    assert "Cell.BT1"           in parts
    assert "Header1xNFemale.J1" in parts
    # Sense, TS, three pull-ups.
    for n in (1, 2, 3, 4, 5):
        assert f"Resistor.R{n}" in parts
    # REGIN / VCC / BAT decoupling caps.
    for n in (1, 2, 3):
        assert f"Capacitor.C{n}" in parts


def test_board_refdes(board):
    assert board.refdes == 'A1'


def test_one_connector_exposed(board):
    """Just the host-side header — pack terminals are internal."""
    assert len(board.connectors) == 1


def test_full_cell_yields_full_soc(board):
    out = board(1.0)
    assert out['state_of_charge'] == pytest.approx(1.0)
    assert out['shutdown_enable'] is True


def test_mid_cell_yields_mid_soc(board):
    out = board(0.5)
    assert out['state_of_charge'] == pytest.approx(0.5)
    assert out['shutdown_enable'] is True


def test_below_threshold_trips_shutdown_enable(board):
    out = board(0.02)
    assert out['shutdown_enable'] is False


def test_empty_cell_reports_zero_soc(board):
    out = board(0.0)
    assert out['state_of_charge'] == 0.0
    assert out['shutdown_enable'] is False


def test_pack_voltage_matches_ocv_curve(board):
    out = board(1.0)
    assert out['pack_voltage'] == pytest.approx(4.2)
    out = board(0.5)
    assert out['pack_voltage'] == pytest.approx(3.7)
    out = board(0.0)
    assert out['pack_voltage'] == pytest.approx(3.0)


def test_discharge_walk_is_monotonic(board):
    """Walking SoC from 100 % to 0 % must produce a monotonically
    decreasing gauge SoC and a monotonically decreasing cell voltage —
    the OCV curve must not fold back on itself anywhere along the
    way."""
    last_soc = None
    last_v   = None
    for stim in (1.0, 0.8, 0.5, 0.2, 0.07, 0.03, 0.0):
        out = board(stim)
        if last_soc is not None:
            assert out['state_of_charge'] <= last_soc + 1e-9
            assert out['pack_voltage']    <= last_v   + 1e-9
        last_soc = out['state_of_charge']
        last_v   = out['pack_voltage']


def test_shutdown_threshold_is_default_5pct(board):
    """SE HIGH well above 5 %, LOW well below.  Exact boundary is
    fuzzed by float rounding in the OCV-curve forward/inverse pair,
    so this checks safely-clear values either side of the threshold
    rather than the boundary itself."""
    out = board(0.10)
    assert out['shutdown_enable'] is True
    out = board(0.04)
    assert out['shutdown_enable'] is False
