"""Doorbell protector — composite-circuit demo.

Faithful recreation of the project at
https://www.electronicsforu.com/electronics-projects/prevent-multiple-doorbell-rings
— a two-LM555 add-on that rings the doorbell once for ~5 s and then
locks itself out for ~50 s, so a visitor mashing the button only rings
the bell once per minute.

Bill of materials:
    U1  NE555_5sMonostable   ~5 s bell-pulse timer (R3=1MΩ, C2=4.7µF)
    U2  NE555_50sMonostable  ~50 s lock-out timer  (R6=1MΩ, C5=47µF)
    Q1  BC548                relay-coil driver (T1)
    Q2  Q2N3904              IC1-reset gate    (T2)
    D1  D1N4007              relay-coil flyback diode
    D2  red LED              bell-ringing status indicator
    K1  Relay_SPDT           drives the doorbell through its NO contact
    R1, R4  1 kΩ             base resistors
    R2, R3, R6  1 MΩ         timing & pull-up
    R5  10 kΩ                IC1 reset-line pull-up (kept HIGH at rest)
    R7  4.7 kΩ
    R8  47 kΩ
    C1, C3, C4  100 nF       trigger coupling & CTRL decoupling
    C2  4.7 µF               IC1 timing capacitor
    C5  47 µF                IC2 timing capacitor
    Battery: 9 V – 12 V supply.

Composite call surface:
    DoorbellProtector(button_pressed, advance_ms) -> bool   # bell-ringing

`button_pressed` is the push-switch state (True = pressed, False =
released).  `advance_ms` is the simulated time elapsed since the
previous call; the composite uses it to step both monostable cells
forward.  The return is the relay's NO-throw state — True while the
relay is energised and the bell is sounding.

Simulation notes
----------------
RC-driven 555 timing isn't solvable in a voltage-only steady-state
graph; two `Monostable` cells embedded in NE555 subclasses (same
pattern as the thermometer's `Uno_ThermometerSketch`) model the LM555
monostable behaviour and expose `_remaining_ms` as a Python-level
escape hatch that the composite decrements each call.  T2 inverts
IC2.OUT to drive IC1.RESET; in the simulator we propagate that
inversion through a separate `Inverter` cell wired in parallel with
the physical Q2N3904, which sits in the BOM and on the wirelist but
contributes nothing under graph evaluation.

The IC1.OUT → IC2.TRIG and IC2.OUT → inverter → IC1.RESET paths form
a feedback cycle that the topological sort cannot break, so the
warning at construction is expected.  Factor-node declaration order is
laid out so that the fallback evaluation order produces correct
dataflow within a single evaluate pass.
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
    Chip, Circuit, Direction, Pin, PinId,
    GroundDomain, ELECTRICAL, RefdesNumber, validate_refdes,
    wire,
    BC548, Q2N3904, D1N4007, LED, Rail, Resistor, Capacitor, Relay_SPDT,
    NE555,
    run_scenarios,
)
from framework.port_map import PortMap
from components.chips.concepts.inverter   import Inverter
from components.chips.concepts.monostable import Monostable


# ---------------------------------------------------------------------------
# NE555 wired as a monostable with a fixed pulse duration.
# ---------------------------------------------------------------------------

class NE555_Monostable(NE555):
    """NE555 with an internal Monostable cell of fixed duration.

    Same 8-pin DIP as plain NE555, same datasheet pinout — the only
    differences are: TRIG and RESET feed the cell's trig/reset inputs
    via the package pins, and OUT is driven by the cell's out port.

    Like CD4017's `_PIN_TABLE` reordering trick, this constructor
    bypasses `Chip.__init__` so the cell evaluates *between* the IN
    pins (which copy external→internal first) and the OUT pin (which
    must copy internal→external afterwards) under the topological
    sort's cycle-fallback ordering.
    """

    __slots__ = ('_monostable',)

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        duration_ms: float,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._monostable = Monostable(duration_ms=duration_ms, domain=domain)

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        # External TRIG / RESET drive the cell's inputs; the cell's
        # OUT drives the OUT-pin internal face (which Pin.evaluate
        # then copies to external).
        wire(by_name['TRIG'].internal,  self._monostable.ports['trig'])
        wire(by_name['RESET'].internal, self._monostable.ports['reset'])
        wire(self._monostable.ports['out'], by_name['OUT'].internal)

        # Lay out factor_nodes so IN pins are first (so external→internal
        # propagation happens before the cell reads), then the cell,
        # then OUT pins (so internal→external happens after the cell
        # drives), then everything else.  Mirrors the trick CD4017 uses
        # for its Q-output pins.
        in_pin_names  = {'TRIG', 'RESET', 'THRES'}
        out_pin_names = {'OUT', 'DISCH'}
        in_pins    = [p for p in pins if p.id.name in in_pin_names]
        out_pins   = [p for p in pins if p.id.name in out_pin_names]
        other_pins = [p for p in pins
                      if p.id.name not in in_pin_names
                      and p.id.name not in out_pin_names]

        self._ports_by_number = {pin.id.number: pin.external for pin in pins}
        self._port_map = PortMap(self._ports_by_number)
        Circuit.__init__(
            self,
            factor_nodes=in_pins + [self._monostable] + out_pins + other_pins,
            ports=dict(self._port_map.items()),
        )

    @property
    def monostable(self) -> Monostable:
        return self._monostable

    @property
    def duration_ms(self) -> float:
        return self._monostable.duration_ms

    @property
    def remaining_ms(self) -> float:
        return self._monostable.remaining_ms

    @property
    def running(self) -> bool:
        return self._monostable.running

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, trig: bool | None = True, reset: bool | None = True) -> bool:
        """Standalone-test interface — drive TRIG / RESET, evaluate, return OUT.
        Refuses if any package pin is wired into a parent circuit."""
        self._assert_no_inputs_wired()
        self._ports['TRIG'].drive(trig)
        self._ports['RESET'].drive(reset)
        self.evaluate()
        return bool(self._ports['OUT'].value)

    def __repr__(self) -> str:
        return (f"NE555_Monostable(duration_ms={self.duration_ms!r}, "
                f"refdes={self.refdes!r}, remaining_ms={self.remaining_ms!r})")


# ---------------------------------------------------------------------------
# Composite circuit.
# ---------------------------------------------------------------------------

class DoorbellProtector(Circuit):
    """Two-LM555 doorbell protector.

    External-port surface:
        button  Digital IN — push-to-make switch.  Drive HIGH while
                pressed, LOW (or release) otherwise.  The composite
                inverts to the LM555 active-LOW trigger convention.

    Composite call:
        protector(button_pressed: bool, advance_ms: float = 0) -> bool

    Returns whether the relay's NO throw is currently closed (= the
    doorbell is sounding).  Auto-collect Circuit composite: parts are
    listed in dataflow order so the cycle-fallback evaluation runs
    sources before consumers in a single pass.
    """

    BELL_DURATION_MS:    float = 5_000.0
    LOCKOUT_DURATION_MS: float = 50_000.0

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # Rails go first so they evaluate before anything that reads
        # them.  The supply rail also drives IC2.RESET (always HIGH).
        self.gnd = Rail(False)
        self.vcc = Rail(True)

        # The two LM555s.  IC1 is the bell-duration timer; IC2 is the
        # lock-out timer.  IC1 must declare before IC2 so IC1.OUT
        # updates before IC2 reads it (falling edge → lock-out trigger).
        self.ic1 = NE555_Monostable(self.BELL_DURATION_MS,    refdes_number=1)
        self.ic2 = NE555_Monostable(self.LOCKOUT_DURATION_MS, refdes_number=2)

        # Inverter cell that propagates the IC2.OUT → IC1.RESET
        # inversion; the physical Q2N3904 (T2) is opaque under graph
        # evaluation, so this cell is what actually drives RESET LOW
        # during the lock-out window.  Must declare after IC2 (reads
        # IC2.OUT) and before IC1 wouldn't help — the cycle makes
        # IC1's RESET lag one evaluate, which is fine here.
        self.t2_inverter = Inverter()

        # Transistors (BOM-only — opaque under graph evaluation but
        # listed on the wirelist with conventional connections).
        self.t1 = BC548   (refdes_number=1)   # bell-relay driver
        self.t2 = Q2N3904 (refdes_number=2)   # IC1 reset gate

        # Diode and status LED.
        self.d1   = D1N4007(refdes_number=1)              # coil flyback
        self.led1 = LED('red', refdes_number=2)           # bell-ringing indicator

        # Resistors — values per the project BOM.
        self.r1 = Resistor(1_000,     refdes_number=1)   # T1 base resistor
        self.r2 = Resistor(1_000_000, refdes_number=2)   # IC1 TRIG pull-up
        self.r3 = Resistor(1_000_000, refdes_number=3)   # IC1 timing R
        self.r4 = Resistor(1_000,     refdes_number=4)   # T2 base resistor
        self.r5 = Resistor(10_000,    refdes_number=5)   # IC1 RESET pull-up
        self.r6 = Resistor(1_000_000, refdes_number=6)   # IC2 timing R
        self.r7 = Resistor(4_700,     refdes_number=7)
        self.r8 = Resistor(47_000,    refdes_number=8)

        # Capacitors.
        self.c1 = Capacitor(100e-9, refdes_number=1)     # IC1 CTRL decoupling
        self.c2 = Capacitor(4.7e-6, refdes_number=2)     # IC1 timing capacitor
        self.c3 = Capacitor(100e-9, refdes_number=3)     # S1 trigger coupling
        self.c4 = Capacitor(100e-9, refdes_number=4)     # IC1→IC2 trigger coupling
        self.c5 = Capacitor(47e-6,  refdes_number=5)     # IC2 timing capacitor

        # Relay — the bell is wired through its NO contact.
        self.relay = Relay_SPDT(refdes_number=1)

        # --------------------------------------------------------------
        # Signal-bearing wires
        # --------------------------------------------------------------
        # IC1.OUT carries the bell-active signal: drives the relay
        # coil (high side, behavioural shortcut), triggers IC2 on its
        # falling edge, lights the status LED, and shows up on T1.base
        # / R1 for BOM fidelity (the Q-driven coil-low side stays
        # opaque under graph evaluation).
        wire(self.ic1.OUT,
             self.ic2.TRIG,
             self.r1.t1, self.r1.t2,          # 0-Ω BOM passthrough
             self.t1.b,
             self.relay.coil_plus,
             self.c4.t1, self.c4.t2,          # 0-Ω coupling cap (BOM)
             self.led1.anode)

        # T1's collector / flyback diode / coil-low side stays
        # un-netted: in real hardware they're tied together but
        # nothing in the model drives that net, and ERC flags any
        # multi-port net without a driver as floating.  Each part is
        # still in the BOM via auto-collect; the relay's coil_minus
        # is read as None → 0 V, which is exactly what we want for
        # the differential calculation against coil_plus.

        # VCC consumers — flyback cathode and IC2 reset.
        wire(self.vcc.out, self.d1.cathode, self.ic2.RESET)

        # IC2.OUT drives T2.base (BOM) and the behavioural inverter.
        wire(self.ic2.OUT,
             self.r4.t1, self.r4.t2,          # 0-Ω BOM passthrough
             self.t2.b,
             self.t2_inverter.a)

        # Inverter output → IC1.RESET (via R5 pull-up & T2 collector
        # in the BOM).  When IC2 is idle, the inverter drives RESET
        # HIGH; while IC2 is running, RESET is pulled LOW and IC1 is
        # held in reset.
        wire(self.t2_inverter.y,
             self.r5.t1, self.r5.t2,          # 0-Ω BOM passthrough
             self.t2.c,
             self.ic1.RESET)

        # GND consumers.
        wire(self.gnd.out,
             self.led1.cathode,
             self.t1.e,
             self.t2.e)

        super().__init__(
            ports={
                # `button` re-exports IC1.TRIG; the composite's
                # __call__ inverts the user's `button_pressed`
                # (active HIGH) into the LM555's active-LOW trigger.
                'button': self.ic1.TRIG,
            },
        )

    # ------------------------------------------------------------------
    # Read accessors
    # ------------------------------------------------------------------

    @property
    def bell_ringing(self) -> bool:
        """True iff the relay's coil is energised (NO throw closed)."""
        return self.relay.energised

    @property
    def locked_out(self) -> bool:
        """True iff the IC2 lock-out timer is currently running."""
        return self.ic2.running

    @property
    def bell_remaining_ms(self) -> float:
        return self.ic1.monostable.remaining_ms

    @property
    def lockout_remaining_ms(self) -> float:
        return self.ic2.monostable.remaining_ms

    # ------------------------------------------------------------------
    # Drive interface
    # ------------------------------------------------------------------

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, button_pressed: bool, advance_ms: float = 0.0) -> bool:
        """Advance `advance_ms` of simulated time and report bell state.

        The push switch is sampled as the boolean `button_pressed`:
        the composite drives IC1.TRIG to its inverse (the LM555's
        active-LOW trigger).  Transitions in `button_pressed` between
        consecutive calls are what register as trigger edges on the
        underlying Monostable cell — call with True once to model a
        press, then False to release.
        """
        # 1. Step time on both monostable cells.  Doing this first
        # means that when their evaluate() runs, the remaining_ms
        # reflects the elapsed window; an advance large enough to
        # exhaust IC1.OUT lets IC2 see the falling edge in the same
        # pass.
        elapsed = float(advance_ms)
        self.ic1.monostable._remaining_ms = max(
            0.0, self.ic1.monostable._remaining_ms - elapsed)
        self.ic2.monostable._remaining_ms = max(
            0.0, self.ic2.monostable._remaining_ms - elapsed)

        # 2. Drive the trigger pin: LM555 TRIG is active LOW, so a
        # pressed push-button corresponds to a LOW level on the pin.
        self._ports['button'].drive(not button_pressed)

        # 3. Propagate.
        self.evaluate()
        return self.bell_ringing

    def __repr__(self) -> str:
        return (f"DoorbellProtector(bell_ringing={self.bell_ringing}, "
                f"locked_out={self.locked_out})")


