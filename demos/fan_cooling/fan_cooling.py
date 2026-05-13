"""Fan-cooling module — composable Board demo.

Inspired by TI Designs reference TIDA-00517 ("Basic fan controller
reference design with over-temperature detection",
https://www.ti.com/tool/TIDA-00517).  The whole module is a `Board`
subclass with two pin headers on its surface, so it can be inserted
into a larger circuit by mating its connectors — exactly like the
SensorBoard / ControllerBoard pair in `demos/water_alarm_split.py`.

Architecture
------------
Power comes in on `J1` (VIN, GND) and a fan plugs into `J2` (FAN+,
FAN-).  Internally a TMP302 die-temperature switch decides whether
the chip is over its trip temperature; its open-drain OUT is pulled
to the 3.3 V rail produced by a small zener regulator, then fed
through a single Schmitt-trigger inverter (SN74AHC1G14) to a
low-side N-channel MOSFET that grounds the fan's return leg.

In the framework's voltage-only graph the TMP302's silicon and the
MOSFET's switching aren't simulable, so the three chips and the
MOSFET sit in the BOM as black-box parts and a separate `FanController`
cell models the hysteresis-driven on/off behaviour at the system
level.  The cell drives the FAN- pin of the J2 connector through its
internal face; mating circuits read the J2 surface to see whether
the fan is being commanded on.

Composability
-------------
`FanCoolingBoard` exposes everything a larger design needs as
connector pins.  `CooledSystem` at the bottom of this file shows the
intended pattern: a parent `Circuit` mates the board's connectors,
supplies VIN to J1, and drives the ambient temperature for the
TMP302 through the board's exposed `ambient_c` property.  Run
directly to see a hysteresis walk plus the composed-assembly read-back:

    python demos/fan_cooling.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from wirebench import (
    Board, Circuit, Direction, mate, wire,
    Rail, Resistor,
    D1N4728A,
    Q2N7000,
    TMP302, SN74AHC1G14,
    run_scenarios,
)
from components.connectors.headers import Header1xNFemale, Header1xNMale
from components.chips.concepts.fan_controller import FanController
from framework.registry import register


# --------------------------------------------------------------------------
# Composable Board
# --------------------------------------------------------------------------

class FanCoolingBoard(Board):
    """Temperature-triggered cooling-fan module.

    Connector surface:
        J1 (Header1xNFemale, 2-pin)  — power input
            J1.p1 = VIN  (18.3 V – 27.6 V)
            J1.p2 = GND
        J2 (Header1xNFemale, 2-pin)  — fan output
            J2.p1 = FAN+ (tied internally to VIN — always at the
                          supply rail when the board is powered)
            J2.p2 = FAN- (driven LOW while the controller is
                          asking for the fan to run; HIGH otherwise)

    Reading the board:
        board.ambient_c   →  set/get the temperature the TMP302 sees
        board.fan_on      →  True iff the FanController is commanding
                              the MOSFET on
        board.trip_high_c →  upper hysteresis threshold (60 °C default,
                              matching the TIDA-00517 TMP302A + TripSet
                              configuration)
        board.trip_low_c  →  lower hysteresis threshold (50 °C default)

    Omits __slots__ so `Board.__init__` auto-collects every part from
    `self.__dict__` (Capacitor / Inductor / Resistor / Diode / Chip /
    Connector / Part are all picked up).
    """

    REFDES_PREFIX = 'A'

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        *,
        refdes_number: int,
        trip_high_c: float = 60.0,
        trip_low_c:  float = 50.0,
    ) -> None:
        # Active devices and protection.
        self.u1 = TMP302       (refdes_number=1)   # over-temperature switch
        self.u2 = SN74AHC1G14  (refdes_number=2)   # Schmitt-trigger inverter
        self.q1 = Q2N7000      (refdes_number=1)   # low-side fan-current MOSFET
        self.d1 = D1N4728A     (refdes_number=1)   # 3.3 V zener for the local rail

        # Resistors — values from the TIDA-00517 design guide.
        self.r1 = Resistor(10_000, refdes_number=1)   # zener ballast / current limit
        self.r2 = Resistor(10_000, refdes_number=2)   # TMP302 OUT pull-up to V_3V3
        self.r3 = Resistor(10_000, refdes_number=3)   # MOSFET gate pull-down

        # Connector surface.  Both are female receptacles: power
        # comes in through J1 from a mating power-source board (or
        # bench supply harness); fans plug into J2.
        self.power_in = Header1xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
        self.fan_out  = Header1xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=2)

        # Behavioural controller — encapsulates the TMP302 + inverter
        # + MOSFET signal chain into one hysteretic switch.  The
        # physical parts above sit in the BOM for wirelist fidelity;
        # this cell is what actually drives the FAN- output node.
        self.controller = FanController(
            trip_high_c=trip_high_c, trip_low_c=trip_low_c,
        )

        # ------------------------------------------------------------
        # The board doesn't generate power — VIN arrives on J1.p1
        # from the mating supply, GND on J1.p2.  FAN+ (J2.p1) is the
        # same net as VIN so the fan's positive leg sees the supply
        # whenever the board is powered; the controller drives FAN-
        # (J2.p2) LOW when it's asking the fan to run.  Pin
        # `_effective_role = OUT` on the J2 pins forces Pin.evaluate
        # to always copy internal → external, sidestepping the BIDIR
        # contention check that trips when the external face still
        # holds the previous cycle's value while the internal face
        # is freshly driven this cycle.
        # ------------------------------------------------------------
        wire(self.power_in.pins[0].internal,
             self.fan_out.pins[0].internal)        # VIN bridge: J1.p1 ↔ J2.p1
        wire(self.controller.ports['fan_drive'],
             self.fan_out.pins[1].internal)        # J2.p2 = FAN-

        self.fan_out.pins[1]._effective_role = Direction.OUT

        super().__init__(
            name='Fan Cooling Module',
            revision='A',
            refdes_number=refdes_number,
        )

    # ------------------------------------------------------------------
    # Composable read / write surface
    # ------------------------------------------------------------------

    @property
    def ambient_c(self) -> float:
        return self.controller.temperature_c

    @ambient_c.setter
    def ambient_c(self, value: float) -> None:
        """Set the temperature the TMP302 sees.  In real hardware this
        is just the chip's die temperature; here we expose it as a
        Python-level state so parent circuits can simulate
        thermal scenarios."""
        self.controller._temperature_c = float(value)

    @property
    def fan_on(self) -> bool:
        return self.controller.fan_on

    @property
    def trip_high_c(self) -> float:
        return self.controller.trip_high_c

    @property
    def trip_low_c(self) -> float:
        return self.controller.trip_low_c

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, ambient_c: float) -> bool:
        """Standalone-test surface — set ambient and return fan state.

        Refuses to run while the board's connector pins are mated into
        a parent assembly (standard `_assert_no_inputs_wired` guard);
        a parent should set `board.ambient_c = …` directly and call
        its own evaluate()."""
        self._assert_no_inputs_wired()
        self.ambient_c = ambient_c
        self.evaluate()
        return self.fan_on


# --------------------------------------------------------------------------
# Example composition: power-supply board mated to the fan-cooling board.
# --------------------------------------------------------------------------

@register('PowerSourceBoard')
class PowerSourceBoard(Board):
    """Bench-style 24-V supply on a mating-side connector.

    Single Header1xNMale (P1) with two pins: VIN and GND.  Plugs into
    a FanCoolingBoard's J1 receptacle.  Demonstrates how a larger
    system would deliver power to the cooling module."""

    REFDES_PREFIX = 'A'

    def __init__(self, *, refdes_number: int) -> None:
        self.vcc = Rail(True)
        self.gnd = Rail(False)
        self.plug = Header1xNMale(pin_count=2, pitch_mm=2.54, refdes_number=1)

        wire(self.vcc.ports['out'], self.plug.pins[0].internal)
        wire(self.gnd.ports['out'], self.plug.pins[1].internal)

        super().__init__(
            name='Power Source',
            revision='A',
            refdes_number=refdes_number,
        )


class CooledSystem(Circuit):
    """A power source mated to a fan-cooling module — the composed
    assembly the FanCoolingBoard is designed to slot into.

    External call surface mirrors the standalone board: drive
    `ambient_c` to walk the TMP302's hysteresis curve."""

    def __init__(self) -> None:
        self.supply = PowerSourceBoard (refdes_number=1)
        self.cooler = FanCoolingBoard  (refdes_number=2)

        # Mate the supply's male plug to the cooler's female power
        # receptacle.  Surface ports of both boards are dotted by
        # connector refdes (P1.pN / J1.pN); mate() merges them into
        # the same logical net.
        mate(self.supply.connectors[0], self.cooler.connectors[0])

        super().__init__()

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, ambient_c: float) -> bool:
        """Drive the cooler board's ambient temperature and propagate
        through the assembly.  Returns the fan-on state."""
        self.cooler.ambient_c = float(ambient_c)
        self.evaluate()
        return self.cooler.fan_on

    @property
    def fan_on(self) -> bool:
        return self.cooler.fan_on


