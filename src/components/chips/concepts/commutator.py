from pydantic import validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.signals import Digital


# Standard 120° Hall encoding for a 3-phase BLDC motor: at each rotor
# position one Hall sensor sees the north pole, one sees the south,
# and one sits on the boundary.  The six valid Hall patterns map 1-1
# onto the six 60° electrical sectors; (0,0,0) and (1,1,1) are
# unreachable with the sensors mounted correctly and indicate a wiring
# fault.
#
# For each valid sector we drive exactly two phases — one high-side,
# one low-side — leaving the third high-impedance via its enable line.
# Convention: AH/BH/CH command the high-side switch of phases A/B/C;
# AL/BL/CL command the low-side; en_a/en_b/en_c gate the whole
# half-bridge (LOW = phase coasts).
#
# The table below is the textbook six-step trapezoidal sequence.
_SECTOR_TABLE: dict[tuple[bool, bool, bool], dict[str, bool]] = {
    # (ha, hb, hc): drive command per output line.
    (True,  False, True ): {'ah': True,  'al': False, 'bh': False, 'bl': True,
                            'ch': False, 'cl': False, 'en_a': True,
                            'en_b': True,  'en_c': False},   # sector 1: A+ B-
    (True,  False, False): {'ah': True,  'al': False, 'bh': False, 'bl': False,
                            'ch': False, 'cl': True,  'en_a': True,
                            'en_b': False, 'en_c': True },   # sector 2: A+ C-
    (True,  True,  False): {'ah': False, 'al': False, 'bh': True,  'bl': False,
                            'ch': False, 'cl': True,  'en_a': False,
                            'en_b': True,  'en_c': True },   # sector 3: B+ C-
    (False, True,  False): {'ah': False, 'al': True,  'bh': True,  'bl': False,
                            'ch': False, 'cl': False, 'en_a': True,
                            'en_b': True,  'en_c': False},   # sector 4: B+ A-
    (False, True,  True ): {'ah': False, 'al': True,  'bh': False, 'bl': False,
                            'ch': True,  'cl': False, 'en_a': True,
                            'en_b': False, 'en_c': True },   # sector 5: C+ A-
    (False, False, True ): {'ah': False, 'al': False, 'bh': False, 'bl': True,
                            'ch': True,  'cl': False, 'en_a': False,
                            'en_b': True,  'en_c': True },   # sector 6: C+ B-
}

# When the rotor is between sectors or sensors disagree (000 / 111),
# every gate is held LOW and every half-bridge enable is HIGH-impedance
# (LOW).  This is the safe coast state — no two transistors fight, no
# winding gets a short pulse.
_FAULT_OUTPUT: dict[str, bool] = {
    'ah': False, 'al': False, 'bh': False, 'bl': False,
    'ch': False, 'cl': False,
    'en_a': False, 'en_b': False, 'en_c': False,
}

_INPUT_NAMES  = ('ha', 'hb', 'hc')
_OUTPUT_NAMES = ('ah', 'al', 'bh', 'bl', 'ch', 'cl', 'en_a', 'en_b', 'en_c')


class Commutator(Part):
    """Six-step BLDC commutation table — Hall-pattern → gate drive.

    Reads three Hall-sensor signals and writes six gate-command
    outputs plus three per-phase enables.  Drop-in firmware model for
    an MCU running the textbook trapezoidal commutation loop: lookup
    is purely combinational, the active sector is determined entirely
    by the Hall pattern, and unreachable patterns (all-LOW, all-HIGH)
    fall back to a coast state with every enable LOW.

    Designed to be embedded inside an ATmega328P subclass (or any
    other Chip the framework supports), the same way
    `Uno_ThermometerSketch` embeds the firmware model in the
    digital-thermometer demo.

    Ports
    -----
        ha, hb, hc      Digital IN  — Hall-sensor inputs.
        ah, al          Digital OUT — phase-A high / low gate commands.
        bh, bl          Digital OUT — phase-B high / low gate commands.
        ch, cl          Digital OUT — phase-C high / low gate commands.
        en_a, en_b, en_c Digital OUT — half-bridge enables; LOW idles
                                       the phase (high-Z).
    """

    __slots__ = ('_ports', '_active_sector')

    SECTOR_COUNT: int = 6

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        self._ports: dict[str, Port] = {}
        for name in _INPUT_NAMES:
            self._ports[name] = Port(name, Direction.IN, domain,
                                     mandatory=False, signal_type=Digital)
        for name in _OUTPUT_NAMES:
            self._ports[name] = Port(name, Direction.OUT, domain,
                                     mandatory=False, signal_type=Digital)
        # 0 ≤ sector ≤ 6 — 1..6 for valid Hall patterns, 0 for the
        # coast / fault state.  Useful for tests and trace output.
        self._active_sector: int = 0

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def active_sector(self) -> int:
        """1..6 for a valid commutation sector, 0 for the coast state."""
        return self._active_sector

    def evaluate(self) -> None:
        hall: tuple[bool, bool, bool] = tuple(  # type: ignore[assignment]
            bool(Digital(self._ports[n].value)) for n in _INPUT_NAMES
        )
        drive = _SECTOR_TABLE.get(hall, _FAULT_OUTPUT)
        # Map the Hall pattern back to a 1-based sector index for
        # tracing; the dict iteration is over insertion order so the
        # index matches the table comments above.
        keys = list(_SECTOR_TABLE.keys())
        self._active_sector = keys.index(hall) + 1 if hall in _SECTOR_TABLE else 0
        for name, value in drive.items():
            self._ports[name].drive(value)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, ha: bool, hb: bool, hc: bool) -> dict[str, bool]:
        """Standalone-test invocation — drive the Hall inputs, run the
        lookup, and return every gate-command output as a dict."""
        self._assert_no_inputs_wired()
        self._ports['ha'].drive(ha)
        self._ports['hb'].drive(hb)
        self._ports['hc'].drive(hc)
        self.evaluate()
        return {name: bool(self._ports[name].value) for name in _OUTPUT_NAMES}

    def __repr__(self) -> str:
        return f"Commutator(active_sector={self._active_sector})"
