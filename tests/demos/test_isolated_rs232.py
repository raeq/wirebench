import pytest


def _board():
    from isolated_rs232 import IsolatedRS232Board
    return IsolatedRS232Board(refdes_number=1)


def _link():
    from isolated_rs232 import IsolatedRS232Link
    return IsolatedRS232Link()


@pytest.fixture
def board():
    return _board()


@pytest.fixture
def link():
    return _link()


# ----------------------------------------------------------------------
# Standalone IsolatedRS232Board
# ----------------------------------------------------------------------

def test_bom_present(board):
    from framework.refdes import RefdesBearing
    parts = {
        f"{type(fn).__name__}.{fn.refdes}"
        for fn in board._factor_nodes
        if isinstance(fn, RefdesBearing)
    }
    assert "ISOW7841.U1"          in parts
    assert "TRS3122E.U2"          in parts
    assert "Header1xNFemale.J1"   in parts
    assert "Header1xNFemale.J2"   in parts
    # Bypass + charge-pump caps.
    for n in (1, 2, 3, 4, 5, 6, 7):
        assert f"Capacitor.C{n}" in parts


def test_board_refdes_uses_a_prefix(board):
    assert board.refdes == 'A1'


def test_two_connectors_exposed(board):
    """One controller-side, one iso-side — the whole point of the
    board."""
    assert len(board.connectors) == 2


def test_two_distinct_domains_are_used(board):
    from isolated_rs232 import ISOLATED
    from framework.ground import ELECTRICAL
    assert board.j_logic.pins[0].external.domain is ELECTRICAL
    assert board.j_iso  .pins[0].external.domain is ISOLATED
    assert ELECTRICAL is not ISOLATED


def test_isow7841_straddles_the_barrier(board):
    """U1's logic-side and iso-side pins must end up in different
    domains — verifying the chip honoured the constructor args the
    board passed in."""
    from isolated_rs232 import ISOLATED
    from framework.ground import ELECTRICAL
    pins = {p.id.name: p for p in board.u1.pins}
    assert pins['INA' ].external.domain is ELECTRICAL
    assert pins['OUTA'].external.domain is ISOLATED


def test_idle_inputs_propagate_low_outputs(board):
    out = board(False, False)
    assert bool(out['line_tx']) is False
    assert bool(out['host_rx']) is False


def test_tx_high_propagates_to_line(board):
    """A logic-side TXD = 1 must reach the RS-232 line-out (J2.p1)
    through ISOW7841 channel A and TRS3122E TX1."""
    out = board(True, False)
    assert bool(out['line_tx']) is True


def test_rx_high_propagates_back_to_host(board):
    """A line-side RIN = 1 must reach the logic-side RX (J1.p4)
    through TRS3122E RX1 and ISOW7841 channel D."""
    out = board(False, True)
    assert bool(out['host_rx']) is True


def test_independent_tx_and_rx_paths(board):
    """Driving both inputs HIGH must light up both outputs — the
    forward and reverse paths must not interfere."""
    out = board(True, True)
    assert bool(out['line_tx']) is True
    assert bool(out['host_rx']) is True


def test_return_to_idle(board):
    board(True, True)
    out = board(False, False)
    assert bool(out['line_tx']) is False
    assert bool(out['host_rx']) is False


# ----------------------------------------------------------------------
# Composed IsolatedRS232Link
# ----------------------------------------------------------------------

def test_link_constructs(link):
    assert link is not None


def test_link_exposes_three_boards(link):
    from isolated_rs232 import (
        ControllerSourceBoard, IsolatedRS232Board, RS232CableBoard,
    )
    assert isinstance(link.host,      ControllerSourceBoard)
    assert isinstance(link.iso_rs232, IsolatedRS232Board)
    assert isinstance(link.cable,     RS232CableBoard)


def test_link_propagates_host_tx_to_line(link):
    out = link(True, False)
    assert bool(out['line_tx']) is True


def test_link_propagates_cable_rin_to_host(link):
    out = link(False, True)
    assert bool(out['host_rx']) is True


def test_link_full_bidirectional(link):
    out = link(True, True)
    assert bool(out['line_tx']) is True
    assert bool(out['host_rx']) is True


def test_link_idle(link):
    out = link(False, False)
    assert bool(out['line_tx']) is False
    assert bool(out['host_rx']) is False
