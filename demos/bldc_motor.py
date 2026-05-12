"""Hall-sensored three-phase BLDC motor controller — composable demo.

The canonical hobbyist BLDC topology: an ATmega328P reads three
Hall-effect sensors, looks up the six-step trapezoidal commutation
table, and drives a DRV8313 three-channel half-bridge driver that
switches the motor windings.  Not anchored to a specific TI Designs
reference (modern TI BLDC references are largely sensorless FOC); the
architecture is the one you'll find in countless Arduino BLDC
projects, built here with real TI / Microchip parts so the BOM and
wirelist are honest.

Composable layout
-----------------
`BLDCControllerBoard` is a `Board` subclass with three connector
surfaces:

    J1 (Header1xNFemale, 2-pin) — power input  (VIN, GND)
    J2 (Header1xNFemale, 3-pin) — motor windings (OUT1, OUT2, OUT3)
    J3 (Header1xNFemale, 3-pin) — Hall sensors  (HA, HB, HC)

A larger assembly mates the boards' connectors together.  `BLDCSystem`
at the bottom of this file shows the pattern: a `PowerSourceBoard`
plug mates into J1 and a `BLDCMotor` cell sits in the parent circuit
with its Hall outputs wired into J3 and the controller's J2 winding
outputs flowing back into the motor's winding-input pins for BOM
fidelity (the framework's voltage-only graph doesn't drive the
windings electrically — the motor's rotor angle is the only thing
that actually advances state).

Run directly to see the rotor walked through one electrical
revolution at 30° steps; the commutator's `active_sector` ticks 1..6
and the gate-output column shows which two phases are conducting in
each step:

    python demos/bldc_motor.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from circuitry import (
    Chip, Circuit, Board,
    Direction, Pin, PinId,
    GroundDomain, ELECTRICAL,
    RefdesNumber, validate_refdes,
    Rail, Resistor, Capacitor,
    ATmega328P, DRV8313,
    mate, wire,
    run_scenarios,
)
from framework.port_map import PortMap
from components.connectors.headers import Header1xNFemale, Header1xNMale
from components.chips.concepts.commutator import Commutator
from components.chips.concepts.bldc_motor import BLDCMotor


# ---------------------------------------------------------------------------
# ATmega328P loaded with the BLDC commutation firmware.
# ---------------------------------------------------------------------------

class Uno_BLDCCommutator(ATmega328P):
    """ATmega328P running the Hall-driven six-step commutation loop.

    Same DIP-28 silicon and pinout as a stock ATmega328P; the only
    difference is that an internal `Commutator` concept cell decodes
    the three Hall inputs (read on Arduino A0/A1/A2 = ATmega PC0/PC1/
    PC2) and drives the nine DRV8313 control lines on Arduino D2..D7
    (low-/high-side gate commands) and D8..D10 (per-phase enables).

    Same trick as `Uno_ThermometerSketch` in the digital-thermometer
    demo: skip `ATmega328P.__init__` (which finalises `Chip` with
    cells=[]) and call `Chip.__init__` directly with the firmware cell
    included.  Pin `_effective_role` is fixed to IN on the Hall
    inputs and OUT on the gate / enable outputs so `Pin.evaluate`
    deterministically copies signal across the bond wire each cycle
    instead of tripping its BIDIR contention check on the previous
    cycle's stale value.
    """

    __slots__ = ('_commutator',)

    # ATmega328P pin name → Commutator port the firmware wires it to.
    _GATE_OUTPUTS: dict[str, str] = {
        'PD2': 'al',   'PD3': 'ah',
        'PD4': 'bl',   'PD5': 'bh',
        'PD6': 'cl',   'PD7': 'ch',
        'PB0': 'en_a', 'PB1': 'en_b', 'PB2': 'en_c',
    }
    _HALL_INPUTS: dict[str, str] = {
        'PC0': 'ha', 'PC1': 'hb', 'PC2': 'hc',
    }

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._commutator = Commutator(domain)

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        # Firmware-driven outputs: commutator port drives the pin's
        # internal face, the pin then bonds out to the external pad.
        for pin_name, port_name in self._GATE_OUTPUTS.items():
            pin = by_name[pin_name]
            wire(self._commutator.ports[port_name], pin.internal)
            pin._effective_role = Direction.OUT

        # Hall inputs: external pad drives the pin, internal face
        # bonds onto the commutator's input port.
        for pin_name, port_name in self._HALL_INPUTS.items():
            pin = by_name[pin_name]
            wire(pin.internal, self._commutator.ports[port_name])
            pin._effective_role = Direction.IN

        Chip.__init__(self, pins=pins, cells=[self._commutator])

    @property
    def commutator(self) -> Commutator:
        return self._commutator

    @property
    def active_sector(self) -> int:
        return self._commutator.active_sector

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, ha: bool, hb: bool, hc: bool) -> int:
        """Standalone-test invocation: drive the three Hall input pins
        and return the resulting commutation sector (1..6, or 0 for
        the fault / coast state)."""
        self._assert_no_inputs_wired()
        self._ports['PC0'].drive(ha)
        self._ports['PC1'].drive(hb)
        self._ports['PC2'].drive(hc)
        self.evaluate()
        return self._commutator.active_sector

    def __repr__(self) -> str:
        return (f"Uno_BLDCCommutator(refdes={self.refdes!r}, "
                f"sector={self._commutator.active_sector})")


# ---------------------------------------------------------------------------
# Composable controller board.
# ---------------------------------------------------------------------------

class BLDCControllerBoard(Board):
    """Three-phase BLDC motor controller — composable.

    Surface:
        J1 (Header1xNFemale, 2-pin) — VIN, GND.
        J2 (Header1xNFemale, 3-pin) — motor windings (OUT1, OUT2, OUT3
            tap straight off DRV8313's output stage).
        J3 (Header1xNFemale, 3-pin) — Hall-sensor inputs (HA, HB, HC).

    The Hall inputs land on the ATmega328P's A0/A1/A2 pins (PC0/PC1/
    PC2 in datasheet notation).  The ATmega's nine commutation-output
    pins (D2..D7 for the six gates, D8..D10 for the three half-bridge
    enables) drive the corresponding DRV8313 inputs.

    Omits `__slots__` so `Board.__init__` auto-collects every part
    from `self.__dict__` (the chip subclass, the DRV8313, the
    bypass / bootstrap capacitors, and the three connectors).
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, *, refdes_number: int) -> None:
        # Programmed microcontroller + half-bridge driver IC.
        self.mcu = Uno_BLDCCommutator(refdes_number=1)
        self.drv = DRV8313         (refdes_number=2)

        # DRV8313 needs an external bootstrap capacitor on each phase
        # (BST1/2/3) for the high-side gate-drive supply, plus charge-
        # pump and bypass capacitors.  Values pulled straight from the
        # DRV8313 datasheet application section.
        self.c_bst1 = Capacitor(10e-9,  refdes_number=1)  # phase-A bootstrap
        self.c_bst2 = Capacitor(10e-9,  refdes_number=2)
        self.c_bst3 = Capacitor(10e-9,  refdes_number=3)
        self.c_cp   = Capacitor(10e-9,  refdes_number=4)  # charge-pump flying cap
        self.c_vcp  = Capacitor(100e-9, refdes_number=5)  # VCP storage
        self.c_vm   = Capacitor(10e-6,  refdes_number=6)  # VM bulk decoupling

        # MCU reset-pin pull-up.
        self.r_reset = Resistor(10_000, refdes_number=1)

        # Three connectors comprise the entire surface — mating
        # systems plug power into J1, the BLDC motor's windings into
        # J2, and the Hall-sensor harness into J3.
        self.power_in   = Header1xNFemale(pin_count=2, pitch_mm=2.54, refdes_number=1)
        self.windings   = Header1xNFemale(pin_count=3, pitch_mm=2.54, refdes_number=2)
        self.hall_input = Header1xNFemale(pin_count=3, pitch_mm=2.54, refdes_number=3)

        # --------------------------------------------------------------
        # Wire the MCU's gate-command pins to the DRV8313 inputs.
        # Each ATmega digital pin sits on the same net as the DRV8313
        # input pin it commands; the pin numbering matches the
        # Arduino-style firmware that drives them.
        # --------------------------------------------------------------
        wire(self.mcu.ports['PD2'], self.drv.ports['IN1'])  # AL  → phase-A low-side
        wire(self.mcu.ports['PD3'], self.drv.ports['IN2'])  # AH  → phase-A high-side
        wire(self.mcu.ports['PD4'], self.drv.ports['IN3'])  # BL
        wire(self.mcu.ports['PD5'], self.drv.ports['IN4'])  # BH
        wire(self.mcu.ports['PD6'], self.drv.ports['IN5'])  # CL
        wire(self.mcu.ports['PD7'], self.drv.ports['IN6'])  # CH
        wire(self.mcu.ports['PB0'], self.drv.ports['EN1'])  # EN_A
        wire(self.mcu.ports['PB1'], self.drv.ports['EN2'])  # EN_B
        wire(self.mcu.ports['PB2'], self.drv.ports['EN3'])  # EN_C

        # --------------------------------------------------------------
        # Hall inputs come in on J3 and land on PC0/PC1/PC2.
        # Connector pins are conductors — both faces BIDIR Analog
        # wildcards — so wire() accepts the Digital-typed MCU pin on
        # the same net via the conductor-wildcard rule.
        # --------------------------------------------------------------
        wire(self.hall_input.pins[0].internal, self.mcu.ports['PC0'])  # HA
        wire(self.hall_input.pins[1].internal, self.mcu.ports['PC1'])  # HB
        wire(self.hall_input.pins[2].internal, self.mcu.ports['PC2'])  # HC

        # --------------------------------------------------------------
        # Motor windings flow out through J2.  In real hardware these
        # connect to DRV8313's OUT1/2/3 pins; the framework treats the
        # connector pins as conductor wildcards so the BOM-listed
        # OUT pins still appear on the wirelist, just opaque.
        # --------------------------------------------------------------
        wire(self.drv.ports['OUT1'], self.windings.pins[0].internal)
        self.windings.pins[0]._effective_role = Direction.OUT
        wire(self.drv.ports['OUT2'], self.windings.pins[1].internal)
        self.windings.pins[1]._effective_role = Direction.OUT
        wire(self.drv.ports['OUT3'], self.windings.pins[2].internal)
        self.windings.pins[2]._effective_role = Direction.OUT

        super().__init__(
            name='BLDC Controller',
            revision='A',
            refdes_number=refdes_number,
        )

        # The framework's topological sort, when it sees the J3
        # pins' BIDIR-with-no-external-net configuration, defaults
        # `_effective_role = OUT` on each (it's optimised for the
        # case where the connector is mated and the external side
        # has nothing connected).  Override to IN so Pin.evaluate
        # copies external → internal — that's the direction Hall
        # signals actually flow when this board is used standalone
        # or has its J3 mated to a sensor harness on the outside.
        for pin in self.hall_input.pins:
            pin._effective_role = Direction.IN

    # ------------------------------------------------------------------
    # Composable read accessors
    # ------------------------------------------------------------------

    @property
    def active_sector(self) -> int:
        """Six-step sector the commutator currently asserts (1..6;
        0 for the safe coast / fault state)."""
        return self.mcu.active_sector

    @property
    def gates(self) -> dict[str, bool]:
        """Snapshot of the nine DRV8313 control inputs."""
        commutator = self.mcu.commutator
        return {name: bool(commutator.ports[name].value)
                for name in ('ah', 'al', 'bh', 'bl', 'ch', 'cl',
                             'en_a', 'en_b', 'en_c')}

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, ha: bool, hb: bool, hc: bool) -> int:
        """Standalone-test surface: drive each Hall input straight
        onto J3's *internal* bond (which already shares the node with
        the MCU's PC0/1/2 external pad) and read back the resulting
        commutation sector.

        Driving the external pad would normally be the right surface
        for a user, but with the J3 receptacle unmated the topo sort's
        ordering puts MCU.PC0 before the connector pin's evaluate, so
        the external→internal propagation through the bond wire would
        lag the commutator by one evaluate.  Driving the internal
        side lands the value on the same node and sidesteps the lag —
        for tests this is exactly the signal a mated Hall harness
        would present anyway.
        """
        self._assert_no_inputs_wired()
        self.hall_input.pins[0].internal.drive(ha)
        self.hall_input.pins[1].internal.drive(hb)
        self.hall_input.pins[2].internal.drive(hc)
        self.evaluate()
        return self.active_sector


