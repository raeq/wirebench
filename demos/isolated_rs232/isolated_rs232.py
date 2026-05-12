"""Isolated RS-232 — composable Board demo with two GroundDomains.

Inspired by TI Designs reference TIDA-01230 (Isolated RS-232 With
Integrated Signal and Power): an ISOW7841 reinforced digital
isolator carries three forward channels and one reverse channel
between the controller-side rail and an iso-side rail that the
ISOW7841 itself generates; a TRS3122E full-duplex RS-232
transceiver on the iso side then level-shifts to the ±5 V line
format and connects to a DB-9 (modelled here as a 4-pin header).

This is the only demo in the library that exercises the framework's
`GroundDomain` plumbing across an actual barrier.  Every wire on the
logic side stays in the framework's default `ELECTRICAL` domain;
every wire on the iso side stays in a new `ISOLATED` domain.  The
two are joined exclusively through the `IsolatedChannel` cells
embedded inside the ISOW7841 chip — those cells have ports in
*different* domains, which is the only place in the framework where
that's legal.

Composable layout
-----------------
`IsolatedRS232Board` exposes two connectors:

    J1 (Header1xNFemale, 4-pin, ELECTRICAL) — controller-side
        J1.p1 = VCC1   (3.3 V or 5 V logic supply)
        J1.p2 = GND1
        J1.p3 = TXD    (logic level, host → line)
        J1.p4 = RXD    (logic level, line → host)

    J2 (Header1xNFemale, 4-pin, ISOLATED)   — RS-232 cable side
        J2.p1 = TX     (RS-232 line out)
        J2.p2 = RX     (RS-232 line in)
        J2.p3 = ISOGND
        J2.p4 = VISO   (the chip's regulated 5 V iso rail, exposed
                        for harnesses that want to power a passive
                        cable terminator off it)

Larger systems mate their host-side header into J1 and their RS-232
cable's DB-9 into J2.  `IsolatedRS232Link` at the bottom of this file
demonstrates the pattern: a `ControllerSourceBoard` plugs into J1
and an `RS232CableBoard` (a stand-in for the cable's chassis-side
DB-9) plugs into J2.

Run directly to see TX bytes propagate across the barrier and RX
bytes return:

    python demos/isolated_rs232.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from circuitry import (
    Board, Circuit, Direction, GroundDomain, ELECTRICAL, mate, wire,
    Capacitor, Rail,
    ISOW7841, TRS3122E,
    run_scenarios,
)
from components.connectors.headers import Header1xNFemale, Header1xNMale
from framework.registry import register


# Distinct ground domain for the isolated secondary side.  Created
# once at module import so every component on that side of the
# barrier ends up referencing the same `GroundDomain` instance
# (the framework's domain registry interns by name).
ISOLATED = GroundDomain('isolated_rs232')


# ---------------------------------------------------------------------------
# Composable isolated-RS-232 module
# ---------------------------------------------------------------------------

@register('IsolatedRS232Board')
class IsolatedRS232Board(Board):
    """Reinforced isolated RS-232 module.

    Two `GroundDomain`s coexist on the board: every part on the logic
    side (J1, ISOW7841's first eight pins, the input-side decoupling
    cap) lives in the framework's default `ELECTRICAL` domain; every
    part on the iso side (J2, ISOW7841's pins 9-16, the TRS3122E, its
    charge-pump capacitors, and the iso-side bulk cap) lives in
    `ISOLATED`.  `wire()` refuses to cross the boundary, which is
    exactly the rule a real isolated design needs to obey for
    creepage / clearance — only the four `IsolatedChannel` cells
    inside the ISOW7841 are allowed to bridge.

    Omits `__slots__` so `Board.__init__` auto-collects every part.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, *, refdes_number: int) -> None:
        # The two active ICs straddling / sitting-behind the barrier.
        self.u1 = ISOW7841(refdes_number=1,
                           logic_domain=ELECTRICAL,
                           iso_domain=ISOLATED)
        self.u2 = TRS3122E(domain=ISOLATED, refdes_number=2)

        # Bypass capacitors — one each side, plus the iso-side
        # charge-pump caps the TRS3122E datasheet calls for.  The
        # framework's Capacitor takes a `domain` argument so the
        # logic-side cap sits in ELECTRICAL and the iso-side caps
        # sit in ISOLATED.
        self.c_vcc1 = Capacitor(100e-9, domain=ELECTRICAL, refdes_number=1)
        self.c_viso = Capacitor(10e-6,  domain=ISOLATED,   refdes_number=2)
        self.c_vl   = Capacitor(100e-9, domain=ISOLATED,   refdes_number=3)
        self.c_cp1  = Capacitor(100e-9, domain=ISOLATED,   refdes_number=4)
        self.c_cp2  = Capacitor(100e-9, domain=ISOLATED,   refdes_number=5)
        self.c_vp   = Capacitor(100e-9, domain=ISOLATED,   refdes_number=6)
        self.c_vm   = Capacitor(100e-9, domain=ISOLATED,   refdes_number=7)

        # Connector surface — one each side.  Each connector must be
        # constructed with the appropriate domain so its pins land
        # in the right `GroundDomain`.
        self.j_logic = Header1xNFemale(
            pin_count=4, pitch_mm=2.54,
            domain=ELECTRICAL, refdes_number=1,
        )
        self.j_iso = Header1xNFemale(
            pin_count=4, pitch_mm=2.54,
            domain=ISOLATED, refdes_number=2,
        )

        # ------------------------------------------------------------
        # Wire the logic side.
        # ------------------------------------------------------------
        # J1.p3 (TXD logic in) -> ISOW7841 INA  (forward channel A)
        wire(self.j_logic.pins[2].internal, self.u1.ports['INA'])
        self.j_logic.pins[2]._effective_role = Direction.IN
        # ISOW7841 OUTD -> J1.p4 (RXD logic out) — reverse channel D
        wire(self.u1.ports['OUTD'], self.j_logic.pins[3].internal)
        self.j_logic.pins[3]._effective_role = Direction.OUT

        # ------------------------------------------------------------
        # Wire the iso side.
        # ------------------------------------------------------------
        # ISOW7841 OUTA (forward TX) -> TRS3122E TIN1 -> TOUT1 -> J2.p1
        wire(self.u1.ports['OUTA'], self.u2.ports['TIN1'])
        wire(self.u2.ports['TOUT1'], self.j_iso.pins[0].internal)
        self.j_iso.pins[0]._effective_role = Direction.OUT
        # J2.p2 (RX line in) -> TRS3122E RIN1 -> ROUT1 -> ISOW7841 IND
        wire(self.j_iso.pins[1].internal, self.u2.ports['RIN1'])
        self.j_iso.pins[1]._effective_role = Direction.IN
        wire(self.u2.ports['ROUT1'], self.u1.ports['IND'])

        super().__init__(
            name='Isolated RS-232',
            revision='A',
            refdes_number=refdes_number,
        )

    # ------------------------------------------------------------------
    # Composable read accessors
    # ------------------------------------------------------------------

    @property
    def line_tx(self) -> bool | None:
        """RS-232 line transmit (J2.p1) — what the host-side TX bit
        looks like after crossing the isolator and the level
        translator.  Surface read for tests and traces."""
        v: bool | None = self.j_iso.pins[0].external.value
        return v

    @property
    def host_rx(self) -> bool | None:
        """Logic-side receive (J1.p4) — the bit that came back across
        the isolator from whatever the cable side drove onto J2.p2."""
        v: bool | None = self.j_logic.pins[3].external.value
        return v

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        txd: bool | None = None,
        rin: bool | None = None,
    ) -> dict[str, bool | None]:
        """Standalone-test surface: drive the logic-side TXD and the
        iso-side RIN (RS-232 line in), evaluate, and read back the
        line TX and host RX.

        Drives the connector-pin *external* faces — both pins carry an
        `_effective_role = Direction.IN` override, which makes their
        Connector cells copy external → internal during evaluate.  An
        unmated receptacle would otherwise overwrite a drive on the
        internal face with the (None) external value."""
        self._assert_no_inputs_wired()
        self.j_logic.pins[2].external.drive(txd)
        self.j_iso  .pins[1].external.drive(rin)
        self.evaluate()
        return {
            'line_tx':  self.line_tx,
            'host_rx':  self.host_rx,
        }