# ---------------------------------------------------------------------------
# Scenario walk
# ---------------------------------------------------------------------------

def _main() -> None:
    """Demonstrate the protector across a press-during-bell, then a
    press-during-lock-out, then a press after the lock-out clears."""
    run_scenarios(
        DoorbellProtector(),
        scenarios=[
            # Settle initial state with the button released.
            ("idle (button released)",              (False, 0.0)),
            # First press triggers the 5 s bell pulse.
            ("press the button",                    (True,  10.0)),
            # 2 s in: bell still ringing.
            ("2 s later — bell still ringing",      (False, 2_000.0)),
            # Press again 1 s in: too soon, IC1 already running.
            ("press during bell (ignored)",         (True,  10.0)),
            ("release",                             (False, 10.0)),
            # Run out the rest of the 5 s bell pulse — IC2 fires when
            # IC1.OUT falls.
            ("5 s mark — bell ends, lock-out begins", (False, 3_000.0)),
            # Press during the 50 s lock-out: IC1 reset held LOW, no bell.
            ("press during lock-out (1 s in)",      (True,  1_000.0)),
            ("release",                             (False, 10.0)),
            ("press again at 25 s into lock-out",   (True,  24_000.0)),
            ("release",                             (False, 10.0)),
            # Run out the lock-out plus a small margin so the inverter
            # propagates the new RESET HIGH.
            ("end of lock-out",                     (False, 26_000.0)),
            ("settle inverter / RESET update",      (False, 10.0)),
            # Now a press should re-trigger the bell.
            ("press after lock-out clears",         (True,  10.0)),
            ("release",                             (False, 10.0)),
        ],
        columns=[
            ("btn",      lambda c, a, k: 'on' if a[0] else 'off'),
            ("dt_ms",    lambda c, a, k: f"{a[1]:>7.0f}"),
            ("bell",     lambda c, a, k: 'RING' if c.bell_ringing else '—'),
            ("locked",   lambda c, a, k: 'YES'  if c.locked_out   else 'no'),
            ("bell_ms",  lambda c, a, k: f"{c.bell_remaining_ms:>6.0f}"),
            ("lock_ms",  lambda c, a, k: f"{c.lockout_remaining_ms:>6.0f}"),
        ],
    )


if __name__ == '__main__':
    _main()
