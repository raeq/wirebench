from typing import Annotated, ClassVar

from pydantic import Field, validate_call

from framework.part import Part
from framework.ground import GroundDomain, ELECTRICAL
from framework.port import Port, Direction
from framework.refdes import RefdesNumber, validate_refdes
from framework.registry import register
from framework.signals import Analog, Digital
from framework.units import Volts


@register('Relay_SPDT')
class Relay_SPDT(Part):
    """SPDT electromechanical relay — single coil drives one common
    contact between a normally-open and a normally-closed throw.

    Terminals
    ---------
        coil_plus, coil_minus    Analog BIDIR — coil drive.
        com                      BIDIR Analog conductor — common pole.
        no                       BIDIR Analog conductor — normally-open throw.
        nc                       BIDIR Analog conductor — normally-closed throw.

    Behaviour
    ---------
    The coil is energised when the voltage across it (coil_plus minus
    coil_minus, both read as Analog) exceeds `pickup_voltage`.  In a
    voltage-only steady-state graph the contacts can't dynamically
    merge nets, so signal does not propagate from `com` to `no` / `nc`.
    The switched state is reported instead via `closed_path`:

        'no'  — coil energised; the COM-to-NO path is conducting.
        'nc'  — coil de-energised; the COM-to-NC path is conducting.

    `evaluate()` reads the coil voltage and updates `closed_path`; the
    enclosing circuit can read it to decide what the contacts are
    driving (a doorbell, a relay-driven load, a status LED, etc.).
    Digital coil drives (HIGH / LOW) are accepted via the Analog
    wildcard: HIGH is treated as VDD-level (energised) and LOW as 0 V
    (de-energised).
    """

    __slots__ = ('_ports', '_refdes_number', '_pickup', '_closed_path')

    REFDES_PREFIX: ClassVar[str] = 'K'
    FOOTPRINT: ClassVar[str | None] = "Relay_THT:Relay_SPDT_Generic"

    VERIFY: ClassVar[tuple[str, ...]] = (
        "**Measure the coil resistance with your multimeter.** Put the "
        "meter in resistance (Ω) mode and probe the two coil pins. "
        "A small hobby relay's coil typically reads between 50 Ω and "
        "a few hundred ohms; 0 Ω means the coil is shorted (don't "
        "apply power), OL means it's burned open. The package usually "
        "labels which pins are the coil.",
        "**Check the resting contact state.** Switch the meter to "
        "continuity / beep mode. Probe Common (COM) to Normally-Closed "
        "(NC): the meter should beep — these contacts are connected "
        "when the coil is *not* energised. Probe Common to "
        "Normally-Open (NO): OL — these contacts are not connected at "
        "rest. Now briefly apply the rated coil voltage and you should "
        "hear an audible click as the relay actuates; the readings "
        "flip (COM-NC opens, COM-NO closes). No click means the coil "
        "is dead or you've applied the wrong voltage.",
    )

    GOTCHAS: ClassVar[tuple[str, ...]] = (
        "**Put a diode across the relay's coil — the band toward the "
        "+ supply side.** A 1N4001 or 1N4007 does the job. Without "
        "this 'flyback' diode, the moment you switch the coil off the "
        "collapsing magnetic field generates a +100 V spike that "
        "destroys whatever was driving the coil (your MCU pin, your "
        "transistor, or your MOSFET). This is the single most common "
        "relay-circuit mistake, and the failure happens silently — the "
        "driving transistor just stops working some time later.",
        "**The relay has two voltage ratings, and they're independent.** "
        "The coil voltage is what powers the electromagnet (5 V, 12 V, "
        "etc.); the contact voltage rating is what the relay can switch "
        "(often 250 V AC at several amps). A 5 V relay with 250 V "
        "contacts is normal. Don't tie the coil supply and the load "
        "supply together without checking both ratings — they're "
        "designed to be separate.",
        "**MCU pins can't power a relay coil directly — use a transistor "
        "in between.** Relay coils typically draw 50–100 mA continuously "
        "while energised; MCU pins are rated for about 20 mA absolute "
        "max. Drive the coil through an NPN transistor (or N-channel "
        "MOSFET) and switch *that* with the MCU. Also confirm your "
        "supply has the current to spare: a 9 V battery feeding a "
        "small regulator may already be near its limit when you add "
        "a relay.",
        "**Switching inductive AC loads (motors, transformer primaries) "
        "wears the contacts out fast.** Each switch-off arcs the "
        "contacts; over thousands of cycles the surfaces pit and "
        "eventually weld shut or fail to make contact. Add a 'snubber' "
        "(100 Ω resistor in series with a 100 nF capacitor, the pair "
        "wired across the contacts) to dissipate the arc energy. For "
        "fast or frequent switching, use a solid-state relay instead.",
    )
    PIN_NUMBERS: ClassVar[dict[str, int]] = {
        'coil_plus':  1,
        'coil_minus': 2,
        'com':        3,
        'no':         4,
        'nc':         5,
    }

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(
        self,
        domain: GroundDomain = ELECTRICAL,
        *,
        refdes_number: RefdesNumber,
        pickup_voltage: Annotated[float, Field(gt=0)] | Volts = Volts(1.0),
    ) -> None:
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._pickup: Volts = Volts(pickup_voltage)
        # Default rest position: coil de-energised, COM tied to NC.
        self._closed_path: str = 'nc'
        # Coil drive is Analog so that a Digital HIGH (canonicalised to
        # 1.0 by the framework) and a real 9 V supply both work.  All
        # five terminals are BIDIR / Analog so wire() accepts whatever
        # the surrounding circuit hangs on them.
        self._ports = {
            'coil_plus':  Port('coil_plus',  Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'coil_minus': Port('coil_minus', Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'com':        Port('com',        Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'no':         Port('no',         Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
            'nc':         Port('nc',         Direction.BIDIR, domain, mandatory=False, signal_type=Analog),
        }

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def refdes(self) -> str:
        return f"{self.REFDES_PREFIX}{self._refdes_number}"

    @property
    def refdes_number(self) -> int:
        return self._refdes_number

    @property
    def pickup_voltage(self) -> Volts:
        return self._pickup

    @property
    def closed_path(self) -> str:
        """Which throw the common pole is currently routed to.  'no'
        while the coil is energised, 'nc' when at rest."""
        return self._closed_path

    @property
    def energised(self) -> bool:
        """Convenience: True iff the coil is currently pulling the
        armature toward the NO throw."""
        return self._closed_path == 'no'

    def evaluate(self) -> None:
        plus  = self._ports['coil_plus'].value
        minus = self._ports['coil_minus'].value
        # Treat None as 0 V at rest — same convention Analog(None)
        # gives 0.0 — and accept Digital HIGH / LOW too.  Comparing
        # against `is True` first preserves the digital-drive case
        # without having to teach the relay about signal types.
        v_plus  = 1.0 if plus  is True else 0.0 if plus  is None or plus  is False else float(plus)
        v_minus = 1.0 if minus is True else 0.0 if minus is None or minus is False else float(minus)
        v_coil = v_plus - v_minus
        self._closed_path = 'no' if v_coil >= float(self._pickup) else 'nc'

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, coil_plus: float | bool | None = 0.0,
                 coil_minus: float | bool | None = 0.0) -> str:
        """Drive the coil terminals and return which throw is closed.
        Standalone-test surface; refuses when wired into a parent."""
        self._assert_no_inputs_wired()
        self._ports['coil_plus'].drive(coil_plus)
        self._ports['coil_minus'].drive(coil_minus)
        self.evaluate()
        return self._closed_path

    def __str__(self) -> str:
        return f"{self.refdes}: COM-{self._closed_path.upper()}"

    def __repr__(self) -> str:
        return (f"Relay_SPDT(refdes={self.refdes!r}, "
                f"pickup_voltage={float(self._pickup)!r}, "
                f"closed_path={self._closed_path!r})")