# ---------------------------------------------------------------------------
# Example composition: host source board mated to the iso module, plus a
# cable stand-in mated to J2.
# ---------------------------------------------------------------------------

@register('ControllerSourceBoard')
class ControllerSourceBoard(Board):
    """Bench-style host plug — Header1xNMale with VCC1 + GND1 +
    TXD-driver + RXD-monitor; mates into J1.  All four pins live in
    `ELECTRICAL`."""

    def __init__(self, *, refdes_number: int) -> None:
        self.vcc = Rail(True,  domain=ELECTRICAL)
        self.gnd = Rail(False, domain=ELECTRICAL)
        self.plug = Header1xNMale(
            pin_count=4, pitch_mm=2.54,
            domain=ELECTRICAL, refdes_number=1,
        )

        # Plug pins: VCC on p1, GND on p2; p3 (TXD) and p4 (RXD) are
        # signal pins — left floating so the test scenario drives
        # them through the mated J1 ports.
        wire(self.vcc.ports['out'], self.plug.pins[0].internal)
        wire(self.gnd.ports['out'], self.plug.pins[1].internal)

        super().__init__(
            name='Controller Plug',
            revision='A',
            refdes_number=refdes_number,
        )


@register('RS232CableBoard')
class RS232CableBoard(Board):
    """RS-232 cable stand-in — Header1xNMale plug mating into J2 on
    the isolated side of the link.  All pins in `ISOLATED`.  The
    scenario drives 'RX' onto the cable's p2 (RIN line) so the
    isolator can carry it back to the host."""

    def __init__(self, *, refdes_number: int) -> None:
        self.gnd_iso = Rail(False, domain=ISOLATED)
        self.plug = Header1xNMale(
            pin_count=4, pitch_mm=2.54,
            domain=ISOLATED, refdes_number=2,
        )

        # The cable's GND (p3) shadows the iso-side ground rail.
        wire(self.gnd_iso.ports['out'], self.plug.pins[2].internal)

        super().__init__(
            name='RS-232 Cable',
            revision='A',
            refdes_number=refdes_number,
        )


