"""Electronic dice — composite-circuit demo.

Faithful recreation of the project at
https://electronicsclub.info/p_dice.htm — a 555 + 4017 dice that
displays a random 1-to-6 reading on a seven-LED dice-dot pattern when
the player releases the push switch.

Bill of materials:
    U1  NE555           astable oscillator (~5 kHz clock)
    U2  CD4017          decade counter; the counter cell advances on
                        the rising edge of CLK while CE is LOW
    D1..D6  1N4148      signal diodes forming the wired-OR matrix
                        that combines counter outputs for LEDs A and C
    D7      LED         dice centre  (group A)
    D8, D9   LED        first diagonal pair (group B; LED B1 + B2)
    D10, D11 LED        second diagonal pair (group C; LED C1 + C2)
    D12, D13 LED        middle pair (group D; LED D1 + D2)
    R1      470 Ω       centre-LED current limiter
    R2..R4  330 Ω       pair-LED current limiters (one per pair)
    R5, R6  10 kΩ       555 timing resistors (R_A, R_B in astable)
    R7      10 kΩ       CE pull-up (button releases CE HIGH → inhibit)
    C1      0.01 µF     555 timing capacitor
    C2      0.1 µF      555 CTRL pin decoupling

Run directly to see a per-tick trace of the dice cycling through its
six faces and stopping when the button is released:

    python demos/dice.py

Dice display layout
-------------------
The 7-LED pattern, with each label keyed to the group it belongs to::

    B1 .  C1
    .  A  .
    C2 .  B2
    D1 .  D2

Group → counter mapping (the counter is wired so Q0..Q5 represent
rolls 2, 3, 4, 5, 6, 1 in that order — picking up the trick the
project page calls out, so the CO output naturally lights LEDs B for
all of rolls 2..6 with no diodes):

    Roll  active Q   A on?  B on?  C on?  D on?  pattern
     1    Q5         yes    no     no     no     centre only
     2    Q0         no     yes    no     no     B diagonal
     3    Q1         yes    yes    no     no     B diagonal + centre
     4    Q2         no     yes    yes    no     both diagonals
     5    Q3         yes    yes    yes    no     both diagonals + centre
     6    Q4         no     yes    yes    yes    both diagonals + middle

LED A is driven by D1 (Q1→A) + D2 (Q3→A) + D3 (Q5→A) wire-OR'd.
LED B is driven directly from CO (HIGH for counts 0..4 = rolls 2..6).
LED C is driven by D4 (Q2→C) + D5 (Q3→C) + D6 (Q4→C) wire-OR'd.
LED D is driven directly from Q4 (roll 6 only).
Q6 is fed back to RST so the count rolls over after six rolls.

Simulation notes
----------------
The 555's astable oscillation depends on RC time constants that a
voltage-only graph cannot solve, so U1 is a black-box BOM part: the
demo composite drives CLK directly through its `tick` input.  C1, C2
and R5..R7 are in the BOM and on the wirelist as 0-Ω / 0-F
pass-throughs (their evaluate methods are no-ops).  The wired-OR
matrix is propagated through `DiodeOR` cells in parallel with the six
physical 1N4148s, which appear in the BOM and on the wirelist but
are opaque under graph evaluation.
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
    Circuit, wire,
    NE555, CD4017, D1N4148,
    Capacitor, LED, Rail, Resistor,
    run_scenarios,
)
# DiodeOR is a chip-internal concept cell, not part of the consumer-
# facing surface.  Import via its full path to flag the boundary cross.
from components.chips.concepts.diode_or import DiodeOR


# Map from active CD4017 output to dice face value, encoding the
# "sequence starts at 2" trick the project uses to save diodes.
_Q_TO_ROLL: dict[int, int] = {
    0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 1,
}


class Dice(Circuit):
    """Push-button electronic dice on a single board.

    External-port surface:
        tick    Digital IN — clock toggle.  Drive HIGH then LOW (one
                rising edge) to advance the counter by one step.  In
                real hardware the 555 generates this at ~5 kHz; here
                the composite's `__call__` drives the edges directly.
        button  Digital IN — push-to-make switch state.  HIGH means
                pressed (CE LOW → counter enabled).  LOW means
                released (CE HIGH → counter frozen on its current
                value).
    """

    __slots__ = (
        '_ne555', '_cd4017',
        '_diodes', '_or_a', '_or_c',
        '_leds',
        '_r_a', '_r_b', '_r_c', '_r_d',
        '_r_555a', '_r_555b', '_r_pullup',
        '_c_timing', '_c_decouple',
        '_vcc', '_gnd',
    )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        ne555  = NE555(refdes_number=1)
        cd4017 = CD4017(refdes_number=2)

        # Six 1N4148s for the wired-OR matrix: D1..D3 → LED A,
        # D4..D6 → LED C.
        d1 = D1N4148(refdes_number=1)   # Q1 → A
        d2 = D1N4148(refdes_number=2)   # Q3 → A
        d3 = D1N4148(refdes_number=3)   # Q5 → A
        d4 = D1N4148(refdes_number=4)   # Q2 → C
        d5 = D1N4148(refdes_number=5)   # Q3 → C
        d6 = D1N4148(refdes_number=6)   # Q4 → C
        diodes = (d1, d2, d3, d4, d5, d6)

        # Seven LEDs — D7 (centre) plus three labelled pairs.
        led_a  = LED('red', refdes_number=7)   # centre
        led_b1 = LED('red', refdes_number=8)
        led_b2 = LED('red', refdes_number=9)
        led_c1 = LED('red', refdes_number=10)
        led_c2 = LED('red', refdes_number=11)
        led_d1 = LED('red', refdes_number=12)
        led_d2 = LED('red', refdes_number=13)
        leds = {
            'A':  led_a,
            'B1': led_b1, 'B2': led_b2,
            'C1': led_c1, 'C2': led_c2,
            'D1': led_d1, 'D2': led_d2,
        }

        # LED current limiters.  The lone centre LED has a slightly
        # higher value so its brightness matches the paired groups.
        r_a = Resistor(470, refdes_number=1)
        r_b = Resistor(330, refdes_number=2)
        r_c = Resistor(330, refdes_number=3)
        r_d = Resistor(330, refdes_number=4)

        # 555 astable timing resistors (R5, R6) and CE pull-up (R7).
        r_555a   = Resistor(10_000, refdes_number=5)
        r_555b   = Resistor(10_000, refdes_number=6)
        r_pullup = Resistor(10_000, refdes_number=7)

        # 555 timing cap (C1) and CTRL-pin decoupling cap (C2).
        c_timing   = Capacitor(0.01e-6, refdes_number=1)
        c_decouple = Capacitor(0.1e-6,  refdes_number=2)

        # Behavioural cells for the diode matrix.  The physical 1N4148s
        # sit on the same wires but are opaque; these cells are what
        # propagate the OR'd signal to the LED drivers.
        or_a = DiodeOR(input_names=('q1', 'q3', 'q5'))
        or_c = DiodeOR(input_names=('q2', 'q3', 'q4'))

        gnd = Rail(False)
        vcc = Rail(True)

        # --------------------------------------------------------------
        # Clock and reset chain
        # --------------------------------------------------------------
        # In real hardware NE555.OUT drives CD4017.CLK via R5/R6/C1's
        # astable timing network.  None of those parts is simulable in
        # a voltage-only graph, so we don't wire them: the dice
        # composite re-exports CD4017.CLK as `tick` and the demo
        # __call__ drives the rising/falling edges directly.  The 555,
        # R5, R6, C1 and C2 are still in the BOM, just off-graph.
        #
        # Q6 → RST: after the counter passes Q5 it reaches Q6, which
        # resets it asynchronously.  Six legal counts (Q0..Q5) remain.
        # This makes a feedback loop the topological sort cannot order
        # (the cycle warning at construction is expected); the
        # DecadeCounter cell settles the Q-to-RST feedback inside a
        # single evaluate() pass.
        wire(cd4017.Q6, cd4017.RST)

        # --------------------------------------------------------------
        # Counter outputs feeding the diode-OR matrix
        # --------------------------------------------------------------
        # Q1 → OR_A.q1 + D1 anode.
        wire(cd4017.Q1, or_a.q1, d1.anode)
        # Q2 → OR_C.q2 + D4 anode.
        wire(cd4017.Q2, or_c.q2, d4.anode)
        # Q3 splits to both OR matrices (D2 → A, D5 → C).
        wire(cd4017.Q3,
             or_a.q3, or_c.q3,
             d2.anode, d5.anode)
        # Q5 → OR_A.q5 + D3 anode.
        wire(cd4017.Q5, or_a.q5, d3.anode)

        # --------------------------------------------------------------
        # Direct counter-to-LED drives
        # --------------------------------------------------------------
        # Q4 lights the middle pair (LED D) directly *and* feeds OR_C
        # for roll 6.  R_D is wired as a 0-Ω pass-through (both
        # terminals on the same node) so the simulator can propagate
        # while keeping the resistor in the BOM and on the wirelist.
        wire(cd4017.Q4,
             or_c.q4, d6.anode,
             r_d.t1, r_d.t2,
             led_d1.anode, led_d2.anode)
        # CO drives the first diagonal pair (LED B) directly — its
        # active phase covers rolls 2..6, no diodes needed.
        wire(cd4017.CO,
             r_b.t1, r_b.t2,
             led_b1.anode, led_b2.anode)

        # --------------------------------------------------------------
        # Diode-OR outputs to LEDs A and C through current limiters
        # --------------------------------------------------------------
        wire(or_a.out,
             d1.cathode, d2.cathode, d3.cathode,
             r_a.t1, r_a.t2,
             led_a.anode)
        wire(or_c.out,
             d4.cathode, d5.cathode, d6.cathode,
             r_c.t1, r_c.t2,
             led_c1.anode, led_c2.anode)

        # --------------------------------------------------------------
        # LED cathodes to GND
        # --------------------------------------------------------------
        wire(gnd.out,
             led_a.cathode,
             led_b1.cathode, led_b2.cathode,
             led_c1.cathode, led_c2.cathode,
             led_d1.cathode, led_d2.cathode)

        # --------------------------------------------------------------
        # Pull-up R7 sits between VCC and CD4017.CE in the hardware.
        # We cannot make that wire active in the simulator: a 0-Ω
        # pass-through would let the Rail unconditionally re-drive CE
        # HIGH each evaluation, masking the externally-supplied
        # `button` signal.  R7 stays in the BOM with its terminals
        # unwired; the push switch is also off-graph and is
        # represented by the composite's `button` external port, which
        # drives CE directly.  Tie VCC to NE555.RESET (a Digital IN
        # pin) so the supply rail still has a real consumer in the
        # netlist — mirrors the hardware requirement that 555 RESET be
        # held HIGH for normal astable operation.
        wire(vcc.out, ne555.RESET)

        # Factor-node order matters: the Q6→RST feedback wire creates a
        # cycle that the topological sort cannot break, so it falls
        # back to declaration order.  Lay them out in dataflow order
        # (rails → 555 → counter → OR matrix → opaque parts → LEDs)
        # so that each consumer's evaluate runs after its sources have
        # driven their outputs in the same pass.
        super().__init__(
            factor_nodes=[
                vcc, gnd,
                ne555, cd4017,
                or_a, or_c,
                d1, d2, d3, d4, d5, d6,
                r_a, r_b, r_c, r_d, r_555a, r_555b, r_pullup,
                c_timing, c_decouple,
                led_a, led_b1, led_b2, led_c1, led_c2, led_d1, led_d2,
            ],
            ports={
                'tick':   cd4017.CLK,
                'button': cd4017.CE,
                'q':      cd4017.Q0,   # exposed for tracing
            },
        )

        self._ne555       = ne555
        self._cd4017      = cd4017
        self._diodes      = diodes
        self._or_a        = or_a
        self._or_c        = or_c
        self._leds        = leds
        self._r_a, self._r_b, self._r_c, self._r_d = r_a, r_b, r_c, r_d
        self._r_555a, self._r_555b = r_555a, r_555b
        self._r_pullup    = r_pullup
        self._c_timing    = c_timing
        self._c_decouple  = c_decouple
        self._vcc, self._gnd = vcc, gnd

    # ------------------------------------------------------------------
    # Public read accessors
    # ------------------------------------------------------------------

    @property
    def counter(self) -> CD4017:
        return self._cd4017

    @property
    def leds(self) -> dict[str, LED]:
        return self._leds

    @property
    def face(self) -> int | None:
        """Dice face currently shown, decoded from the active counter
        output.  Returns None before any tick has been applied (no
        single Q output drives HIGH).  The Q-to-roll mapping is the
        "starts at 2" sequence the project uses to save diodes."""
        count = self._cd4017.count
        return _Q_TO_ROLL.get(count)

    @property
    def lit_leds(self) -> tuple[str, ...]:
        """Names of LEDs currently lit, in canonical order."""
        order = ('A', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2')
        return tuple(name for name in order if self._leds[name].lit)

    # ------------------------------------------------------------------
    # Drive interface
    # ------------------------------------------------------------------

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, button_pressed: bool, ticks: int = 1) -> int | None:
        """Simulate `ticks` 555 clock cycles with the button in the
        given state, returning the dice face currently shown.

        Each tick toggles CLK LOW→HIGH→LOW so the counter sees exactly
        one rising edge per tick.  Pressing the button (CE LOW)
        enables counting; releasing it (CE HIGH) freezes the count on
        whatever it last reached, which is the randomising trick.
        """
        # CE is active LOW: pressed (True) → CE LOW, released → CE HIGH.
        ce_level = not button_pressed
        self._ports['button'].drive(ce_level)
        n = int(ticks)
        for _ in range(n):
            self._ports['tick'].drive(True)
            self.evaluate()
            self._ports['tick'].drive(False)
            self.evaluate()
        if n <= 0:
            # No clock edges this call — still settle outputs so the
            # caller sees the LEDs reflect the current count and
            # button state.
            self.evaluate()
        return self.face

    def render(self) -> str:
        """Return a small ASCII pip diagram of the current face."""
        lit = set(self.lit_leds)
        def dot(name: str) -> str:
            return '●' if name in lit else '·'
        return (
            f"{dot('B1')}   {dot('C1')}\n"
            f"{dot('D1')} {dot('A')} {dot('D2')}\n"
            f"{dot('C2')}   {dot('B2')}\n"
        )

    def __repr__(self) -> str:
        return f"Dice(face={self.face}, lit={self.lit_leds!r})"


def _main() -> None:
    """Walk through a few button-press scenarios and print the dice
    face and a trace of which LEDs are lit at each step."""
    dice = Dice()
    run_scenarios(
        dice,
        scenarios=[
            ("release button (initial)",            (False, 0)),
            ("press and roll 1 tick",               (True,  1)),
            ("keep pressed, roll 4 more",           (True,  4)),
            ("hold for one more tick",              (True,  1)),
            ("release — freeze",                    (False, 1)),
            ("button up, more ticks (no advance)",  (False, 5)),
            ("press again, roll 3",                 (True,  3)),
            ("release on roll",                     (False, 1)),
        ],
        columns=[
            ("btn",   lambda c, a, k: 'on' if a[0] else 'off'),
            ("ticks", lambda c, a, k: a[1]),
            ("count", lambda c, a, k: c.counter.count),
            ("face",  lambda c, a, k: c.face if c.face is not None else '?'),
            ("LEDs",  lambda c, a, k: ','.join(c.lit_leds)),
        ],
    )
    print()
    print("Final dice face:")
    print(dice.render())


if __name__ == '__main__':
    _main()
