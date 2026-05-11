from pydantic import validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


# Pin/segment names follow the universal 7-seg-with-DP convention.
_DIGIT_NAMES   = ('dig_1', 'dig_2', 'dig_3', 'dig_4')
_SEGMENT_NAMES = ('seg_a', 'seg_b', 'seg_c', 'seg_d',
                  'seg_e', 'seg_f', 'seg_g', 'seg_dp')


class SegmentMatrix(FactorNode):
    """4-digit × 8-segment common-anode LED matrix cell.

    Each LED is lit when its digit anode is HIGH (sourcing current) and
    its segment cathode is LOW (sinking current).  A LOW digit anode
    blanks the digit regardless of segment state; a HIGH segment line
    holds that segment off regardless of digit state.

    Models the lit pattern only — no V_F or I_F numerics.  Used inside
    chips like Display5641AS.
    """

    __slots__ = ('_ports', '_lit_matrix')

    DIGITS:   int = 4
    SEGMENTS: int = 8

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports = {
            name: Port(name, Direction.IN, domain,
                       mandatory=False, signal_type=Digital)
            for name in _DIGIT_NAMES + _SEGMENT_NAMES
        }
        # 4×8 of None until first evaluate().
        self._lit_matrix: tuple[tuple[bool | None, ...], ...] = tuple(
            tuple(None for _ in range(self.SEGMENTS))
            for _ in range(self.DIGITS)
        )

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def lit_matrix(self) -> tuple[tuple[bool | None, ...], ...]:
        """Row-major: lit_matrix[digit_index][segment_index]."""
        return self._lit_matrix

    def evaluate(self) -> None:
        digits   = tuple(self._ports[n].value for n in _DIGIT_NAMES)
        segments = tuple(self._ports[n].value for n in _SEGMENT_NAMES)
        # Common-anode polarity: lit iff anode HIGH AND cathode LOW.
        # `seg is False` distinguishes a driven-LOW cathode from an
        # undriven (None) one — an undriven cathode does not sink
        # current, so the segment is not lit.
        self._lit_matrix = tuple(
            tuple(bool(dig) and (seg is False) for seg in segments)
            for dig in digits
        )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self,
                 dig_1: bool | None = False, dig_2: bool | None = False,
                 dig_3: bool | None = False, dig_4: bool | None = False,
                 seg_a: bool | None = True,  seg_b: bool | None = True,
                 seg_c: bool | None = True,  seg_d: bool | None = True,
                 seg_e: bool | None = True,  seg_f: bool | None = True,
                 seg_g: bool | None = True,  seg_dp: bool | None = True,
                 ) -> tuple[tuple[bool, ...], ...]:
        self._assert_no_inputs_wired()
        drives = {
            'dig_1': dig_1, 'dig_2': dig_2, 'dig_3': dig_3, 'dig_4': dig_4,
            'seg_a': seg_a, 'seg_b': seg_b, 'seg_c': seg_c, 'seg_d': seg_d,
            'seg_e': seg_e, 'seg_f': seg_f, 'seg_g': seg_g, 'seg_dp': seg_dp,
        }
        for name, value in drives.items():
            self._ports[name].drive(value)
        self.evaluate()
        return self._lit_matrix  # type: ignore[return-value]

    def __repr__(self) -> str:
        return f"SegmentMatrix(lit_matrix={self._lit_matrix!r})"
