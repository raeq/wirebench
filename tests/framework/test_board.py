"""Board class tests."""
import pytest

from framework.board import Board
from framework.errors import RefdesError
from components.connectors.headers import Header2xNFemale


def test_empty_board():
    b = Board(name='X', revision='A', components=[], refdes_number=1)
    assert b.refdes == 'A1'
    assert b.ports == {}


def test_board_with_connector_exposes_externals():
    c = Header2xNFemale(pin_count=40, pitch_mm=2.54, refdes_number=1)
    b = Board(name='Test', revision='A', components=[c], refdes_number=1)
    assert all(f'J1.p{i}' in b.ports for i in range(1, 41))


def test_multiple_connectors_no_collision():
    c1 = Header2xNFemale(pin_count=4,  pitch_mm=2.54, refdes_number=1)
    c2 = Header2xNFemale(pin_count=6,  pitch_mm=2.54, refdes_number=2)
    b = Board(name='Test', revision='A', components=[c1, c2], refdes_number=1)
    assert 'J1.p1' in b.ports
    assert 'J2.p1' in b.ports


def test_two_connectors_same_refdes_rejected():
    c1 = Header2xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    c2 = Header2xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1)
    # The Board's own qualified-port collision check fires first; either
    # message indicates the conflict.
    with pytest.raises(RefdesError, match="Duplicate surface port|Duplicate refdes"):
        Board(name='Test', revision='A', components=[c1, c2], refdes_number=1)


def test_board_refdes_prefix_is_A():
    assert Board.REFDES_PREFIX == 'A'
    b = Board(name='X', revision='A', components=[], refdes_number=3)
    assert b.refdes == 'A3'


def test_board_requires_non_empty_name():
    with pytest.raises(ValueError, match="name"):
        Board(name='', revision='A', components=[], refdes_number=1)


def test_board_requires_non_empty_revision():
    with pytest.raises(ValueError, match="revision"):
        Board(name='X', revision='', components=[], refdes_number=1)


def test_board_name_revision_read_only():
    b = Board(name='X', revision='A', components=[], refdes_number=1)
    with pytest.raises(AttributeError):
        b.name = 'Y'
    with pytest.raises(AttributeError):
        b.revision = 'B'