# ---------------------------------------------------------------------------
# Example composition: power supply + motor + controller board.
# ---------------------------------------------------------------------------

class PowerSourceBoard(Board):
    """Bench-style supply on a mating-side connector — 24 V on a
    Header1xNMale, plugs into a BLDCControllerBoard's J1 receptacle.
    Symmetric to `fan_cooling.PowerSourceBoard`."""

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


class BLDCSystem(Circuit):
    """Composed assembly: power supply mated to the controller board,
    plus a `BLDCMotor` cell whose Hall outputs feed the controller's
    J3 receptacle through a Header1xNMale plug.

    Demonstrates the BLDCControllerBoard plugged into a larger system
    the way `WaterAlarmAssembly` and `CooledSystem` do for their
    respective boards.  `__call__(rotor_angle_deg)` walks the rotor
    through electrical angle and returns the commutator's sector
    decision; the demo's scenario table reads back the gate states
    so you can see which two phases are driving each step."""

    def __init__(self) -> None:
        self.supply     = PowerSourceBoard   (refdes_number=1)
        self.controller = BLDCControllerBoard(refdes_number=2)

        # The motor stand-in — a behavioural BLDCMotor cell whose
        # rotor-angle Python state we advance in __call__.  A mating
        # 3-pin male plug carries its Hall outputs into J3 of the
        # controller; for BOM fidelity the motor's "winding inputs"
        # are also wired out through a second plug, even though our
        # voltage-only graph doesn't simulate torque or back-EMF.
        self.motor      = BLDCMotor()
        self.hall_plug  = Header1xNMale(pin_count=3, pitch_mm=2.54, refdes_number=2)
        self.motor_plug = Header1xNMale(pin_count=3, pitch_mm=2.54, refdes_number=3)

        wire(self.motor.ports['ha'], self.hall_plug.pins[0].internal)
        wire(self.motor.ports['hb'], self.hall_plug.pins[1].internal)
        wire(self.motor.ports['hc'], self.hall_plug.pins[2].internal)
        for pin in self.hall_plug.pins:
            pin._effective_role = Direction.OUT

        # Mate every connector pair on the assembly.
        mate(self.supply.connectors[0],     self.controller.connectors[0])
        mate(self.controller.connectors[1], self.motor_plug)
        mate(self.controller.connectors[2], self.hall_plug)

        super().__init__()

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, rotor_angle_deg: float) -> int:
        """Advance the rotor to `rotor_angle_deg` electrical degrees,
        propagate, return the commutator's active sector (1..6)."""
        self.motor.rotor_angle_deg = rotor_angle_deg
        self.evaluate()
        return self.controller.active_sector

    @property
    def gates(self) -> dict[str, bool]:
        return self.controller.gates


