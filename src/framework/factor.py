from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, ClassVar

from framework.errors import WiredChipCallError
from framework.port import Direction, Port


# Footprint-string prefixes that mark a part as through-hole.  The
# `FOOTPRINT` class attribute conventionally follows KiCad library
# naming (`Package_DIP:DIP-14_W7.62mm`, `Resistor_THT:R_Axial_DIN0207`,
# …); we classify by the leading library segment.
_THT_FOOTPRINT_MARKERS = (
    'Package_DIP:',
    'Package_TO_SOT_THT:',
    'Connector_PinHeader_2.54mm:',
    'Connector_PinHeader_1.27mm:',
    'TerminalBlock:',            # Phoenix-style screw terminals are THT
    'Connector_IDC:',            # 2.54 mm IDC pin headers are THT on board side
    'Capacitor_THT:',
    'Resistor_THT:',
    'LED_THT:',
    'Diode_THT:',
    'Inductor_THT:',
    'Crystal:Crystal_HC49',
    'Connector_BarrelJack:',     # all DC barrel jacks are THT
    'Battery:',                  # battery holders are THT
    'Display_7Segment:',         # 7-segment displays are DIP-style THT
    'Relay_THT:',                # PCB-mount through-hole relays
)

# Footprint-string prefixes that mark a part as surface-mount.
_SMD_FOOTPRINT_MARKERS = (
    'Package_SO:', 'Package_SOIC:', 'Package_QFN:', 'Package_QFP:',
    'Package_BGA:', 'Package_LGA:', 'Package_TO_SOT_SMD:',
    'Package_DFN_QFN:', 'Package_SON:',
    'Resistor_SMD:', 'Capacitor_SMD:', 'LED_SMD:', 'Diode_SMD:',
    'Inductor_SMD:',
    'Connector_USB:', 'Connector_Audio:',
    'Connector_Card:',           # MicroSD / SD slots are SMD
    'Connector_HDMI:',
    'Connector_Video:',          # HDMI receptacles use Connector_Video footprints
    'Connector_RJ:',
    'RF_Module:',                # ESP / WROOM modules are SMD castellated
    'Sensor_Motion:',            # IMU sensor packages (MPU6050 QFN)
)


def _footprint_is_through_hole(footprint: str | None) -> bool:
    if footprint is None:
        return False
    return any(footprint.startswith(m) for m in _THT_FOOTPRINT_MARKERS)


def _footprint_is_smd(footprint: str | None) -> bool:
    if footprint is None:
        return False
    return any(footprint.startswith(m) for m in _SMD_FOOTPRINT_MARKERS)


