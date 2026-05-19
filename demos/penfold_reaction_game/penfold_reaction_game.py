"""Project 22 — Reaction Game (after R. A. Penfold, BP107).

A test-your-reflexes game.  An NE555 astable runs at a few hundred
hertz; its output clocks a CD4017 decade counter whose ten outputs are
each connected to one indicator LED through a current-limit resistor.
The ten LEDs light in sequence faster than the eye can resolve.  A
push-button switch on the CD4017's CE (clock-enable) pin freezes the
counter the instant it is released — whichever LED is lit at that
moment shows the player's reaction time on an arbitrary 1..10 scale.

Substitutions from the BP107 original:

- Push-button switch S1 → no dedicated class in the wirebench
  catalogue; the framework exposes the counter's CE pin as the
  composite's `button_pressed` external port and the demo's __call__
  drives it directly.  The single 10 kΩ pull-up resistor that holds
  CE HIGH while S1 is open is in the BOM as a 0-Ω passthrough on the
  VCC rail — same idiom the `dice` demo uses for its CE pull-up.
- NE555 timing components: R1 47 kΩ, R2 4.7 kΩ, C1 100 nF → catalogue
  Resistor / Capacitor values.  The 555 itself is a black-box in
  wirebench's graph evaluation; the demo composite drives CLK
  directly through its `tick` port the same way `dice` does.
- LED current-limit resistors: ten × 470 Ω.  Penfold uses 1 kΩ for
  9 V supplies; 470 Ω is appropriate for a 5 V CMOS rail and keeps
  the wirebench-side simulation honest about the supply assumed.

Source: BP107 — 30 Solderless Breadboard Projects, Book 1
        R. A. Penfold
        Bernard Babani Publishing, October 1982
        ISBN 0 85934 082 1
        Pages 110–113 (text), Fig. 56 (schematic), Fig. 57 (layout).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Path setup so this file runs standalone from anywhere in the repo.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from wirebench import (  # noqa: E402
    Analog,
    Circuit, wire,
    CD4017, NE555,
    Capacitor, LED, Rail, Resistor,
    run_scenarios,
)


# Penfold's ten LEDs map one-to-one onto the CD4017's Q0..Q9.  The
# tuple gives the canonical readout order — Q0 lit means face '1',
# Q9 lit means face '10'.
_Q_NAMES: tuple[str, ...] = tuple(f'Q{i}' for i in range(10))


class ReactionGame(Circuit):
    """Push-button reaction-time game on a single board.

    External-port surface:
        tick             Digital IN — clock toggle.  Drive HIGH then
                         LOW (one rising edge) to advance the counter
                         by one step.  In real hardware the 555
                         astable generates this; here the composite's
                         `__call__` drives the edges directly.
        button_pressed   Digital IN — push-to-make switch state.
                         HIGH means *pressed* (CE LOW → counter runs);
                         LOW means *released* (CE HIGH → counter
                         frozen on its current value).  Penfold's
                         hardware S1 + R_pullup composes the same
                         signal at CE; wirebench refuses to add a
                         "switch part" whose only job is the same
                         thing the port boundary already expresses.

    Omits __slots__ so `Circuit.__init__` can auto-collect parts from
    `self.__dict__`.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        # ── Rails ───────────────────────────────────────────────────
        # Same Analog/Digital twin-rail pattern the `dice` demo uses:
        # logic-level Digital rails for the CE pull-up and CLK input;
        # Analog rails for the CD4017 / NE555 supply pins which are
        # declared Analog (Vdd, Vss, Vcc, Gnd).
        self.gnd   = Rail(False)
        self.vcc   = Rail(True)
        self.vcc_a = Rail(True,  signal_type=Analog)
        self.gnd_a = Rail(False, signal_type=Analog)

        # ── Active parts ────────────────────────────────────────────
        self.timer   = NE555(refdes_number=1)
        self.counter = CD4017(refdes_number=2)

        # ── Ten indicator LEDs ──────────────────────────────────────
        # One per CD4017 output.  Q0 → LED 1 .. Q9 → LED 10 in the
        # readout convention.  Wired through individual 470 Ω limit
        # resistors back to GND — the standard one-resistor-per-LED
        # layout.
        self.leds = tuple(
            LED('red', refdes_number=i + 1) for i in range(10)
        )
        self.r_leds = tuple(
            Resistor(470, refdes_number=i + 1) for i in range(10)
        )

        # ── NE555 timing network ────────────────────────────────────
        # R1, R2, C1 set the astable frequency.  The framework can't
        # solve the 555 timing graph, so these passives sit on a 0-Ω
        # passthrough on the VCC rail — exactly the dice-demo idiom.
        self.r1 = Resistor(47_000, refdes_number=11)     # R_A
        self.r2 = Resistor(4_700,  refdes_number=12)     # R_B
        self.c1 = Capacitor(100e-9, refdes_number=1)     # C1 = 100 nF
        # CTRL-pin decoupling cap on pin 5.
        self.c2 = Capacitor(10e-9,  refdes_number=2)     # C2 = 10 nF

        # ── CE pull-up ──────────────────────────────────────────────
        # 10 kΩ from VCC to CE.  Hardware: S1 closes pulls CE to GND
        # (counter runs).  S1 open lets the pull-up hold CE HIGH
        # (counter frozen).  R_pullup is in the BOM as a 0-Ω
        # passthrough on VCC; the externally-driven `button_pressed`
        # port carries the actual CE state.
        self.r_pullup = Resistor(10_000, refdes_number=13)

        # ── Wiring ──────────────────────────────────────────────────

        # Counter outputs → LEDs → current-limit R → GND.
        # The resistor sits between the LED's cathode and GND so the
        # framework's strict signal-typing sees a BIDIR-Analog wildcard
        # on the GND side and Digital all the way down from the
        # CD4017's Q pin to the LED's anode.  Same wiring shape the
        # `dice` and `digital_thermometer` demos use.
        for q_name, led, r in zip(_Q_NAMES, self.leds, self.r_leds):
            wire(self.counter.ports[q_name], led.anode)
            wire(led.cathode, r.t1)
            wire(r.t2, self.gnd.out)

        # CE pull-up R13 → off-graph passthrough on the VCC rail.  See
        # the dice demo for the rationale: the framework can't see
        # the open-circuit "pull-up" behaviour through a resistor, so
        # R_pullup is BOM-only and the actual CE level is driven
        # externally via the composite's `button_pressed` port.
        wire(self.vcc.out, self.timer.RESET,
             self.r_pullup.t1, self.r_pullup.t2,
             self.r1.t1, self.r1.t2,
             self.r2.t1, self.r2.t2,
             self.c1.t1, self.c1.t2,
             self.c2.t1, self.c2.t2)

        # Chip supply pins.  NE555 VCC/GND and CD4017 VDD/VSS all
        # declare Analog signal type; route via the Analog twin rails.
        wire(self.vcc_a.out, self.timer.VCC, self.counter.VDD)
        wire(self.gnd_a.out, self.timer.GND, self.counter.VSS)

        super().__init__(
            ports={
                'tick':           self.counter.CLK,
                'button_pressed': self.counter.CE,
            },
        )

    # ── Read accessors ──────────────────────────────────────────────

    @property
    def face(self) -> int | None:
        """1-based readout of the LED currently lit, or None if no LED
        is lit (counter at rest before any clock edge).
        """
        c = self.counter.count
        return c + 1 if 0 <= c <= 9 else None

    @property
    def lit_leds(self) -> tuple[int, ...]:
        """Indices (1..10) of currently-lit LEDs.  In normal operation
        exactly one LED is lit; the tuple is the canonical readout."""
        return tuple(i + 1 for i, led in enumerate(self.leds) if led.lit)

    # ── Drive interface ─────────────────────────────────────────────

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, button_pressed: bool, ticks: int = 1) -> int | None:
        """Simulate `ticks` 555 clock cycles with the button held in
        the given state.  Returns the 1..10 face currently shown
        (or None if no LED is lit).

        button_pressed semantics: True = pressed (CE LOW → counting),
        False = released (CE HIGH → frozen).  Same convention as the
        dice demo's CE pin (active-LOW).
        """
        ce_level = not button_pressed
        self._ports['button_pressed'].drive(ce_level)
        n = int(ticks)
        for _ in range(n):
            self._ports['tick'].drive(True)
            self.evaluate()
            self._ports['tick'].drive(False)
            self.evaluate()
        if n <= 0:
            self.evaluate()
        return self.face

    def __repr__(self) -> str:
        return f"ReactionGame(face={self.face}, lit={self.lit_leds!r})"


def _main() -> None:
    game = ReactionGame()
    run_scenarios(
        game,
        scenarios=[
            ("idle (button released)",      (False, 0)),
            ("press → 1 tick",              (True,  1)),
            ("hold → 4 more ticks",         (True,  4)),
            ("hold → another tick",         (True,  1)),
            ("release — freeze on face 6",  (False, 1)),
            ("button up, more ticks ignore", (False, 5)),
            ("press → 3 ticks",             (True,  3)),
            ("release — final freeze",      (False, 1)),
        ],
        columns=[
            ("btn",   lambda c, a, k: 'down' if a[0] else 'up'),
            ("ticks", lambda c, a, k: a[1]),
            ("count", lambda c, a, k: c.counter.count),
            ("face",  lambda c, a, k: c.face if c.face is not None else '?'),
            ("LEDs",  lambda c, a, k: ','.join(str(i) for i in c.lit_leds)),
        ],
    )


if __name__ == '__main__':
    _main()