# ---------------------------------------------------------------------------
# Scenario walks
# ---------------------------------------------------------------------------

def _gate_summary(gates: dict[str, bool]) -> str:
    """Return a compact 'A+ B-' style label for the active drive."""
    high = next((p for p in 'abc' if gates[f'{p}h']), None)
    low  = next((p for p in 'abc' if gates[f'{p}l']), None)
    if high is None and low is None:
        return 'coast'
    return f"{(high or '?').upper()}+ {(low or '?').upper()}-"


def _main() -> None:
    print("=" * 80)
    print("Standalone BLDCControllerBoard — drive each Hall pattern directly:")
    print("=" * 80)
    run_scenarios(
        BLDCControllerBoard(refdes_number=1),
        scenarios=[
            ("Hall 101 — sector 1 (A+ B-)", (True,  False, True )),
            ("Hall 100 — sector 2 (A+ C-)", (True,  False, False)),
            ("Hall 110 — sector 3 (B+ C-)", (True,  True,  False)),
            ("Hall 010 — sector 4 (B+ A-)", (False, True,  False)),
            ("Hall 011 — sector 5 (C+ A-)", (False, True,  True )),
            ("Hall 001 — sector 6 (C+ B-)", (False, False, True )),
            ("Hall 000 — fault (coast)",    (False, False, False)),
            ("Hall 111 — fault (coast)",    (True,  True,  True )),
        ],
        columns=[
            ("HA",     lambda c, a, k: '1' if a[0] else '0'),
            ("HB",     lambda c, a, k: '1' if a[1] else '0'),
            ("HC",     lambda c, a, k: '1' if a[2] else '0'),
            ("sector", lambda c, a, k: c.active_sector),
            ("drive",  lambda c, a, k: _gate_summary(c.gates)),
        ],
    )
    print()
    print("=" * 80)
    print("Composed BLDCSystem — walk the rotor through one electrical revolution:")
    print("=" * 80)
    run_scenarios(
        BLDCSystem(),
        scenarios=[
            (f"rotor = {angle:>3d}°", (float(angle),))
            for angle in (0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330)
        ],
        columns=[
            ("angle°", lambda c, a, k: f"{a[0]:>4.0f}"),
            ("hall",   lambda c, a, k: ''.join('1' if b else '0'
                                                for b in c.motor.hall_pattern)),
            ("sector", lambda c, a, k: c.controller.active_sector),
            ("drive",  lambda c, a, k: _gate_summary(c.gates)),
        ],
    )


if __name__ == '__main__':
    _main()
