import pytest


def _board():
    from fan_cooling import FanCoolingBoard
    return FanCoolingBoard(refdes_number=1)


def _system():
    from fan_cooling import CooledSystem
    return CooledSystem()


@pytest.fixture
def board():
    return _board()


@pytest.fixture
def system():
    return _system()


# ----------------------------------------------------------------------
# Standalone board behaviour
# ----------------------------------------------------------------------

def test_bom_present(board):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in board._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    assert "TMP302.U1"        in parts
    assert "SN74AHC1G14.U2"   in parts
    assert "Q2N7000.Q1"       in parts
    assert "D1N4728A.D1"      in parts
    assert "Header1xNFemale.J1" in parts
    assert "Header1xNFemale.J2" in parts
    for n in (1, 2, 3):
        assert f"Resistor.R{n}" in parts


def test_board_refdes_uses_a_prefix(board):
    """Boards carry the IEEE 315 'A' assembly refdes prefix."""
    assert board.refdes == 'A1'


def test_starts_with_fan_off(board):
    board(ambient_c=25.0)
    assert board.fan_on is False


def test_at_60c_fan_turns_on(board):
    assert board(ambient_c=60.0) is True


def test_above_trip_keeps_fan_on(board):
    board(ambient_c=60.0)
    assert board(ambient_c=80.0) is True


def test_deadband_holds_state_when_off(board):
    """25 °C → 55 °C should stay OFF (never crossed the 60 °C trip)."""
    board(ambient_c=25.0)
    assert board(ambient_c=55.0) is False


def test_deadband_holds_state_when_on(board):
    """65 °C → 55 °C should stay ON (haven't crossed 50 °C falling trip)."""
    board(ambient_c=65.0)
    assert board(ambient_c=55.0) is True


def test_at_50c_falling_trip_fan_turns_off(board):
    board(ambient_c=65.0)
    assert board(ambient_c=50.0) is False


def test_custom_trip_points():
    from fan_cooling import FanCoolingBoard
    b = FanCoolingBoard(refdes_number=1, trip_high_c=80.0, trip_low_c=70.0)
    assert b.trip_high_c == 80.0
    assert b.trip_low_c  == 70.0
    assert b(ambient_c=75.0) is False
    assert b(ambient_c=80.0) is True
    assert b(ambient_c=75.0) is True
    assert b(ambient_c=70.0) is False


def test_fan_negative_drive_propagates_to_connector_external(board):
    """When the controller turns the fan on, the FAN- pin's external
    face should read HIGH — that's the signal a mating fan sees."""
    board(ambient_c=65.0)
    fan_negative_external = board.fan_out.pins[1].external.value
    assert bool(fan_negative_external) is True
    # And LOW when fan is off:
    board(ambient_c=25.0)
    fan_negative_external = board.fan_out.pins[1].external.value
    assert bool(fan_negative_external) is False


def test_ambient_c_setter_round_trip(board):
    board.ambient_c = 75.0
    assert board.ambient_c == 75.0


def test_connectors_exposed_for_mating(board):
    """Both connectors must be in the Board's `connectors` tuple so a
    parent can mate to them by index, the way water_alarm_split.py
    does for its sensor and controller boards."""
    assert len(board.connectors) == 2


# ----------------------------------------------------------------------
# Composed CooledSystem behaviour
# ----------------------------------------------------------------------

def test_cooled_system_constructs(system):
    """The assembly's __init__ must complete without raising — the
    mating of supply→cooler must not short any rail or trigger a
    floating-net error."""
    assert system is not None


def test_cooled_system_fan_off_at_room_temp(system):
    assert system(ambient_c=25.0) is False


def test_cooled_system_fan_on_above_trip(system):
    assert system(ambient_c=70.0) is True


def test_cooled_system_hysteresis_preserved(system):
    """Mating doesn't disturb the hysteresis behaviour of the
    underlying FanCoolingBoard."""
    system(ambient_c=70.0)
    assert system(ambient_c=55.0) is True            # deadband, fan stays on
    system(ambient_c=45.0)
    assert system(ambient_c=55.0) is False           # deadband, fan stays off


def test_cooled_system_exposes_cooler_board(system):
    """The cooler board is reachable as a public attribute on the
    assembly, the same pattern WaterAlarmAssembly uses for its
    sensor / controller boards."""
    from fan_cooling import FanCoolingBoard, PowerSourceBoard
    assert isinstance(system.cooler, FanCoolingBoard)
    assert isinstance(system.supply, PowerSourceBoard)