# --------------------------------------------------------------------------
# Scenario walks
# --------------------------------------------------------------------------

def _main() -> None:
    print("=" * 80)
    print("Standalone FanCoolingBoard — temperature ramp through hysteresis:")
    print("=" * 80)
    run_scenarios(
        FanCoolingBoard(refdes_number=1),
        scenarios=[
            ("ambient = 25 °C (idle)",            (25.0,)),
            ("ramp to 49 °C (still below trip)",  (49.0,)),
            ("ramp to 55 °C (in deadband)",       (55.0,)),
            ("hit 60 °C — fan should turn on",    (60.0,)),
            ("65 °C (over-temp, fan running)",    (65.0,)),
            ("drop to 55 °C (still in deadband)", (55.0,)),
            ("drop to 50 °C — falling trip",      (50.0,)),
            ("48 °C (fan back off)",              (48.0,)),
            ("back to 25 °C (idle)",              (25.0,)),
        ],
        columns=[
            ("ambient °C", lambda c, a, k: f"{a[0]:>5.1f}"),
            ("fan",        lambda c, a, k: 'RUN' if c.fan_on else '—'),
            ("trip_high",  lambda c, a, k: f"{c.trip_high_c:>4.0f}"),
            ("trip_low",   lambda c, a, k: f"{c.trip_low_c:>4.0f}"),
        ],
    )
    print()
    print("=" * 80)
    print("Composed CooledSystem — supply board mated to fan-cooling board:")
    print("=" * 80)
    run_scenarios(
        CooledSystem(),
        scenarios=[
            ("ambient = 25 °C",   (25.0,)),
            ("ambient = 65 °C",   (65.0,)),
            ("ambient = 55 °C",   (55.0,)),
            ("ambient = 45 °C",   (45.0,)),
        ],
        columns=[
            ("ambient °C", lambda c, a, k: f"{a[0]:>5.1f}"),
            ("fan",        lambda c, a, k: 'RUN' if c.fan_on else '—'),
        ],
    )


if __name__ == '__main__':
    _main()