class IsolatedRS232Link(Circuit):
    """End-to-end demonstration: controller plug → isolated module →
    cable plug, three boards mated together.  Walks bits in both
    directions across the barrier."""

    def __init__(self) -> None:
        self.host    = ControllerSourceBoard(refdes_number=1)
        self.iso_rs232 = IsolatedRS232Board   (refdes_number=2)
        self.cable   = RS232CableBoard      (refdes_number=3)

        mate(self.host .connectors[0], self.iso_rs232.connectors[0])
        mate(self.iso_rs232.connectors[1], self.cable.connectors[0])

        super().__init__()

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(
        self,
        txd: bool | None = None,
        rin: bool | None = None,
    ) -> dict[str, bool | None]:
        """Drive the host's TXD and the cable's RX-line pins via
        their mated plug pins' external faces.  The plug pins land on
        the same nodes as the IsolatedRS232Board's J1/J2 receptacle
        pins (which carry the `_effective_role = IN` overrides), so a
        drive on the plug's external face propagates through the mated
        receptacle into the chip side."""
        self.host .plug.pins[2].external.drive(txd)
        self.cable.plug.pins[1].external.drive(rin)
        self.evaluate()
        return {
            'line_tx': self.iso_rs232.line_tx,
            'host_rx': self.iso_rs232.host_rx,
        }


# ---------------------------------------------------------------------------
# Scenario walks
# ---------------------------------------------------------------------------

def _b(v: bool | float | None) -> str:
    if v is None:
        return '·'
    return '1' if bool(v) else '0'


def _main() -> None:
    print("=" * 80)
    print("Standalone IsolatedRS232Board — bits across the barrier:")
    print("=" * 80)
    run_scenarios(
        IsolatedRS232Board(refdes_number=1),
        scenarios=[
            ("idle (TX=0, RX=0)",      (False, False)),
            ("host TX=1, line RX=0",   (True,  False)),
            ("host TX=0, line RX=1",   (False, True )),
            ("host TX=1, line RX=1",   (True,  True )),
            ("both back to 0",         (False, False)),
        ],
        columns=[
            ("TXD",     lambda c, a, k: _b(a[0])),
            ("RIN",     lambda c, a, k: _b(a[1])),
            ("line_tx", lambda c, a, k: _b(c.line_tx)),
            ("host_rx", lambda c, a, k: _b(c.host_rx)),
        ],
    )
    print()
    print("=" * 80)
    print("Composed IsolatedRS232Link — host + iso module + cable:")
    print("=" * 80)
    run_scenarios(
        IsolatedRS232Link(),
        scenarios=[
            ("idle",                   (False, False)),
            ("host transmits a 1",     (True,  False)),
            ("cable replies 1",        (False, True )),
            ("both lines high",        (True,  True )),
            ("idle again",             (False, False)),
        ],
        columns=[
            ("TXD",     lambda c, a, k: _b(a[0])),
            ("RIN",     lambda c, a, k: _b(a[1])),
            ("line_tx", lambda c, a, k: _b(c.iso_rs232.line_tx)),
            ("host_rx", lambda c, a, k: _b(c.iso_rs232.host_rx)),
        ],
    )


if __name__ == '__main__':
    _main()
