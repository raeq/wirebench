import pytest


def _board():
    from bldc_motor import BLDCControllerBoard
    return BLDCControllerBoard(refdes_number=1)


def _system():
    from bldc_motor import BLDCSystem
    return BLDCSystem()


@pytest.fixture
def board():
    return _board()


@pytest.fixture
def system():
    return _system()


# ----------------------------------------------------------------------
# Standalone BLDCControllerBoard
# ----------------------------------------------------------------------

def test_bom_present(board):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in board.parts
        if isinstance(fn, RefdesBearing)
    }
    assert "Uno_BLDCCommutator.U1"   in parts
    assert "DRV8313.U2"               in parts
    assert "Header1xNFemale.J1"      in parts
    assert "Header1xNFemale.J2"      in parts
    assert "Header1xNFemale.J3"      in parts
    # Bootstrap caps + bypass + charge-pump caps.
    for n in (1, 2, 3, 4, 5, 6):
        assert f"Capacitor.C{n}" in parts


def test_board_refdes_uses_a_prefix(board):
    """Board carries the IEEE 315 'A' assembly refdes prefix."""
    assert board.refdes == 'A1'


def test_three_connectors_exposed(board):
    """Power, windings, Hall sensors — three mating surfaces."""
    assert len(board.connectors) == 3


def test_starts_in_coast_state(board):
    """No Hall input driven yet — controller must coast (sector 0)."""
    board.evaluate()
    assert board.active_sector == 0


@pytest.mark.parametrize("hall,expected_sector", [
    ((True,  False, True ), 1),
    ((True,  False, False), 2),
    ((True,  True,  False), 3),
    ((False, True,  False), 4),
    ((False, True,  True ), 5),
    ((False, False, True ), 6),
])
def test_each_hall_pattern_maps_to_expected_sector(board, hall, expected_sector):
    assert board(*hall) == expected_sector


@pytest.mark.parametrize("hall", [(False, False, False), (True, True, True)])
def test_invalid_hall_patterns_coast(board, hall):
    assert board(*hall) == 0


def test_sector_1_drives_a_high_and_b_low(board):
    board(True, False, True)
    g = board.gates
    assert g['ah'] is True
    assert g['bl'] is True
    # Phase C idles.
    assert g['en_c'] is False


def test_sector_6_drives_c_high_and_b_low(board):
    board(False, False, True)
    g = board.gates
    assert g['ch'] is True
    assert g['bl'] is True
    assert g['en_a'] is False


def test_walking_sectors_in_sequence(board):
    """The six valid Hall patterns walked in commutation order produce
    sectors 1..6 monotonically — the expected behaviour as the rotor
    advances through one electrical revolution."""
    sequence = [
        (True,  False, True ),   # sector 1
        (True,  False, False),   # 2
        (True,  True,  False),   # 3
        (False, True,  False),   # 4
        (False, True,  True ),   # 5
        (False, False, True ),   # 6
    ]
    for i, hall in enumerate(sequence, start=1):
        assert board(*hall) == i


# ----------------------------------------------------------------------
# Composed BLDCSystem
# ----------------------------------------------------------------------

def test_system_constructs(system):
    assert system is not None


def test_system_walks_through_six_sectors_per_revolution(system):
    sectors = [system(float(a)) for a in (0, 60, 120, 180, 240, 300)]
    assert sectors == [1, 2, 3, 4, 5, 6]


def test_system_returns_to_sector_1_after_full_revolution(system):
    system(0.0)
    assert system.controller.active_sector == 1
    system(360.0)            # wraps mod 360
    assert system.controller.active_sector == 1


def test_system_30deg_step_stays_in_same_sector(system):
    """Within a 60° sector window the commutator must not retrigger
    — the rotor at 30° and 0° should both report sector 1."""
    system(0.0)
    first = system.controller.active_sector
    system(30.0)
    second = system.controller.active_sector
    assert first == second == 1


def test_system_gates_match_sector(system):
    """Sector 3 (B+ C-) at 120°: BH and CL must be the active pair."""
    system(120.0)
    g = system.gates
    assert g['bh'] is True
    assert g['cl'] is True
    assert g['en_a'] is False   # phase A idles in sector 3


def test_system_exposes_controller_and_motor(system):
    """Both subordinate parts are reachable as public
    attributes on the assembly — same pattern WaterAlarmAssembly
    and CooledSystem use."""
    from bldc_motor import BLDCControllerBoard
    from components.chips.concepts.bldc_motor import BLDCMotor
    assert isinstance(system.controller, BLDCControllerBoard)
    assert isinstance(system.motor,      BLDCMotor)


def test_system_mate_connects_three_connector_pairs(system):
    """Supply→J1, motor windings plug→J2, Hall plug→J3 — three
    mated pairs in total."""
    assert len(system.controller.connectors) == 3
