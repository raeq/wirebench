"""mate() function tests — per spec §13."""
from __future__ import annotations

import pytest

from framework.errors import (
    DomainCrossingError, IncompatibleMateError, NodeMergeError,
    PinCountMismatchError, PitchMismatchError,
)
from framework.ground import GroundDomain, ELECTRICAL
from framework.mate import mate
from framework.wire import wire

from components.connectors.headers import (
    Header1xNFemale, Header1xNMale, Header2xNFemale, Header2xNMale,
)
from components.connectors.usb import USBCPlug, USBCReceptacle
from components.connectors.jst_ph import JSTPHBoardSide, JSTPHCableHousing
from components.connectors.jst_xh import JSTXHBoardSide, JSTXHCableHousing


# -- 17. Successful mate, board-to-board --

def test_mate_board_to_board_wires_externals():
    fem = Header2xNFemale(pin_count=10, pitch_mm=2.54, refdes_number=1)
    mal = Header2xNMale  (pin_count=10, pitch_mm=2.54, refdes_number=1)
    mate(fem, mal)
    # Each pair of externals shares a node.
    for i in range(10):
        assert fem.pins[i].external.node is mal.pins[i].external.node


# -- 17b. Successful mate, receptacle to plug --

def test_mate_usbc_receptacle_plug():
    j = USBCReceptacle(refdes_number=1)
    p = USBCPlug      (refdes_number=1)
    mate(j, p)
    for jpin, ppin in zip(j.pins, p.pins):
        assert jpin.external.node is ppin.external.node


# -- 18. Class-level mismatch --

def test_mate_rejects_unrelated_families():
    a = JSTPHBoardSide  (pin_count=4, refdes_number=1)
    b = JSTXHCableHousing(pin_count=4, refdes_number=1)
    with pytest.raises(IncompatibleMateError, match="MATES_WITH|mates with"):
        mate(a, b)


# -- 19. Pin-count mismatch --

def test_mate_rejects_pin_count_mismatch():
    a = JSTPHBoardSide   (pin_count=4, refdes_number=1)
    b = JSTPHCableHousing(pin_count=5, refdes_number=1)
    with pytest.raises(PinCountMismatchError, match="Pin count mismatch"):
        mate(a, b)


# -- 20. Pitch mismatch --

def test_mate_rejects_pitch_mismatch():
    a = Header2xNMale  (pin_count=10, pitch_mm=2.54, refdes_number=1)
    b = Header2xNFemale(pin_count=10, pitch_mm=1.27, refdes_number=1)
    with pytest.raises(PitchMismatchError, match="Pitch mismatch"):
        mate(a, b)


# -- 21. Ground domain mismatch --

def test_mate_rejects_domain_mismatch():
    thermal = GroundDomain('thermal')
    a = Header2xNFemale(pin_count=4, pitch_mm=2.54, refdes_number=1, domain=ELECTRICAL)
    b = Header2xNMale  (pin_count=4, pitch_mm=2.54, refdes_number=1, domain=thermal)
    with pytest.raises(DomainCrossingError, match="domain"):
        mate(a, b)


# -- 22. A connector cannot be mated twice --

def test_mate_cannot_remate_connector_three_way():
    # Three connectors trying to share the same node: first mate
    # succeeds; second mate would merge two existing nodes (fem and
    # mal2 both already on different nodes after their separate first
    # mates).
    fem  = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
    mal1 = Header2xNMale  (pin_count=2, pitch_mm=2.54, refdes_number=1)
    mal2 = Header2xNMale  (pin_count=2, pitch_mm=2.54, refdes_number=2)
    fem2 = Header2xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=2)
    mate(fem,  mal1)
    mate(fem2, mal2)
    # Now fem.p1.external is on node A; mal2.p1.external is on node B
    # via fem2.  Mating fem and mal2 would have to merge A and B.
    with pytest.raises(NodeMergeError, match="would merge two existing nodes"):
        mate(fem, mal2)


# -- 23. declare_mating_pair symmetry --

def test_declare_mating_pair_symmetric():
    assert Header2xNMale.MATES_WITH is Header2xNFemale
    assert Header2xNFemale.MATES_WITH is Header2xNMale
    assert USBCReceptacle.MATES_WITH is USBCPlug
    assert USBCPlug.MATES_WITH is USBCReceptacle
