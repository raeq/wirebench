from __future__ import annotations

from framework.connector import Connector
from framework.wire import wire


def mate(a: Connector, b: Connector) -> None:
    """Physically mate two connectors: wire each external pin of `a` to the
    same-position external pin of `b`.

    Mating is positional — pin i of `a` joins pin i of `b`, matching the
    physical reality where pin numbers stamped on the housings line up
    when the parts are pushed together.

    Validates three layers of compatibility:
      1. Class-level — `b` is exactly `type(a).MATES_WITH` (the parts are
         physical mates of each other, not unrelated families).
      2. Instance-level — `pin_count` and `pitch_mm` agree (a 6-pin
         JST PH cannot mate with a 5-pin JST PH; a 0.05" header cannot
         mate with a 0.1" header even if both have the same pin count).
      3. Per-pin — delegated to wire(): same ground domain, same signal
         type, no driver conflicts.

    Raises:
        TypeError  — class-level mismatch or `MATES_WITH` is None (a
                     user-facing receptacle has no in-model mate).
        ValueError — instance-level mismatch (pin count, pitch) or any
                     wire()-level error per pin pair.
    """
    mates_with = type(a).MATES_WITH
    if mates_with is None:
        raise TypeError(
            f"{type(a).__name__} has no in-model mate "
            f"(MATES_WITH is None — user-facing receptacle)"
        )
    if type(b) is not mates_with:
        raise TypeError(
            f"{type(a).__name__} mates with {mates_with.__name__}, "
            f"not {type(b).__name__}"
        )
    if a.pin_count != b.pin_count:
        raise ValueError(
            f"Pin count mismatch: {type(a).__name__} has {a.pin_count}, "
            f"{type(b).__name__} has {b.pin_count}"
        )
    if a.pitch_mm != b.pitch_mm:
        raise ValueError(
            f"Pitch mismatch: {type(a).__name__} is {a.pitch_mm} mm, "
            f"{type(b).__name__} is {b.pitch_mm} mm"
        )
    # len(a.pins) == a.pin_count by construction; this guard catches a
    # subclass that overrode _build_pinout incorrectly.
    if len(a.pins) != len(b.pins):
        raise ValueError(
            f"Pin count mismatch after pinout construction: "
            f"{type(a).__name__} produced {len(a.pins)}, "
            f"{type(b).__name__} produced {len(b.pins)}"
        )
    for pa, pb in zip(a.pins, b.pins):
        wire(pa.external, pb.external)