class FactorNode(metaclass=ABCMeta):
    """Base class for all circuit elements: components and composite circuits.

    A factor node expresses a constitutive relation over its ports. Leaf nodes
    are components (Resistor, LED, …). Composite nodes are circuits containing
    sub-components wired together.
    """

    __slots__ = ()

    # If True, this component is a conductor: the framework treats its
    # internal and external faces as one logical net for ERC, and
    # Circuit._validate walks through the component when counting drivers.
    # Used for chip pins (bonded wire from silicon to package) and
    # connector contacts (spring contact in housing). Default False.
    IS_CONDUCTOR: ClassVar[bool] = False

    # If True, this component is *transparent* to the parent's
    # topological sort and evaluation: the parent walks into its
    # sub-components and orders them individually rather than treating
    # this component as a single eval step.  Used for connectors (a
    # connector's pins go in independent directions and need pin-level
    # toposort granularity).  Chips remain opaque (False); their pins +
    # cells live within their own Circuit.evaluate.
    IS_TRANSPARENT: ClassVar[bool] = False

    # Default footprint string for downstream exporters (KiCad, BOM,
    # Yosys). None means "no footprint declared" — exporters that
    # require one error out, exporters that don't simply omit the
    # field. Subclasses override either as a ClassVar (fixed-geometry
    # parts) or via @property (parameterised families that compute
    # from instance state like pin_count/pitch).  Declared as a
    # property here (rather than `ClassVar[str | None] = None`) so
    # that mypy permits the @property override in parameterised
    # subclasses; a literal class-attribute override still works.
    @property
    def FOOTPRINT(self) -> str | None:
        return None

    # Pin numbers for passive terminals whose ports are not wrapped in
    # Pin instances. Maps port name -> datasheet pin number. Chips and
    # connectors carry numbers on each Pin.id; passives declare them
    # here. See framework.export.base.pin_number_of for the unified
    # lookup used by exporters.
    PIN_NUMBERS: ClassVar[dict[str, int]] = {}

    # Per-package layout metadata for the breadboard-assembly exporter.
    # Empty dict means "no physical layout declared" — the exporter
    # uses generic placement.  Concrete bread-board-compatible classes
    # override with one of the supported kinds: 'dip', 'axial_2lead',
    # 'radial_2lead_polarised', 'to92', 'to220', 'header_pins'.
    LAYOUT: ClassVar[dict[str, Any]] = {}

    # Per-class bench warnings the assembly-guide exporter emits in the
    # "Notes & Gotchas" section when this part appears in a design.
    # Empty tuple → no part-specific warnings.
    GOTCHAS: ClassVar[tuple[str, ...]] = ()

    # Per-class pre-install verification steps the assembly-guide
    # exporter emits in the "How to verify" section.  Bench-grade
    # multimeter checks that catch DOA parts before they go on the
    # breadboard.  Empty tuple → no specific check (typical for parts
    # that can't be meaningfully verified in isolation, e.g. most chips).
    VERIFY: ClassVar[tuple[str, ...]] = ()

    # -------------------------------------------------------------
    # Substrate-compatibility surface
    # -------------------------------------------------------------
    # Six read-only booleans describing where this part can physically
    # be mounted.  Defaults are computed from `FOOTPRINT` via a marker
    # lookup; per-class overrides are welcome when the footprint string
    # alone doesn't capture the physical reality of the part.

    @property
    def is_through_hole(self) -> bool:
        """The part has leads designed to pass through holes (DIP,
        axial, radial, TO-92, TO-220, 0.1" pin headers)."""
        return _footprint_is_through_hole(self.FOOTPRINT)

    @property
    def is_smd(self) -> bool:
        """The part is surface-mount (SOIC, QFN, QFP, BGA, SMD
        passives)."""
        return _footprint_is_smd(self.FOOTPRINT)

    @property
    def is_breadboard_compatible(self) -> bool:
        """True if this part can plug directly into a standard 830-pin
        breadboard.  Through-hole parts with 0.1" lead spacing qualify;
        SMD parts and exotic-pitch parts do not.  Parts with no
        FOOTPRINT (Rail, Ground) are vacuously compatible — they're
        not physical parts, so they don't block breadboard assembly."""
        if self.FOOTPRINT is None:
            return True
        return self.is_through_hole

    @property
    def is_perfboard_compatible(self) -> bool:
        """True if this part can be soldered onto standard 0.1"
        perfboard.  Currently equivalent to `is_breadboard_compatible`
        — same hole geometry."""
        return self.is_breadboard_compatible

    @property
    def is_pcb_compatible(self) -> bool:
        """True if this part can land on a custom PCB.  Both through-
        hole and SMD parts qualify; the only exclusion is parts that
        aren't placeable (Rail, Ground), which are vacuously True
        since a PCB doesn't need to do anything to accommodate them."""
        if self.FOOTPRINT is None:
            return True
        return self.is_through_hole or self.is_smd

    @property
    def is_dead_bug_compatible(self) -> bool:
        """True if this part can be wired point-to-point in dead-bug
        fashion (leads soldered directly to other leads or to floating
        pads, no PCB required).  Through-hole parts with accessible
        leads qualify; most SMD parts don't without rework adapters."""
        if self.FOOTPRINT is None:
            return True
        return self.is_through_hole

    def other_face(self, port: Port) -> Port:
        """Return the opposite face of this conductor, given one face.

        Only meaningful on IS_CONDUCTOR components (Pin).  The default
        raises — non-conductors have no notion of paired faces.
        """
        raise NotImplementedError(
            f"{type(self).__name__} is not a conductor; other_face() not defined"
        )

    @property
    @abstractmethod
    def ports(self) -> dict[str, Port]:
        ...

    @abstractmethod
    def evaluate(self) -> None:
        ...

    def _assert_no_inputs_wired(self) -> None:
        """Raise if any input or BIDIR port is connected to a node.

        Direct invocation of `__call__` on a wired node would silently
        overwrite the externally driven signal — refuse instead. Every
        leaf component and every chip uses this guard so the silent-
        overwrite hazard is mechanically prevented across the codebase.

        BIDIR ports are included because they may be written from
        __call__ (Resistor's __call__ does this today, but skips this
        guard deliberately because it doesn't actually touch ports).
        Any future BIDIR-driving __call__ inherits the protection.
        """
        wired = [n for n, p in self.ports.items()
                 if p.direction in (Direction.IN, Direction.BIDIR) and p.connected]
        if wired:
            raise WiredChipCallError(
                f"{type(self).__name__}.__call__ refused: port(s) wired "
                f"by an enclosing circuit ({', '.join(wired)}); drive via "
                f"the parent's evaluate() instead."
            )

    def __getattr__(self, name: str) -> Any:
        """Proxy port lookup as attribute access.

        `chip.PD3` resolves to `chip.ports['PD3']` when `PD3` is a port
        name and no real attribute by that name exists.  Lets wire()
        calls read as `wire(arduino.PD3, display.DIG_1)` instead of
        `wire(arduino.ports['PD3'], display.ports['DIG_1'])`.

        Only fires when normal attribute lookup misses, so slots,
        properties, methods, and class attributes are untouched.
        Private names (leading `_`) and `ports` itself short-circuit
        so that pickle, copy, and pydantic introspection don't trip
        the proxy and so that a missing `_ports` during __init__
        doesn't recurse.

        Return type is `Any` because the proxy is a fallback for any
        attribute the static type-checker can't see — including
        composite cells (`board.led`) and Python instance attributes
        set in `__init__` of subclasses that don't declare them in
        `__slots__`.  Annotating as `-> Port` would (incorrectly) tell
        mypy that *every* unknown attribute is a Port.
        """
        if name.startswith('_') or name == 'ports':
            raise AttributeError(name)
        try:
            ports = self.ports
        except Exception:
            raise AttributeError(name)
        try:
            return ports[name]
        except (KeyError, TypeError):
            raise AttributeError(name)
