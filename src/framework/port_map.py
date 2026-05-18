"""Name-keyed view over a Chip's package pins.

A chip's canonical lookup is by datasheet pin number — that's a fact
about the physical part (pin 14 of a DIP-14 is the same hole on the
silkscreen regardless of what the signal is called).  Name-keyed
access is a convenience for the common case where pin names are
unique on the chip.

When multiple pins share a canonical name (an MCU with 5 VCC pins,
say), name lookup must not silently lose information.  PortMap
resolves this by giving each duplicate an ordinal suffix —
`VCC_1`, `VCC_2`, ... — assigned by ascending pin number, while
`chip.ports['VCC']` raises a clear error pointing at the
disambiguated forms and at `chip.ports_by_number`.

Iteration yields every pin exactly once.  Unique names appear
verbatim; duplicates appear with their `_<ordinal>` suffix.  Ordering
is by pin number, ascending — deterministic for exporters.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Iterator

from framework.errors import AmbiguousPinNameError, PartConfigurationError
from framework.port import Port


class PortMap(Mapping[str, Port]):
    """Mapping[str, Port] backed by a dict[int, Port].  Frozen after
    construction; mutation is not supported.

    Keys reflect the disambiguation rule:
      - canonical name when the chip has exactly one pin with that name
      - `<name>_<ordinal>` (1-indexed, ascending by pin number) when
        the chip has two or more pins sharing the canonical name
    """

    __slots__ = ('_by_number', '_disambiguated', '_canonical_to_pins')

    def __init__(self, by_number: dict[int, Port]) -> None:
        # Pin numbers must be unique (PinId invariant), and iteration
        # is sorted by pin number so the ordinal mapping is stable.
        self._by_number: dict[int, Port] = dict(by_number)
        # Map canonical name → sorted list of pin numbers carrying it.
        canonical: dict[str, list[int]] = {}
        for n in sorted(self._by_number):
            canonical.setdefault(self._by_number[n].name, []).append(n)
        self._canonical_to_pins = canonical
        # Build the disambiguated dict (the public name-keyed view).
        # Collision case: a chip with a unique pin named 'DIG_1' AND a
        # second pin set named 'DIG' that disambiguates to the same
        # 'DIG_1' key.  The two pins are semantically distinct but the
        # name-keyed slot is single-valued — silently overwriting one
        # would lose access to a real pin via the name-keyed view.
        # Refuse the construction so the chip class has to rename one
        # of the two.
        self._disambiguated: dict[str, Port] = {}
        for n in sorted(self._by_number):
            port = self._by_number[n]
            siblings = canonical[port.name]
            if len(siblings) == 1:
                key = port.name
            else:
                ordinal = siblings.index(n) + 1
                key = f'{port.name}_{ordinal}'
            if key in self._disambiguated:
                other_pin = next(
                    pn for pn, p in self._by_number.items()
                    if p is self._disambiguated[key]
                )
                raise PartConfigurationError(
                    f"PortMap key collision: pin {n} ({port.name!r}) "
                    f"disambiguates to {key!r}, which is already claimed "
                    f"by pin {other_pin}.  Rename one of the two so the "
                    f"name-keyed view has a unique slot per pin."
                )
            self._disambiguated[key] = port

    # ----- Mapping protocol ------------------------------------------

    def __getitem__(self, key: str) -> Port:
        if key in self._disambiguated:
            return self._disambiguated[key]
        # Canonical-name lookup on a duplicated name: raise with the
        # list of disambiguated alternatives.
        pins = self._canonical_to_pins.get(key)
        if pins is not None and len(pins) > 1:
            alternatives = ', '.join(
                f"{key}_{i+1} (pin {n})" for i, n in enumerate(pins)
            )
            raise AmbiguousPinNameError(
                f"Ambiguous pin name {key!r} — disambiguated names: "
                f"{alternatives}. Use one of these or look up by "
                f"number via ports_by_number[n]."
            )
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._disambiguated)

    def __len__(self) -> int:
        return len(self._disambiguated)

    def __contains__(self, key: object) -> bool:
        # True for both disambiguated keys and the canonical name of
        # any duplicated set — lets `'VCC' in chip.ports` succeed for
        # introspection even though `chip.ports['VCC']` would raise.
        return key in self._disambiguated or key in self._canonical_to_pins
