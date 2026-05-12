from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.factor import FactorNode
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.registry import register
from framework.signals import Digital


# 60°-wide electrical-angle sectors, each yielding one of the six
# valid Hall patterns expected by a standard 120°-spaced sensor
# layout.  Sectors are 1-indexed to match the Commutator cell's
# `active_sector` so traces line up visually.
#
# Within a sector the pattern is constant; transitions are at the
# 60° boundaries.  An angle outside [0, 360) is taken modulo a full
# electrical revolution before lookup, so external code can advance
# rotor angle freely without worrying about wrap-around.
_SECTOR_HALL_PATTERN: tuple[tuple[bool, bool, bool], ...] = (
    (True,  False, True ),    # sector 1   0°– 60°
    (True,  False, False),    # sector 2  60°–120°
    (True,  True,  False),    # sector 3 120°–180°
    (False, True,  False),    # sector 4 180°–240°
    (False, True,  True ),    # sector 5 240°–300°
    (False, False, True ),    # sector 6 300°–360°
)


@register('BLDCMotor')
class BLDCMotor(FactorNode):
    """Behavioural model of a 3-phase BLDC motor's Hall-sensor face.

    The framework's voltage-only graph can't solve rotor dynamics —
    torque, inertia, back-EMF, winding inductance — so this cell
    models only the *output* side of the motor: given the rotor's
    electrical angle (set as Python state by the surrounding
    composite), it emits the three Hall-sensor signals that an
    ATmega328P-class controller would read on its A0/A1/A2 inputs.

    The cell deliberately ignores the three winding-drive inputs.
    In a real motor the windings exert torque on the rotor and the
    rotor's mechanical inertia integrates that into an angle; in our
    discrete-time, voltage-only graph the demo's scenario walk
    *prescribes* the rotor angle and lets the surrounding hardware
    react to it.

    Ports
    -----
        ha, hb, hc   Digital OUT — three Hall signals at 120° spacing.

    Python state
    ------------
        rotor_angle_deg   electrical-angle position; surrounding
                          composites set this before each evaluate to
                          simulate motion.
    """

    __slots__ = ('_ports', '_rotor_angle_deg')

    SERIALIZE_KWARGS: ClassVar[tuple[str, ...]] = ('initial_angle_deg',)
    _SERIALIZE_ATTRS: ClassVar[dict[str, str]] = {
        'initial_angle_deg': '_rotor_angle_deg',
    }

    SECTOR_COUNT: int = 6

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        initial_angle_deg: float = 0.0,
        domain: GroundDomain = ELECTRICAL,
    ) -> None:
        self._rotor_angle_deg: float = float(initial_angle_deg) % 360.0
        self._ports = {
            'ha': Port('ha', Direction.OUT, domain, mandatory=False, signal_type=Digital),
            'hb': Port('hb', Direction.OUT, domain, mandatory=False, signal_type=Digital),
            'hc': Port('hc', Direction.OUT, domain, mandatory=False, signal_type=Digital),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def rotor_angle_deg(self) -> float:
        return self._rotor_angle_deg

    @rotor_angle_deg.setter
    def rotor_angle_deg(self, value: float) -> None:
        self._rotor_angle_deg = float(value) % 360.0

    @property
    def active_sector(self) -> int:
        """1..6 sector index that currently encloses the rotor angle."""
        return int(self._rotor_angle_deg // 60.0) + 1

    @property
    def hall_pattern(self) -> tuple[bool, bool, bool]:
        """Current (HA, HB, HC) triple as plain booleans."""
        sector_index = int(self._rotor_angle_deg // 60.0) % self.SECTOR_COUNT
        return _SECTOR_HALL_PATTERN[sector_index]

    def evaluate(self) -> None:
        pattern = self.hall_pattern
        self._ports['ha'].drive(pattern[0])
        self._ports['hb'].drive(pattern[1])
        self._ports['hc'].drive(pattern[2])

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        rotor_angle_deg: Annotated[float, Field(ge=0)] | None = None,
    ) -> tuple[bool, bool, bool]:
        """Standalone-test invocation: optionally set a new rotor
        angle, evaluate, and return the resulting Hall pattern."""
        self._assert_no_inputs_wired()
        if rotor_angle_deg is not None:
            self.rotor_angle_deg = rotor_angle_deg
        self.evaluate()
        return self.hall_pattern

    def __repr__(self) -> str:
        return (f"BLDCMotor(rotor_angle_deg={self._rotor_angle_deg!r}, "
                f"sector={self.active_sector})")
