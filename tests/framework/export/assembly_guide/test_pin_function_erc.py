"""Pin-function ERC rules in the assembly-guide exporter.

One predicate per `PinFunction` member.  Each test constructs a
minimal `Circuit` that either satisfies or violates the rule, then
checks that `export_to_string(circuit, 'assembly_guide')` raises (or
doesn't raise) `BreadboardIncompatibleError` with the role-appropriate
message.

The stub chips have Analog VCC/GND and a function-specific extra pin;
each test wires through a Rail of the matching signal_type, mirroring
the project convention (see dice.py and doorbell_protector.py) of
declaring `vcc_a = Rail(True, signal_type=Analog)` for Analog supply
pins and `vcc = Rail(True)` for Digital pins.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import ClassVar

import pytest

# Make demos/ importable for any e2e tests that need a real demo.
_DEMOS = Path(__file__).resolve().parents[4] / 'demos'
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))

import components.chips     # noqa: F401 — registry side effects
import components.diodes    # noqa: F401
import components.passives  # noqa: F401

from framework.chip import Chip
from framework.drive_type import DriveType
from framework.errors import BreadboardIncompatibleError
from framework.export import export_to_string
from framework.ground import ELECTRICAL, GroundDomain
from framework.pin import Pin, PinId
from framework.port import Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.signals import Analog, Digital

from wirebench import Circuit, NE555, Rail, Resistor, wire


# ----------------------------------------------------------- stub chips

class _RefChip(Chip):
    """Stub chip with VCC, GND, VREF — used for REFERENCE-rule tests.
    Has no OUT pins so it doesn't trip the behavioural-cell check."""
    REFDES_PREFIX: ClassVar[str] = 'U'
    __slots__ = ('_refdes_number',)

    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(1, 'VCC'),  Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(2, 'GND'),  Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(3, 'VREF'), Direction.IN, domain, mandatory=False, signal_type=Analog),
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    def __call__(self) -> None: pass


class _ClkChip(Chip):
    """Stub chip with VCC, GND, CLKIN — used for CLOCK_IN-rule tests."""
    REFDES_PREFIX: ClassVar[str] = 'U'
    __slots__ = ('_refdes_number',)

    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(1, 'VCC'),   Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(2, 'GND'),   Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(3, 'CLKIN'), Direction.IN, domain, mandatory=False, signal_type=Digital),
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    def __call__(self) -> None: pass


class _ClkChipInternal(_ClkChip):
    """Same as `_ClkChip` but declares the chip has an internal
    oscillator, so the CLOCK_IN pin may be left unwired."""
    INTERNAL_OSCILLATOR: ClassVar[bool] = True


class _NCChip(Chip):
    """Stub chip with VCC, GND, NC — used for NC-rule tests."""
    REFDES_PREFIX: ClassVar[str] = 'U'
    __slots__ = ('_refdes_number',)

    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(1, 'VCC'), Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(2, 'GND'), Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(3, 'NC'),  Direction.IN, domain, mandatory=False, signal_type=Digital),
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    def __call__(self) -> None: pass


# --------------------------------------------------------- POWER / GROUND
# Regression: the refactored walker keeps the existing rule's behaviour.

class _UnwiredVCC(Circuit):
    """Stub chip with VCC unwired — the POWER rule must refuse."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _RefChip(refdes_number=1)
        # GND + VREF wired (so REFERENCE rule passes), VCC deliberately
        # unwired — only the POWER pin should be flagged.
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.gnd_a.out, self.u1.ports['VREF'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_power_rule_refuses_unwired_vcc() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_UnwiredVCC(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'unwired supply pins' in msg
    assert 'VCC' in msg
    assert '+ rail' in msg


class _UnwiredGND(Circuit):
    """Stub chip with GND unwired."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _RefChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'], self.u1.ports['VREF'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_ground_rule_refuses_unwired_gnd() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_UnwiredGND(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'unwired supply pins' in msg
    assert 'GND' in msg
    assert '− rail' in msg


# ---------------------------------------------------------- REFERENCE

class _UnwiredVREF(Circuit):
    """Chip with VREF left unwired — the REFERENCE rule must refuse."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _RefChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        # VREF deliberately floating.
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_reference_rule_refuses_floating_vref() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_UnwiredVREF(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'undriven reference pins' in msg
    assert 'VREF' in msg


class _VREFDirectToRail(Circuit):
    """VREF tied directly to VCC rail — the REFERENCE rule must
    accept this (a Rail is a stable analog source)."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _RefChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'], self.u1.ports['VREF'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_reference_rule_accepts_direct_rail_wiring() -> None:
    # No raise — REFERENCE pin satisfied by direct Rail connection.
    export_to_string(_VREFDirectToRail(), 'assembly_guide')


# --------------------------------------------------------------- RESET
# NE555 has a real RESET pin (pin 4).  Test both violation and
# correct wiring via direct rail tie and via pull-up resistor.

