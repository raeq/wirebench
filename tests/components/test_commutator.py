import pytest

from components.chips.concepts.commutator import Commutator
from framework.port import Direction


# Expected (active_sector, A-side, B-side, C-side) per Hall pattern,
# where the side flags are which transistor of that phase is asked
# to conduct.  Sectors 1..6 cover the 60°-wide windows of a
# 120°-spaced Hall layout; (0,0,0) and (1,1,1) are unreachable with
# a healthy sensor mount and must coast.
EXPECTED = {
    # (ha, hb, hc): (sector, ah, al, bh, bl, ch, cl, en_a, en_b, en_c)
    (True,  False, True ): (1, True,  False, False, True,  False, False, True,  True,  False),
    (True,  False, False): (2, True,  False, False, False, False, True,  True,  False, True ),
    (True,  True,  False): (3, False, False, True,  False, False, True,  False, True,  True ),
    (False, True,  False): (4, False, True,  True,  False, False, False, True,  True,  False),
    (False, True,  True ): (5, False, True,  False, False, True,  False, True,  False, True ),
    (False, False, True ): (6, False, False, False, True,  True,  False, False, True,  True ),
    (False, False, False): (0, False, False, False, False, False, False, False, False, False),
    (True,  True,  True ): (0, False, False, False, False, False, False, False, False, False),
}


def test_construction_starts_in_coast_state():
    c = Commutator()
    assert c.active_sector == 0


def test_ports_have_correct_directions():
    c = Commutator()
    for name in ('ha', 'hb', 'hc'):
        assert c.ports[name].direction is Direction.IN
    for name in ('ah', 'al', 'bh', 'bl', 'ch', 'cl', 'en_a', 'en_b', 'en_c'):
        assert c.ports[name].direction is Direction.OUT


@pytest.mark.parametrize("hall_pattern,expected", list(EXPECTED.items()))
def test_table_lookup(hall_pattern, expected):
    """Every Hall pattern (valid and fault) must produce the right
    gate commands and sector index."""
    c = Commutator()
    ha, hb, hc = hall_pattern
    out = c(ha=ha, hb=hb, hc=hc)
    sector, ah, al, bh, bl, ch, cl, en_a, en_b, en_c = expected
    assert c.active_sector == sector
    assert out['ah']   is ah
    assert out['al']   is al
    assert out['bh']   is bh
    assert out['bl']   is bl
    assert out['ch']   is ch
    assert out['cl']   is cl
    assert out['en_a'] is en_a
    assert out['en_b'] is en_b
    assert out['en_c'] is en_c


def test_each_valid_sector_drives_exactly_one_high_and_one_low():
    """The trapezoidal commutation sequence has one high-side and
    one low-side switch active at any moment — never two of the
    same kind."""
    c = Commutator()
    for hall_pattern, expected in EXPECTED.items():
        if expected[0] == 0:
            continue   # fault state: no switches active
        out = c(*hall_pattern)
        highs = sum(1 for k in ('ah', 'bh', 'ch') if out[k])
        lows  = sum(1 for k in ('al', 'bl', 'cl') if out[k])
        assert highs == 1, f"Hall {hall_pattern}: {highs} high-side switches"
        assert lows  == 1, f"Hall {hall_pattern}: {lows} low-side switches"


def test_each_valid_sector_idles_exactly_one_phase():
    """One phase is high-Z (both EN low) per sector — that's the
    untouched winding that's free to back-EMF."""
    c = Commutator()
    for hall_pattern, expected in EXPECTED.items():
        if expected[0] == 0:
            continue
        out = c(*hall_pattern)
        idle_phases = sum(1 for k in ('en_a', 'en_b', 'en_c') if not out[k])
        assert idle_phases == 1, f"Hall {hall_pattern}: {idle_phases} idled phases"


def test_fault_state_disables_every_phase():
    """All-zero and all-one Hall readings must blank every enable
    (coast / fault state)."""
    c = Commutator()
    for fault_pattern in ((False, False, False), (True, True, True)):
        c(*fault_pattern)
        for name in ('en_a', 'en_b', 'en_c'):
            assert bool(c.ports[name].value) is False
        for name in ('ah', 'al', 'bh', 'bl', 'ch', 'cl'):
            assert bool(c.ports[name].value) is False


def test_active_sector_property_is_one_indexed():
    c = Commutator()
    c(True, False, True)
    assert c.active_sector == 1
    c(False, False, True)
    assert c.active_sector == 6


def test_repr_includes_sector():
    c = Commutator()
    c(True, False, True)
    assert 'active_sector=1' in repr(c)
