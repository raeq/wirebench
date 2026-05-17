"""Internal helpers for chip-class construction.

Not registered or part of the public API; just shared utilities the
chip classes pull in to avoid repeating the same boilerplate.
"""
from __future__ import annotations

from framework.part import Part
from framework.ground import GroundDomain
from framework.pin import Pin
from framework.port import Direction
from framework.signals import Digital
from framework.wire import wire

from .idle_driver import IdleDriver


def wire_idle_drivers(
    pins: list[Pin],
    domain: GroundDomain,
) -> list[Part]:
    """Attach an `IdleDriver` to every OUT-direction pin in `pins`.

    For chips whose actual behaviour is too complex to model
    behaviourally at the framework's voltage-only level (specialty
    ICs, protocol-bus devices, internal-state-machine parts), this
    helper produces the bare minimum of cells needed to satisfy the
    "every OUT pin must be driven" invariant enforced in
    `framework.chip.Chip.__init__`.

    Idle values follow a uniform convention: Digital outputs idle
    LOW (False); Analog outputs idle at 0.0 V.  Demos that need
    specific output values can post-process the chip's pin values
    after construction.

    Returns the list of `IdleDriver` cells in pin order — pass it
    to `super().__init__(pins=pins, cells=…)`.
    """
    drivers: list[Part] = []
    for pin in pins:
        if pin.direction is not Direction.OUT:
            continue
        signal_type = pin.external.signal_type
        idle_value: object
        if isinstance(signal_type, type) and issubclass(signal_type, Digital):
            idle_value = False
        else:
            idle_value = 0.0
        drv = IdleDriver(signal_type, idle_value=idle_value, domain=domain)
        wire(drv.ports['out'], pin.internal)
        drivers.append(drv)
    return drivers