class _NE555FloatingReset(Circuit):
    """NE555 with RESET floating — the RESET rule must refuse.
    NE555's VCC and GND are Analog; RESET is Digital."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = NE555(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        # TRIG / THRES / DISCH / CTRL / OUT not wired (mandatory=False);
        # only RESET floating is the violation under test.
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_reset_rule_refuses_floating_reset() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_NE555FloatingReset(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'floating reset pins' in msg
    assert 'RESET' in msg


class _NE555ResetTiedToVCC(Circuit):
    """NE555 RESET tied directly to a Digital VCC rail — accepted."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.vcc_d = Rail(True)   # Digital, for the RESET pin
        self.u1    = NE555(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.vcc_d.out, self.u1.ports['RESET'])
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.vcc_d, self.u1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_reset_rule_accepts_direct_vcc_tie() -> None:
    export_to_string(_NE555ResetTiedToVCC(), 'assembly_guide')


class _NE555ResetPullUp(Circuit):
    """NE555 RESET pulled up to VCC through a resistor — accepted.
    Resistor terminals are Analog BIDIR, the Rail driving them must
    be Analog too; on the RESET side, the Analog signal is consumed
    by the Digital RESET pin (the framework allows Analog signals to
    cross into Digital pins through a Resistor — the resistor is the
    point where the wire-type discipline relaxes)."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = NE555(refdes_number=1)
        self.r1    = Resistor(10_000, refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        # Pull-up: RESET — R1 — VCC_a.
        wire(self.u1.ports['RESET'], self.r1.ports['t1'])
        wire(self.r1.ports['t2'],    self.vcc_a.out)
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.r1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_reset_rule_accepts_pull_up_resistor_to_vcc() -> None:
    export_to_string(_NE555ResetPullUp(), 'assembly_guide')


class _NE555ResetPullDownToGND(Circuit):
    """RESET pulled to GND through a resistor — NOT accepted.
    The pull is to the wrong rail; the predicate insists on POWER."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = NE555(refdes_number=1)
        self.r1    = Resistor(10_000, refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.u1.ports['RESET'], self.r1.ports['t1'])
        wire(self.r1.ports['t2'],    self.gnd_a.out)
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.r1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_reset_rule_rejects_pull_down_to_gnd() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_NE555ResetPullDownToGND(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'floating reset pins' in msg
    assert 'RESET' in msg


# ------------------------------------------------------------- CLOCK_IN

class _ClkChipFloatingCLKIN(Circuit):
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ClkChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_clock_in_rule_refuses_floating_clkin() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_ClkChipFloatingCLKIN(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'unwired clock-input pins' in msg
    assert 'CLKIN' in msg
    assert 'INTERNAL_OSCILLATOR' in msg


class _ClkChipInternalFloatingCLKIN(Circuit):
    """Same as `_ClkChipFloatingCLKIN` but with INTERNAL_OSCILLATOR on
    the chip class — the rule accepts a floating CLKIN."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ClkChipInternal(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_clock_in_rule_internal_clock_ok_skips_check() -> None:
    export_to_string(_ClkChipInternalFloatingCLKIN(), 'assembly_guide')


# ------------------------------------------------------------------ NC

class _NCChipUnwiredNC(Circuit):
    """NC pin left unwired — the only correct state for an NC pin."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _NCChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        # NC deliberately not wired.
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_nc_rule_accepts_unwired_nc() -> None:
    export_to_string(_NCChipUnwiredNC(), 'assembly_guide')


class _NCChipWiredNC(Circuit):
    """NC pin tied to a Digital GND rail — strict default refuses
    any wiring on an NC pin."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.gnd_d = Rail(False)  # Digital, to match the NC pin's signal_type
        self.u1    = _NCChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.gnd_d.out, self.u1.ports['NC'])
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.gnd_d, self.u1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_nc_rule_refuses_any_wiring() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_NCChipWiredNC(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'no-connect pins wired' in msg
    assert 'NC' in msg
    assert "PIN_FUNCTIONS = {'NC1': None}" in msg


# ============================================== OPEN_DRAIN / OPEN_COLLECTOR
# Stage C — DriveType axis.  Pulls up to + rail mandatory for OD/OC.

class _ODChip(Chip):
    """Stub chip with VCC, GND, plus one OPEN_DRAIN output pin.  Used
    for the OD pull-up ERC tests below."""
    REFDES_PREFIX: ClassVar[str] = 'U'
    PIN_DRIVE_TYPES: ClassVar[dict[str, DriveType]] = {
        'OD_OUT': DriveType.OPEN_DRAIN,
    }
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True
    __slots__ = ('_refdes_number',)

    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(1, 'VCC'),    Direction.IN,  domain, mandatory=False, signal_type=Analog),
            Pin(PinId(2, 'GND'),    Direction.IN,  domain, mandatory=False, signal_type=Analog),
            Pin(PinId(3, 'OD_OUT'), Direction.OUT, domain, mandatory=False, signal_type=Digital),
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    def __call__(self) -> None: pass


class _OCChip(_ODChip):
    """Same as `_ODChip` but declares OPEN_COLLECTOR instead.  Both
    drive types share the same ERC predicate."""
    PIN_DRIVE_TYPES: ClassVar[dict[str, DriveType]] = {
        'OD_OUT': DriveType.OPEN_COLLECTOR,
    }


class _ODChipFloatingOD(Circuit):
    """OPEN_DRAIN pin left unwired — lenient default accepts this."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ODChip(refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        super().__init__(parts=[self.vcc_a, self.gnd_a, self.u1], ports={})
    def __call__(self) -> None: pass


def test_open_drain_rule_accepts_unwired_pin() -> None:
    # Lenient default: an unwired OD pin is treated the same as an
    # unwired PUSH_PULL OUT pin (the framework doesn't flag the
    # latter, so being consistent here).
    export_to_string(_ODChipFloatingOD(), 'assembly_guide')


class _SinkChip(Chip):
    """Stub chip that consumes one IN signal — used as the downstream
    reader for OD-output tests."""
    REFDES_PREFIX: ClassVar[str] = 'U'
    BARE_FIRMWARE_DRIVEN: ClassVar[bool] = True
    __slots__ = ('_refdes_number',)

    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        pins = [
            Pin(PinId(1, 'VCC'), Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(2, 'GND'), Direction.IN, domain, mandatory=False, signal_type=Analog),
            Pin(PinId(3, 'SINK'), Direction.IN, domain, mandatory=False, signal_type=Digital),
        ]
        super().__init__(pins=pins, cells=[])

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    def __call__(self) -> None: pass


class _ODChipNoPullUp(Circuit):
    """OPEN_DRAIN pin wired to an input on another chip with no pull-up
    anywhere on the net — the canonical violation."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ODChip(refdes_number=1)
        self.u2    = _SinkChip(refdes_number=2)
        wire(self.vcc_a.out, self.u1.ports['VCC'], self.u2.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'], self.u2.ports['GND'])
        wire(self.u1.ports['OD_OUT'], self.u2.ports['SINK'])
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.u2],
            ports={},
        )
    def __call__(self) -> None: pass


def test_open_drain_rule_refuses_no_pull_up() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_ODChipNoPullUp(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'open-drain' in msg or 'open-collector' in msg
    assert 'pull-up' in msg
    assert 'OD_OUT' in msg


class _ODChipPullUpToVCC(Circuit):
    """OPEN_DRAIN pin pulled up to + rail through a Resistor — accepted.
    The canonical correctly-wired OD bus."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ODChip(refdes_number=1)
        self.r1    = Resistor(10_000, refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        # OD output → R1 → VCC.
        wire(self.u1.ports['OD_OUT'], self.r1.ports['t1'])
        wire(self.r1.ports['t2'],     self.vcc_a.out)
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.r1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_open_drain_rule_accepts_pull_up_to_vcc() -> None:
    export_to_string(_ODChipPullUpToVCC(), 'assembly_guide')


class _ODChipPullDownToGND(Circuit):
    """OD pin pulled to GND through a Resistor — refused.  The
    predicate insists on a + rail (a pull-down rail does nothing for
    an OD output that can only sink LOW)."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _ODChip(refdes_number=1)
        self.r1    = Resistor(10_000, refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.u1.ports['OD_OUT'], self.r1.ports['t1'])
        wire(self.r1.ports['t2'],     self.gnd_a.out)
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.r1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_open_drain_rule_refuses_pull_down_to_gnd() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_ODChipPullDownToGND(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'OD_OUT' in msg
    assert 'pull-up' in msg


class _OCChipPullUpToVCC(Circuit):
    """OPEN_COLLECTOR same as OPEN_DRAIN — same predicate, same
    acceptance condition (a + rail pull-up)."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _OCChip(refdes_number=1)
        self.r1    = Resistor(10_000, refdes_number=1)
        wire(self.vcc_a.out, self.u1.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'])
        wire(self.u1.ports['OD_OUT'], self.r1.ports['t1'])
        wire(self.r1.ports['t2'],     self.vcc_a.out)
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.r1],
            ports={},
        )
    def __call__(self) -> None: pass


def test_open_collector_rule_accepts_pull_up_to_vcc() -> None:
    export_to_string(_OCChipPullUpToVCC(), 'assembly_guide')


class _OCChipNoPullUp(Circuit):
    """OPEN_COLLECTOR pin wired without a pull-up — refused, same as
    OPEN_DRAIN's negative case."""
    def __init__(self) -> None:
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)
        self.u1    = _OCChip(refdes_number=1)
        self.u2    = _SinkChip(refdes_number=2)
        wire(self.vcc_a.out, self.u1.ports['VCC'], self.u2.ports['VCC'])
        wire(self.gnd_a.out, self.u1.ports['GND'], self.u2.ports['GND'])
        wire(self.u1.ports['OD_OUT'], self.u2.ports['SINK'])
        super().__init__(
            parts=[self.vcc_a, self.gnd_a, self.u1, self.u2],
            ports={},
        )
    def __call__(self) -> None: pass


def test_open_collector_rule_refuses_no_pull_up() -> None:
    with pytest.raises(BreadboardIncompatibleError) as exc_info:
        export_to_string(_OCChipNoPullUp(), 'assembly_guide')
    msg = str(exc_info.value)
    assert 'open-collector' in msg or 'open-drain' in msg
    assert 'pull-up' in msg
    assert 'OD_OUT' in msg
